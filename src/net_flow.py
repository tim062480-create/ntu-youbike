"""
台大 YouBike 擁擠預測：淨流量計算與查詢
------------------------------------------------
讀入 data/courses_zones.csv，算出每一區、每一天、每一個「上下課交換時間」的：
  到達人數：這段時間開始上課的人數總和
  離開人數：上一節下課的人數總和
  （人數使用課程網公布的人數上限）
  淨流量 ＝ 到達 − 離開（正數→車變多、難還；負數→車變少、難借）
再把「同一區」全週所有時段排名：前 20% 判為「難還」、後 20% 判為「難借」。
（每區各自排名，因為各區人數規模差很多，全校一起排的話小區永遠是「正常」）

半學期課（例如微積分1 只上第 1～8 週）只算在有上課的那幾週，所以每一週的表可能不同。

有 YouBike 歷史資料時，查詢會結合歷史：過去同一個星期幾、同一時間，
區內平均可借車數 ≤ NEAR 台就直接判「難借」，平均空位 ≤ NEAR 位就判「難還」，
否則沿用課表的判斷。（結合方式還在討論，見 專案紀錄.md）

用法：
  python net_flow.py               # 進入查詢模式，輸入區域、星期、時間（用這一週的課表）
  python net_flow.py --summary     # 列出每一區最難借、最難還的時段
  python net_flow.py --week 9      # 指定第幾週
"""

import csv
import os
import sys
from datetime import date

from periods import PERIODS, ORDER, week_of, LAST_WEEK

_HERE = os.path.dirname(os.path.abspath(__file__))
# 程式放在 src 資料夾時，資料在旁邊的 data
_ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE).lower() == "src" else _HERE
COURSE_FILE = os.path.join(_ROOT, "data", "courses_zones.csv")

ZONES = ["博雅普通區", "共同教學館", "新生教學館", "綜合體育館", "總圖區"]
WEEKDAY_NAMES = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五"}
LEVEL_ICON = {"難借": "🚲 車會被借光", "難還": "🅿️ 車位會停滿", "正常": "👍 借還應該都沒問題"}
LEVEL_TIP = {"難借": "建議提早出門，或走到附近其他區的站借車",
             "難還": "建議提早到，或停在附近其他區的站",
             "正常": ""}
TOP_SHARE = 0.2      # 每區淨流量排名前 20% 難還、後 20% 難借
NEAR = 2             # 歷史平均剩 2 台（或 2 個空位）以下，就算幾乎借光（停滿）


# ========== 讀檔 ==========
def parse_weeks(text):
    """"1-8" → {1..8}；"1,3,5" → {1,3,5}；空白 → None（整學期）"""
    text = (text or "").strip()
    if not text:
        return None
    weeks = set()
    for part in text.split(","):
        if "-" in part:
            a, b = part.split("-")
            weeks.update(range(int(a), int(b) + 1))
        else:
            weeks.add(int(part))
    return weeks


def load_courses():
    courses = []
    with open(COURSE_FILE, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            row["星期"] = int(row["星期"])
            row["人數上限"] = int(row["人數上限"])
            row["人數"] = row["人數上限"]
            row["週次"] = parse_weeks(row.get("上課週次"))
            courses.append(row)
    return courses


def meets(course, week):
    """這門課第 week 週有沒有上課；week 是 None 時只看整學期都有的課"""
    if course["週次"] is None:
        return True
    return week is not None and week in course["週次"]


def current_week():
    """今天是第幾週；不在學期內就用第 1 週"""
    return week_of(date.today()) or 1


def next_period(p):
    """下一節，例如 "4" → "5"；最後一節回傳 None"""
    i = ORDER.index(p)
    return ORDER[i + 1] if i + 1 < len(ORDER) else None


# ========== 核心計算 ==========
def count_flow(courses, zone, day, period, week=None):
    """第 period 節開始前的下課時間：回傳 (到達人數, 離開人數)。連堂中間不算。"""
    arrive = 0
    leave = 0
    for c in courses:
        if c["區域"] == zone and c["星期"] == day and meets(c, week):
            if c["開始節次"] == period:
                arrive += c["人數"]
            if next_period(c["結束節次"]) == period:
                leave += c["人數"]
    return arrive, leave


def judge(net, high, low):
    if net >= high and net > 0:
        return "難還"
    elif net <= low and net < 0:
        return "難借"
    else:
        return "正常"


def build_table(courses, week=None):
    """回傳 {(區域, 星期, 節次): (到達, 離開, 淨流量)}；week＝第幾週（半學期課只算有上的週）"""
    table = {}
    for zone in ZONES:
        for day in range(1, 6):
            for p in ORDER[1:]:          # 第 1 節之後才有「前一節下課」
                arrive, leave = count_flow(courses, zone, day, p, week)
                table[(zone, day, p)] = (arrive, leave, arrive - leave)
    return table


def thresholds(table):
    """每一區各自排名：該區全週有人移動的時段，淨流量排序後取前 20%、後 20% 當門檻
    回傳 {區域: (難還門檻, 難借門檻)}"""
    result = {}
    for zone in ZONES:
        nets = sorted(v[2] for k, v in table.items() if k[0] == zone and (v[0] or v[1]))
        if not nets:
            result[zone] = (0, 0)
            continue
        result[zone] = (nets[min(int(len(nets) * (1 - TOP_SHARE)), len(nets) - 1)],
                        nets[int(len(nets) * TOP_SHARE)])
    return result


def level_of(table, th, zone, day, period):
    """課表預測的等級"""
    high, low = th[zone]
    return judge(table[(zone, day, period)][2], high, low)


def combine(schedule_level, history):
    """結合課表預測和歷史資料，回傳 (最後等級, 依據說明)
    history：(平均可借, 平均可還, 天數) 或 None"""
    if history:
        rent, ret, n = history
        if rent <= NEAR:
            return "難借", f"歷史資料：過去 {n} 天這時平均只剩 {rent:.1f} 台"
        if ret <= NEAR:
            return "難還", f"歷史資料：過去 {n} 天這時平均只剩 {ret:.1f} 個空位"
    return schedule_level, "課表預測"


def to_minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def time_to_period(hhmm):
    """把 "12:15" 換成最接近的交換時段（第幾節開始前）；差超過 20 分鐘回傳 None"""
    t = to_minutes(hhmm)
    best, best_gap = None, None
    for p in ORDER[1:]:
        gap = abs(t - to_minutes(PERIODS[p][0]))
        if best_gap is None or gap < best_gap:
            best, best_gap = p, gap
    return best if best_gap <= 20 else None


def latest_period(hhmm):
    """上課中的時間：回傳「最近一次已經發生的下課時段」；第 1 節開始前或晚上 22:00 後回傳 None"""
    t = to_minutes(hhmm)
    if t > to_minutes(PERIODS[ORDER[-1]][1]):
        return None
    last = None
    for p in ORDER[1:]:
        if to_minutes(PERIODS[p][0]) <= t:
            last = p
    return last


def exchange_window(period):
    """交換時段的時間範圍：上一節下課 ～ 這一節上課，例如第 5 節 → ("12:10", "12:20")"""
    prev = ORDER[ORDER.index(period) - 1]
    return PERIODS[prev][1], PERIODS[period][0]


# ========== 查詢 ==========
def report(table, th, zone, day, hhmm, history=None):
    """th：thresholds() 的結果；history：validate.load_history() 的結果"""
    period = time_to_period(hhmm)
    in_class = period is None
    if in_class:
        period = latest_period(hhmm)
    lines = [f"\n📍 {zone}　星期{WEEKDAY_NAMES[day]} {hhmm}"]
    h = history_at(history, zone, day, hhmm) if history else None
    if period is None:
        lines.append("   不在課表涵蓋的時間（第 1 節前或 22:00 後），課表無法預測")
        schedule_level = None
    else:
        arrive, leave, net = table[(zone, day, period)]
        schedule_level = level_of(table, th, zone, day, period)
        start, end = exchange_window(period)
        if in_class:
            lines.append(f"   上課中，沿用最近一次下課（{start}–{end}）的狀態")
        else:
            lines.append(f"   下課時間 {start}–{end}（第 {period} 節開始前）")
        lines.append(f"   來上課：{arrive} 人　下課離開：{leave} 人　淨流量：{net:+d}")
        lines.append(f"   課表預測：{schedule_level}")
    if history is not None:
        if h:
            rent, ret, n = h
            note = "（天數少，僅供參考）" if n < 3 else ""
            lines.append(f"   歷史資料：過去 {n} 個星期{WEEKDAY_NAMES[day]}的這個時間，平均可借 {rent:.0f} 台、可還 {ret:.0f} 位{note}")
        else:
            lines.append("   歷史資料：這個時間還沒有收集到記錄")
    if schedule_level is not None or h:
        level, why = combine(schedule_level or "正常", h)
        lines.append(f"   ➜ 綜合判斷：{level} {LEVEL_ICON[level]}（依據：{why}）")
        if LEVEL_TIP[level]:
            lines.append(f"   {LEVEL_TIP[level]}")
    return "\n".join(lines)


def history_at(history, zone, day, hhmm, tolerance=10):
    """從 history 找同一個星期幾、時間相差 tolerance 分鐘內的記錄，回傳 (平均可借, 平均可還, 天數)"""
    t = to_minutes(hhmm)
    by_date = {}
    for (z, d, ts), (rent, ret) in history.items():
        if z == zone and d == day:
            gap = abs(to_minutes(ts[11:16]) - t)
            date_ = ts[:10]
            if gap <= tolerance and (date_ not in by_date or gap < by_date[date_][0]):
                by_date[date_] = (gap, rent, ret)
    if not by_date:
        return None
    vals = list(by_date.values())
    return (sum(v[1] for v in vals) / len(vals), sum(v[2] for v in vals) / len(vals), len(vals))


def check_input(zone, day_text, hhmm):
    if zone not in ZONES:
        return "找不到這個區域，請輸入：" + "、".join(ZONES)
    if not day_text.isdigit() or int(day_text) not in range(1, 6):
        return "星期請輸入數字 1 到 5"
    parts = hhmm.split(":")
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        return "時間請用 12:15 這種格式"
    return None


def ask_zone():
    print("\n區域：" + "　".join(f"{i}.{z}" for i, z in enumerate(ZONES, 1)))
    text = input("請輸入區域（名稱或編號，直接按 Enter 結束）：").strip()
    if text.isdigit() and 1 <= int(text) <= len(ZONES):
        return ZONES[int(text) - 1]
    for z in ZONES:                       # 允許只打部分名稱，例如「博雅」「總圖」
        if text and text in z:
            return z
    return text


def interactive(table, th):
    print("\n=== 台大 YouBike 擁擠預測 ===")
    try:
        import validate
        history = validate.load_history()
        print(f"（已載入 YouBike 歷史資料 {len({k[2][:10] for k in history})} 個上課日）")
    except Exception:
        history = None
    while True:
        zone = ask_zone()
        if zone == "":
            print("掰掰！")
            break
        day_text = input("請輸入星期（1-5）：").strip()
        hhmm = input("請輸入時間（例如 12:15）：").strip().replace("：", ":")
        msg = check_input(zone, day_text, hhmm)
        if msg:
            print("⚠️ " + msg)
            continue
        print(report(table, th, zone, int(day_text), hhmm, history))


def summary(table, th, top=3):
    """每區列出最難借、最難還的時段"""
    for zone in ZONES:
        high, low = th[zone]
        rows = [(k, v) for k, v in table.items() if k[0] == zone and (v[0] or v[1])]
        rows.sort(key=lambda kv: kv[1][2])
        print(f"\n【{zone}】（難還門檻 ≥ {high}，難借門檻 ≤ {low}）")
        print("  最難借：")
        for (z, d, p), (a, l, n) in rows[:top]:
            if judge(n, high, low) == "難借":
                s, e = exchange_window(p)
                print(f"    星期{WEEKDAY_NAMES[d]} {s}–{e}　離開 {l} 人、到達 {a} 人（{n:+d}）")
        print("  最難還：")
        for (z, d, p), (a, l, n) in reversed(rows[-top:]):
            if judge(n, high, low) == "難還":
                s, e = exchange_window(p)
                print(f"    星期{WEEKDAY_NAMES[d]} {s}–{e}　到達 {a} 人、離開 {l} 人（{n:+d}）")


def main():
    week = current_week()
    if "--week" in sys.argv:
        week = int(sys.argv[sys.argv.index("--week") + 1])
        if not 1 <= week <= LAST_WEEK:
            print(f"週次請輸入 1 到 {LAST_WEEK}")
            return
    courses = load_courses()
    table = build_table(courses, week)
    th = thresholds(table)
    print(f"已讀入 {len(courses)} 個上課時段，使用第 {week} 週的課表（每區各自排名）")
    if "--summary" in sys.argv:
        summary(table, th)
    else:
        interactive(table, th)


if __name__ == "__main__":
    main()
