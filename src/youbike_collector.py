"""
台大 YouBike 收資料程式
------------------------------------------------
功能：
  1. 第一次執行時，自動找出每個區域附近最近的 YouBike 站，存成 stations_map.csv
  2. 之後每 2 分鐘記錄一次這些站的「可借車數、可還空位」，存進 data/youbike_log/日期.csv（一天一個檔）
     （官方資料每分鐘更新；下課只有 5～10 分鐘，10 分鐘抓一次太粗）

用法：
  python youbike_collector.py          # 開始持續收資料（按 Ctrl+C 停止）
  python youbike_collector.py --once   # 只抓一次，測試用
  python youbike_collector.py --minutes 350   # 跑 350 分鐘後自動結束（雲端排程用）

只用到 Python 內建套件，不用另外安裝任何東西。
資料來源：臺北市 YouBike 2.0 即時資訊（政府資料開放平臺）
"""

import csv
import json
import math
import os
import sys
import time
import urllib.request
from datetime import datetime

API_URL = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"

# ===== 設定區（可以自己改）=====
INTERVAL_MINUTES = 2           # 幾分鐘抓一次
NEAREST_N = 3                  # 每區取最近的幾個站
MAX_DISTANCE_M = 500           # 超過幾公尺就不算「附近」

# 區域 → 區內建築物的經緯度（從 Google 地圖取得，若位置不對請自行修正）
# 位置相近的建築物放同一區，共用附近的站點
ZONES = {
    "博雅普通區": {
        "博雅教學館": (25.01884, 121.53670),
        "普通教學館": (25.01856, 121.53672),
    },
    "共同教學館": {
        "共同教學館": (25.01585, 121.53757),
    },
    "新生教學館": {
        "新生教學館": (25.01974, 121.53847),
    },
    "綜合體育館": {
        "綜合體育館": (25.02169, 121.53512),
    },
    "總圖區": {
        "總圖書館": (25.01734, 121.54057),
        "農藝館": (25.01828, 121.54081),
        "綜合教學館": (25.01824, 121.53950),
        "第一學生活動中心": (25.01776, 121.54009),
    },
}
ZONE_N = {"總圖區": 4}           # 建築物比較多的區可以多取幾個站

# 建築物 → 區域（之後整理課表時，用這個把每門課的教室對應到區域）
BUILDING_TO_ZONE = {b: z for z, blds in ZONES.items() for b in blds}

_HERE = os.path.dirname(os.path.abspath(__file__))
# 程式放在 src 資料夾時，資料在旁邊的 data、地圖在 output
_ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE).lower() == "src" else _HERE
DATA_DIR = os.path.join(_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)
MAP_FILE = os.path.join(DATA_DIR, "stations_map.csv")
LOG_DIR = os.path.join(DATA_DIR, "youbike_log")     # 一天一個檔，例如 2026-10-21.csv
# ===============================


def get(d, *keys, default=None):
    """欄位名稱有時會變，依序嘗試幾個可能的名稱"""
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return default


def fetch_stations():
    """從官方 API 抓全部站點，整理成統一格式的字典串列"""
    req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    if isinstance(raw, dict):  # 有些版本會包在 retVal 裡
        raw = raw.get("retVal", raw)
        if isinstance(raw, dict):
            raw = list(raw.values())

    stations = []
    for s in raw:
        try:
            stations.append({
                "sno": str(get(s, "sno")),
                "name": str(get(s, "sna", default="")).replace("YouBike2.0_", ""),
                "lat": float(get(s, "latitude", "lat")),
                "lng": float(get(s, "longitude", "lng")),
                "total": int(get(s, "total", "Quantity", "tot", default=0)),
                "rent": int(get(s, "available_rent_bikes", "sbi", default=0)),
                "return": int(get(s, "available_return_bikes", "bemp", default=0)),
                "active": str(get(s, "act", default="1")),
                "src_time": str(get(s, "srcUpdateTime", "mday", default="")),
            })
        except (TypeError, ValueError):
            continue  # 資料不完整的站就跳過
    return stations


def distance_m(lat1, lng1, lat2, lng2):
    """兩個經緯度之間的距離（公尺），使用 Haversine 公式"""
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def build_station_map(stations):
    """每區找最近的幾個站，回傳 [(區域, 站號, 站名, 距離), ...]
    站到「區」的距離 = 站到區內最近那棟建築物的距離"""
    rows = []
    for zname, blds in ZONES.items():
        nearby = []
        for s in stations:
            d = min(distance_m(blat, blng, s["lat"], s["lng"]) for blat, blng in blds.values())
            if d <= MAX_DISTANCE_M:
                nearby.append((d, s))
        nearby.sort(key=lambda x: x[0])
        for d, s in nearby[:ZONE_N.get(zname, NEAREST_N)]:
            rows.append((zname, s["sno"], s["name"], round(d)))
    return rows


def save_station_map(rows):
    with open(MAP_FILE, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["區域", "站號", "站名", "距離(公尺)"])
        w.writerows(rows)
    print(f"\n已產生區域與站點對應表：{MAP_FILE}")
    current = None
    for bname, sno, name, d in rows:
        if bname != current:
            print(f"\n【{bname}】")
            current = bname
        print(f"   {name}（{d} 公尺）")


def load_station_map():
    with open(MAP_FILE, encoding="utf-8-sig") as f:
        return [row for row in csv.DictReader(f)]


def log_once(target_snos):
    """抓一次資料，把目標站點的狀態寫進今天的記錄檔"""
    stations = fetch_stations()
    now = datetime.now()
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, now.strftime("%Y-%m-%d") + ".csv")
    new_file = not os.path.exists(log_file)
    count = 0
    with open(log_file, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["記錄時間", "星期", "站號", "站名", "總車位", "可借車數", "可還空位", "是否營運", "官方更新時間"])
        for s in stations:
            if s["sno"] in target_snos:
                w.writerow([now.strftime("%Y-%m-%d %H:%M"), now.isoweekday(), s["sno"], s["name"],
                            s["total"], s["rent"], s["return"], s["active"], s["src_time"]])
                count += 1
    print(f"{now.strftime('%m/%d %H:%M')}  已記錄 {count} 個站")
    return stations


def sleep_until_next(interval):
    """睡到下一個整分刻度（例如每 2 分鐘就對齊 :00、:02、:04…），避免時間越跑越偏"""
    now = time.time()
    step = interval * 60
    time.sleep(step - now % step + 1)


def main():
    once = "--once" in sys.argv
    stop_at = None
    if "--minutes" in sys.argv:
        stop_at = time.time() + float(sys.argv[sys.argv.index("--minutes") + 1]) * 60

    # 第一步：建立（或讀取）區域→站點對應表
    if not os.path.exists(MAP_FILE):
        print("第一次執行，正在下載站點資料並建立對應表...")
        rows = build_station_map(fetch_stations())
        if not rows:
            print("找不到任何附近站點，請檢查 ZONES 的經緯度是否正確。")
            return
        save_station_map(rows)
    mapping = load_station_map()
    target_snos = {row["站號"] for row in mapping}
    print(f"\n追蹤 {len(target_snos)} 個站，每 {INTERVAL_MINUTES} 分鐘記錄一次，存在 {LOG_DIR}")

    # 第二步：持續記錄
    while True:
        try:
            log_once(target_snos)
        except Exception as e:  # 網路斷線等狀況，不要讓程式停掉
            print(f"{datetime.now().strftime('%m/%d %H:%M')}  抓取失敗：{e}，下次再試")
        if once or (stop_at and time.time() + INTERVAL_MINUTES * 60 > stop_at):
            break
        sleep_until_next(INTERVAL_MINUTES)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已停止收資料。")
