"""
抓抱石館附近的 YouBike 站，記錄車數，算出「同時段歷史平均」給網頁做預測
------------------------------------------------
輸入：climbing/data/gyms.json（要先有經緯度，見 enrich.py）
輸出：
  climbing/data/youbike_stations.json   全台站點位置（網頁用來找「你附近」的站；加 --stations 或檔案不存在時才更新）
  climbing/data/youbike_near.json       每間館附近的站和最新車數（網頁讀）
  climbing/data/youbike_log/日期.csv     館附近站點的車數記錄（一天一個檔）
  climbing/data/youbike_pattern.json    每站「平日／假日 × 每 30 分鐘」的平均可借、可還（網頁做到達時預測）

資料來源（兩個都抓，同一站以有車數的為準）：
  1. YouBike 官網用的全台站點 JSON（apis.youbike.com.tw，非正式公開 API，格式可能變）
  2. 臺北市 YouBike 2.0 即時資訊（政府資料開放平臺，只有臺北市）
注意：2026-10-23 01:56 起，兩個來源的臺北、新北、桃園等站「可借、可還」都是 0（嘉義、高雄、台東正常），
所以「兩個都是 0」一律當作沒有資料，不寫進記錄、不算進平均。
只用 Python 內建套件。
用法：python climbing/scripts/youbike_near.py [--stations]
"""

import csv
import json
import math
import sys
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
GYMS = DATA / "gyms.json"
STATIONS_OUT = DATA / "youbike_stations.json"
NEAR_OUT = DATA / "youbike_near.json"
PATTERN_OUT = DATA / "youbike_pattern.json"
LOG_DIR = DATA / "youbike_log"

NATIONAL_URL = "https://apis.youbike.com.tw/json/station-yb2.json"
TAIPEI_URL = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
NEAR_M = 1000          # 館附近多遠內的站
NEAR_N = 4             # 每館最多幾個站
PATTERN_DAYS = 56      # 歷史平均用最近幾天


def get(d, *keys, default=None):
    """欄位名稱各來源不同，依序嘗試"""
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return default


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = json.loads(resp.read().decode("utf-8-sig"))
    if isinstance(raw, dict):
        for k in ("retVal", "data", "result", "stations"):
            if k in raw:
                raw = raw[k]
                break
        if isinstance(raw, dict):
            raw = list(raw.values())
    return raw


def to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def parse(raw, source):
    out = {}
    for s in raw:
        try:
            sno = str(get(s, "station_no", "sno", "StationUID", "stationNo"))
            lat = float(get(s, "lat", "latitude", "StationPosition_PositionLat"))
            lng = float(get(s, "lng", "lon", "longitude", "StationPosition_PositionLon"))
        except (TypeError, ValueError):
            continue
        name = str(get(s, "name_tw", "sna", "StationName_Zh_tw", "name", default=""))
        rent = to_int(get(s, "available_spaces", "available_rent_bikes", "sbi", "AvailableRentBikes"))
        ret = to_int(get(s, "empty_spaces", "available_return_bikes", "bemp", "AvailableReturnBikes"))
        if rent == 0 and ret == 0:   # 可借、可還都是 0 代表資料源沒給數字（見檔頭說明），當作沒有資料
            rent = ret = None
        out[sno] = {
            "name": name.replace("YouBike2.0_", ""),
            "lat": round(lat, 6), "lng": round(lng, 6),
            "total": to_int(get(s, "parking_spaces", "total", "tot", "Quantity")),
            "rent": rent, "ret": ret,
            "t": str(get(s, "updated_at", "srcUpdateTime", "mday", "time", default="")),
            "src": source,
        }
    return out


def fetch_all():
    stations, used = {}, []
    for url, name in ((NATIONAL_URL, "youbike-national"), (TAIPEI_URL, "taipei-opendata")):
        try:
            raw = fetch_json(url)
            if raw and isinstance(raw[0], dict):
                print(f"{name}：{len(raw)} 筆，欄位：{sorted(raw[0].keys())}")
            got = parse(raw, name)
        except Exception as e:
            print(f"{name} 失敗：{e}")
            continue
        used.append(name)
        for sno, s in got.items():
            # 前一個來源沒有車數時，用這個來源的補上
            if sno in stations and stations[sno]["rent"] is None:
                stations[sno].update({k: s[k] for k in ("rent", "ret", "total", "t", "src") if s[k] is not None})
            else:
                stations.setdefault(sno, s)
    return stations, used


def distance_m(lat1, lng1, lat2, lng2):
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin(math.radians(lat2 - lat1) / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lng2 - lng1) / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(a))


def build_pattern(today):
    """每站、平日／假日、每 30 分鐘（slot = 小時*2 + 分//30）的平均可借、可還和樣本數"""
    acc = defaultdict(lambda: [0, 0, 0])
    for i in range(PATTERN_DAYS):
        day = today - timedelta(days=i)
        f = LOG_DIR / f"{day:%Y-%m-%d}.csv"
        if not f.exists():
            continue
        with open(f, encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                rent, ret = to_int(row["可借車數"]), to_int(row["可還空位"])
                if rent is None or ret is None or (rent == 0 and ret == 0):
                    continue
                t = datetime.strptime(row["記錄時間"], "%Y-%m-%d %H:%M")
                daytype = "we" if t.isoweekday() >= 6 else "wd"
                a = acc[(row["站號"], daytype, t.hour * 2 + t.minute // 30)]
                a[0] += rent
                a[1] += ret
                a[2] += 1
    pattern = defaultdict(lambda: {"wd": {}, "we": {}})
    for (sno, daytype, slot), (r, e, n) in acc.items():
        pattern[sno][daytype][slot] = [round(r / n, 1), round(e / n, 1), n]
    return pattern


def main():
    gyms = [g for g in json.loads(GYMS.read_text(encoding="utf-8"))["gyms"]
            if g.get("lat") is not None and g.get("status") != "已停業"]
    stations, used = fetch_all()
    if not stations:
        print("YouBike 資料都抓不到，這次不更新")
        return 0

    if "--stations" in sys.argv or not STATIONS_OUT.exists():
        rows = sorted([sno, s["name"], s["lat"], s["lng"], s["total"]] for sno, s in stations.items())
        STATIONS_OUT.write_text(json.dumps({
            "_說明": "全台 YouBike 站點位置 [站號, 站名, 緯度, 經度, 總車位]，由 scripts/youbike_near.py 產生",
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M"), "sources": used, "stations": rows,
        }, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"已更新全台站點：{len(rows)} 站")

    near, keep = {}, set()
    for g in gyms:
        cand = sorted((distance_m(g["lat"], g["lng"], s["lat"], s["lng"]), sno) for sno, s in stations.items())
        near[g["id"]] = [[sno, round(d)] for d, sno in cand[:NEAR_N] if d <= NEAR_M]
        keep.update(sno for sno, _ in near[g["id"]])

    now = datetime.now()
    NEAR_OUT.write_text(json.dumps({
        "_說明": "抱石館附近 YouBike 站的最新車數，由 scripts/youbike_near.py 產生",
        "updated": now.strftime("%Y-%m-%d %H:%M"), "sources": used,
        "stations": {sno: stations[sno] for sno in sorted(keep)},
        "gyms": near,
    }, ensure_ascii=False, indent=0), encoding="utf-8")

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"{now:%Y-%m-%d}.csv"
    new_file = not log_file.exists()
    with open(log_file, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["記錄時間", "站號", "可借車數", "可還空位", "官方更新時間"])
        for sno in sorted(keep):
            s = stations[sno]
            if s["rent"] is not None:
                w.writerow([now.strftime("%Y-%m-%d %H:%M"), sno, s["rent"], s["ret"], s["t"]])

    PATTERN_OUT.write_text(json.dumps(build_pattern(now.date()), ensure_ascii=False, separators=(",", ":")),
                           encoding="utf-8")
    with_counts = sum(1 for sno in keep if stations[sno]["rent"] is not None)
    print(f"{len(near)} 間館、{len(keep)} 個附近站（{with_counts} 站有即時車數），來源：{', '.join(used)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
