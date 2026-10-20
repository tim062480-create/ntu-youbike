"""
台大課表下載程式
------------------------------------------------
從臺大課程網 (course.ntu.edu.tw) 下載整學期全校課程，
篩選出我們追蹤的 5 個區域，存成 courses_zones.csv。

用法：
  python fetch_courses.py            # 預設抓 115-1 學期
  python fetch_courses.py 115-2      # 下學期只要改學期代碼
  python fetch_courses.py 115-1 --from-json   # 不重新下載，用 data 裡的 JSON 重新產生 CSV

輸出檔案（都在 data 資料夾）：
  all_courses_115-1.json   全校原始資料（備份用）
  courses_zones.csv        5 區的課，一列＝一門課在某一天的一段連續上課時間
    上課週次：空白＝整學期每週上課；"1-8" 表示只有第 1～8 週（半學期課，例如微積分1）
    教室推測：1＝課程網沒排教室，用同一門課其他時段的教室推測區域

只用到 Python 內建套件。
"""

import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request

from youbike_collector import BUILDING_TO_ZONE, DATA_DIR

API = "https://course.ntu.edu.tw/api/v1/courses/search/quick?lang=zh_TW"
BATCH = 100            # 課程網一次最多給 100 筆
DELAY = 0.5            # 每次請求間隔幾秒，避免造成伺服器負擔

# 課程網的節次代號 → 我們的節次（X 代表第 10 節）
PERIOD_FIX = {"X": "10"}
ORDER = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "A", "B", "C", "D"]
WEEKDAYS = "一二三四五六日"


def make_query(semester):
    """課程網快速搜尋的查詢條件；keyword 留空＝全部課程"""
    return {
        "keyword": "", "time": [[], [], [], [], [], []], "timeStrictMatch": False,
        "isFullYear": None, "excludedKeywords": [], "enrollMethods": [],
        "isEnglishTaught": False, "isDistanceLearning": False, "hasChanged": False,
        "isAdditionalCourse": False, "noPrerequisite": False, "isCanceled": False,
        "isIntensive": False, "semester": semester, "isPrecise": True,
        "departments": [], "isCompulsory": None, "type": "quick",
    }


def fetch_page(semester, page):
    body = json.dumps({"query": make_query(semester), "batchSize": BATCH,
                       "pageIndex": page, "sorting": "correlation"}).encode("utf-8")
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"),
        "Origin": "https://course.ntu.edu.tw",
        "Referer": "https://course.ntu.edu.tw/search/quick",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:500]
        print(f"\n課程網回應錯誤：HTTP {e.code} {e.reason}\n{detail}")
        sys.exit(1)


def fetch_all(semester):
    courses, page, total = [], 0, None
    while total is None or page * BATCH < total:
        data = fetch_page(semester, page)
        total = data["totalCount"]
        courses.extend(data["courses"])
        page += 1
        print(f"\r下載中… {len(courses)}/{total}", end="")
        time.sleep(DELAY)
    print()
    return courses


def building_of(classroom):
    """取得建築名稱；少數教室沒有填建築，就用教室名稱開頭判斷（例如「博雅101」）"""
    if not classroom:
        return None
    b = classroom.get("buildingName")
    if b and b != "null":
        return b
    name = classroom.get("name") or ""
    for prefix, bname in [("博雅", "博雅教學館"), ("普", "普通教學館"), ("共", "共同教學館"),
                          ("新", "新生教學館"), ("綜", "綜合教學館")]:
        if name.startswith(prefix):
            return bname
    return None


def split_blocks(periods):
    """把節次串列切成連續的段落，例如 [2,3,4,8,9] → [[2,3,4],[8,9]]"""
    idx = sorted(ORDER.index(p) for p in periods if p in ORDER)
    blocks = []
    for i in idx:
        if blocks and i == blocks[-1][-1] + 1:
            blocks[-1].append(i)
        else:
            blocks.append([i])
    return [[ORDER[i] for i in b] for b in blocks]


def weeks_text(weeks):
    """[1,2,...,8] → "1-8"；[1,2,6] → "1,2,6"；空串列 → ""（整學期）"""
    if not weeks:
        return ""
    weeks = sorted(weeks)
    if len(weeks) > 1 and weeks == list(range(weeks[0], weeks[-1] + 1)):
        return f"{weeks[0]}-{weeks[-1]}"
    return ",".join(map(str, weeks))


def to_rows(courses):
    rows = []
    for c in courses:
        schedules = c.get("schedules", [])
        # 同一門課有排教室的時段在哪些建築；只有一棟時，拿來補「沒排教室」的時段
        known = {building_of(s.get("classroom")) for s in schedules if s.get("classroom")} - {None}
        for s in schedules:
            guessed = 0
            bname = building_of(s.get("classroom"))
            if not s.get("classroom") and len(known) == 1:
                bname, guessed = next(iter(known)), 1
            zone = BUILDING_TO_ZONE.get(bname)
            if not zone:
                continue
            periods = [PERIOD_FIX.get(p, p) for p in s.get("intervals", [])]
            for block in split_blocks(periods):
                rows.append({
                    "流水號": c.get("serial"),
                    "課名": c.get("name"),
                    "班次": c.get("class") or "",
                    "教師": (c.get("teacher") or {}).get("name", ""),
                    "區域": zone,
                    "建築": bname,
                    "教室": s["classroom"].get("name") if s.get("classroom") else "（未排教室）",
                    "星期": s.get("weekday"),
                    "開始節次": block[0],
                    "結束節次": block[-1],
                    "人數上限": c.get("totalStudentQuota") or 0,
                    "上課週次": weeks_text(c.get("intensiveWeeks")),
                    "教室推測": guessed,
                })
    rows.sort(key=lambda r: (r["區域"], r["星期"], ORDER.index(r["開始節次"])))
    return rows


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    semester = args[0] if args else "115-1"
    json_file = os.path.join(DATA_DIR, f"all_courses_{semester}.json")
    print(f"學期：{semester}")
    if "--from-json" in sys.argv:
        with open(json_file, encoding="utf-8") as f:
            courses = json.load(f)
    else:
        courses = fetch_all(semester)
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(courses, f, ensure_ascii=False)

    rows = to_rows(courses)
    with open(os.path.join(DATA_DIR, "courses_zones.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"\n全校共 {len(courses)} 門課，5 區內共 {len(rows)} 個上課時段，已存成 courses_zones.csv")
    print(f"   其中只上部分週次的 {sum(1 for r in rows if r['上課週次'])} 個、"
          f"用其他時段推測教室的 {sum(r['教室推測'] for r in rows)} 個")
    count = {}
    for r in rows:
        count[r["區域"]] = count.get(r["區域"], 0) + 1
    for z, n in count.items():
        print(f"   {z}：{n} 個時段")


if __name__ == "__main__":
    main()
