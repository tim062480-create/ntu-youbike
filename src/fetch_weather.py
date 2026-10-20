"""
台大附近天氣下載程式
------------------------------------------------
下雨時騎 YouBike 的人會大幅減少，驗證時要能把雨天分開看。
從 Open-Meteo（免費、不用申請帳號）下載台大附近每小時的降雨量和氣溫，
可以補抓過去 92 天，所以不用一直開著，隨時執行一次就會補齊。

用法：
  python fetch_weather.py
輸出：data/weather.csv（時間、降雨量(mm)、氣溫(°C)），舊資料會保留、重複的時間以新的為準。
只用到 Python 內建套件。

註：Open-Meteo 是氣象模型資料，不是測站實測。之後如果要更準，可以改用中央氣象署
臺北測站的觀測資料（需要申請 API 授權碼）。
"""

import csv
import json
import os
import urllib.request

from youbike_collector import DATA_DIR

LAT, LNG = 25.0174, 121.5397      # 台大校總區中心
API = ("https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}"
       "&hourly=precipitation,temperature_2m&past_days=92&forecast_days=1&timezone=Asia%2FTaipei")
WEATHER_FILE = os.path.join(DATA_DIR, "weather.csv")


def fetch():
    url = API.format(lat=LAT, lng=LNG)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r:
        data = json.loads(r.read().decode("utf-8"))["hourly"]
    return {t.replace("T", " "): (p, temp)
            for t, p, temp in zip(data["time"], data["precipitation"], data["temperature_2m"])
            if p is not None}


def load():
    """回傳 {"YYYY-MM-DD HH:00": (降雨量, 氣溫)}"""
    if not os.path.exists(WEATHER_FILE):
        return {}
    with open(WEATHER_FILE, encoding="utf-8-sig") as f:
        return {r["時間"]: (float(r["降雨量(mm)"]), float(r["氣溫(°C)"])) for r in csv.DictReader(f)}


def main():
    rows = load()
    new = fetch()
    rows.update(new)
    with open(WEATHER_FILE, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["時間", "降雨量(mm)", "氣溫(°C)"])
        for t in sorted(rows):
            w.writerow([t, rows[t][0], rows[t][1]])
    rainy = sum(1 for p, _ in new.values() if p >= 0.5)
    print(f"已更新 {WEATHER_FILE}：共 {len(rows)} 小時（這次抓到 {len(new)} 小時，其中下雨 {rainy} 小時）")


if __name__ == "__main__":
    main()
