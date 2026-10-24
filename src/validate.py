"""
台大 YouBike 擁擠預測：用實際車數驗證預測
------------------------------------------------
讀入 data/youbike_log/*.csv（收資料程式記錄的車數，一天一個檔）和課表預測，
比較每個下課交換時段「車子實際變多還是變少」，跟預測的「難還／難借」對不對得上。

做法：
  1. 每一區把區內所有站的「可借車數」「可還空位」各自加總
  2. 只看正常上課日（週末、放假、運動會停課都跳過）；每一天用那一週的課表
     （半學期課只算在有上的週）
  3. 每個交換時段，看「上一節下課前 N 分鐘」到「這一節上課後 N 分鐘」這段期間，
     N 同時用 15 和 20 分鐘兩種算
  4. 判斷「符合」：
       預測難借 → 車數變少，或期間內區內可借車數一度 ≤ NEAR 台（幾乎借光）
       預測難還 → 車數變多，或期間內區內空位一度 ≤ NEAR 位（幾乎停滿）
  5. 比較基準：同樣的規則套在「預測正常」的時段上，算出「本來就會發生的比例」。
     預測難借的命中率要明顯高於正常時段「車變少或借光」的比例，才代表預測有用。
     比例都附 95% 信賴區間（Wilson 法），樣本少時區間會很寬。
  6. 相關係數：各區分開算，另外把每區的淨流量、車數變化先標準化（z 分數）再合起來算，
     避免人數多的博雅主導結果
  7. 有 data/weather.csv 時，標出該時段有沒有下雨（≥ 0.5 mm），並另外算不下雨時的結果

用法：
  python validate.py
結果會印在畫面上，並存成 data/validation.csv
"""

import csv
import glob
import math
import os
from datetime import datetime, timedelta

import net_flow as nf
from periods import ORDER, week_of, day_type

DATA_DIR = os.path.join(nf._ROOT, "data")
LOG_DIR = os.path.join(DATA_DIR, "youbike_log")
MAP_FILE = os.path.join(DATA_DIR, "stations_map.csv")
OUT_FILE = os.path.join(DATA_DIR, "validation.csv")
WEATHER_FILE = os.path.join(DATA_DIR, "weather.csv")

MARGINS = [15, 20]   # 交換時段前後各取幾分鐘（兩種都算）
MAX_GAP = 4          # 找記錄時，最多允許差幾分鐘（收資料改成每 2 分鐘一次）
NEAR = nf.NEAR       # 剩幾台（幾個空位）以下算「幾乎借光（停滿）」
RAIN_MM = 0.5        # 一小時降雨量超過多少算下雨


def log_files():
    """所有記錄檔（data/youbike_log 裡每天一個 csv），依日期排序"""
    return sorted(glob.glob(os.path.join(LOG_DIR, "*.csv")))


def has_log():
    return bool(log_files())


def load_station_zones():
    """站號 → 所屬區域（一站可能屬於多區）"""
    zones = {}
    with open(MAP_FILE, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            zones.setdefault(row["站號"], []).append(row["區域"])
    return zones


def load_zone_status(station_zones):
    """回傳 {區域: {記錄時間: (區內可借車總數, 區內可還空位總數)}}，只保留區內每一站都有記錄的時間點
    （可借、可還都是 0 的記錄視為車數不明，那個時間點整區都不算）"""
    raw = {}       # (區域, 時間) → {站號: (可借, 可還)}
    for path in log_files():
        with open(path, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                rent, ret = int(row["可借車數"]), int(row["可還空位"])
                if rent == 0 and ret == 0:   # 車數不明（2026-10-23 起官方資料整批回傳 0），不算
                    continue
                t = datetime.strptime(row["記錄時間"], "%Y-%m-%d %H:%M")
                for z in station_zones.get(row["站號"], []):
                    raw.setdefault((z, t), {})[row["站號"]] = (rent, ret)
    need = {}
    for sno, zs in station_zones.items():
        for z in zs:
            need[z] = need.get(z, 0) + 1
    status = {}
    for (z, t), d in raw.items():
        if len(d) == need[z]:
            status.setdefault(z, {})[t] = (sum(v[0] for v in d.values()), sum(v[1] for v in d.values()))
    return status


def load_history():
    """給查詢用的歷史資料：{(區域, 星期, "YYYY-MM-DD HH:MM"): (可借, 可還)}，只放正常上課日"""
    if not has_log():
        return {}
    hist = {}
    for z, series in load_zone_status(load_station_zones()).items():
        for t, v in series.items():
            if day_type(t.date())[0]:
                hist[(z, t.isoweekday(), t.strftime("%Y-%m-%d %H:%M"))] = v
    return hist


def load_weather():
    """{"YYYY-MM-DD HH": 降雨量}；沒有檔案回傳空字典"""
    if not os.path.exists(WEATHER_FILE):
        return {}
    with open(WEATHER_FILE, encoding="utf-8-sig") as f:
        return {r["時間"][:13]: float(r["降雨量(mm)"]) for r in csv.DictReader(f)}


def nearest(series, target):
    """在 series（時間 → 值）裡找最接近 target 的記錄，差太多回傳 None"""
    best, gap = None, None
    for t in series:
        g = abs((t - target).total_seconds()) / 60
        if gap is None or g < gap:
            best, gap = t, g
    return series[best] if gap is not None and gap <= MAX_GAP else None


def at(day, hhmm, minutes):
    h, m = map(int, hhmm.split(":"))
    return datetime(day.year, day.month, day.day, h, m) + timedelta(minutes=minutes)


def outcome(rent_before, rent_after, rent_min, ret_min):
    """這段期間實際發生了什麼：(車變少或幾乎借光, 車變多或幾乎停滿, 說明)"""
    change = rent_after - rent_before
    fewer = change < 0 or rent_min <= NEAR
    more = change > 0 or ret_min <= NEAR
    notes = []
    if rent_min <= NEAR:
        notes.append(f"一度只剩 {rent_min} 台")
    if ret_min <= NEAR:
        notes.append(f"一度只剩 {ret_min} 位")
    return fewer, more, "、".join(notes)


def compute(margin=15):
    """回傳 (比對結果 rows, 各區車數 status, 有記錄的日期 dates)；margin＝前後各看幾分鐘"""
    courses = nf.load_courses()
    status = load_zone_status(load_station_zones()) if has_log() else {}
    weather = load_weather()
    dates = sorted({t.date() for series in status.values() for t in series})
    by_day = {}                                   # (區域, 日期) → 那一天的記錄，避免每次都掃整學期的資料
    for zone, series in status.items():
        for t, v in series.items():
            by_day.setdefault((zone, t.date()), {})[t] = v
    tables = {}                                   # 每一週的課表和門檻只算一次
    rows = []
    for day in dates:
        ok, note = day_type(day)
        if not ok:
            continue
        week, wd = week_of(day), day.isoweekday()
        if week not in tables:
            table = nf.build_table(courses, week)
            tables[week] = (table, nf.thresholds(table))
        table, th = tables[week]
        for zone in nf.ZONES:
            series = by_day.get((zone, day), {})
            for p in ORDER[1:]:
                arrive, leave, net = table[(zone, wd, p)]
                if arrive == 0 and leave == 0:
                    continue
                start, end = nf.exchange_window(p)
                t0, t1 = at(day, start, -margin), at(day, end, margin)
                before, after = nearest(series, t0), nearest(series, t1)
                if before is None or after is None:
                    continue
                inside = [v for t, v in series.items() if t0 <= t <= t1] or [before, after]
                rent_min = min(v[0] for v in inside)
                ret_min = min(v[1] for v in inside)
                fewer, more, why = outcome(before[0], after[0], rent_min, ret_min)
                level = nf.level_of(table, th, zone, wd, p)
                if level == "難借":
                    hit = "符合" if fewer else "不符合"
                elif level == "難還":
                    hit = "符合" if more else "不符合"
                else:
                    hit = ""
                rain = weather.get(t0.strftime("%Y-%m-%d %H"))
                rows.append({"時間窗": f"前後{margin}分鐘", "日期": day.isoformat(), "星期": wd, "週次": week,
                             "特殊週": note, "區域": zone, "時段": f"{start}-{end}", "預測": level, "淨流量": net,
                             "之前車數": before[0], "之後車數": after[0],
                             "期間最低": rent_min, "期間最高": max(v[0] for v in inside),
                             "期間最少空位": ret_min, "車數變化": after[0] - before[0],
                             "車變少或借光": int(fewer), "車變多或停滿": int(more), "說明": why,
                             "降雨量": "" if rain is None else rain,
                             "下雨": "" if rain is None else int(rain >= RAIN_MM), "結果": hit})
    return rows, status, dates


# ========== 統計 ==========
def wilson(k, n, z=1.96):
    """比例 k/n 的 95% 信賴區間（Wilson 法），回傳 (下限, 上限)"""
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - r) / d, (c + r) / d


def rate_text(k, n):
    lo, hi = wilson(k, n)
    return f"{k}/{n}＝{k / n:.0%}（95% 區間 {lo:.0%}～{hi:.0%}）"


def corr(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return sxy / math.sqrt(sxx * syy) if sxx and syy else None


def zscores(vals):
    n = len(vals)
    m = sum(vals) / n
    sd = math.sqrt(sum((v - m) ** 2 for v in vals) / n)
    return [(v - m) / sd if sd else 0.0 for v in vals]


def correlations(rows):
    """回傳 ({區域: 相關係數}, 各區標準化後合併的相關係數)"""
    per_zone, zx, zy = {}, [], []
    for zone in nf.ZONES:
        sub = [r for r in rows if r["區域"] == zone]
        if len(sub) < 3:
            continue
        xs, ys = [r["淨流量"] for r in sub], [r["車數變化"] for r in sub]
        per_zone[zone] = corr(xs, ys)
        zx += zscores(xs)
        zy += zscores(ys)
    return per_zone, corr(zx, zy)


def summarize(rows):
    """印出一組比對結果的命中率（含比較基準）、相關係數、各區結果"""
    print(f"  共比對 {len(rows)} 個下課時段")
    normal = [r for r in rows if r["預測"] == "正常"]
    for level, key, word in [("難借", "車變少或借光", "車變少或幾乎借光"), ("難還", "車變多或停滿", "車變多或幾乎停滿")]:
        sub = [r for r in rows if r["預測"] == level]
        if sub:
            ok = sum(r[key] for r in sub)
            avg = sum(r["車數變化"] for r in sub) / len(sub)
            print(f"  預測{level}：實際{word} {rate_text(ok, len(sub))}，平均車數變化 {avg:+.1f} 台")
        if normal:
            base = sum(r[key] for r in normal)
            print(f"    比較基準（預測正常的時段也{word}）：{rate_text(base, len(normal))}")
    per_zone, pooled = correlations(rows)
    if per_zone:
        print("  淨流量和車數變化的相關係數（越接近 1 表示預測方向越準）：")
        print("    " + "、".join(f"{z} {c:.2f}" if c is not None else f"{z} —" for z, c in per_zone.items()))
        if pooled is not None:
            print(f"    各區標準化後合併：{pooled:.2f}")
    parts = []
    for zone in nf.ZONES:
        sub = [r for r in rows if r["區域"] == zone and r["結果"]]
        if sub:
            ok = sum(1 for r in sub if r["結果"] == "符合")
            parts.append(f"{zone} {ok}/{len(sub)}（{ok / len(sub):.0%}）")
    if parts:
        print("  各區命中率：" + "、".join(parts))


def main():
    if not has_log():
        print(f"{LOG_DIR} 裡還沒有記錄，請先執行收資料程式。")
        return
    all_rows = []
    for i, margin in enumerate(MARGINS):
        rows, status, dates = compute(margin)
        if i == 0:
            class_days = [d for d in dates if day_type(d)[0]]
            print(f"YouBike 記錄期間：{dates[0]} ～ {dates[-1]}，其中正常上課日 {len(class_days)} 天" if dates else "還沒有記錄")
        print(f"\n【下課前後 {margin} 分鐘】")
        if not rows:
            print("  目前的記錄還對不上任何下課時段，上課日白天收集幾小時後再試。")
            continue
        summarize(rows)
        dry = [r for r in rows if r["下雨"] == 0]
        if dry and len(dry) < len(rows):
            print(f"\n  ── 只看沒下雨的時段（{len(dry)} 個）──")
            summarize(dry)
        all_rows.extend(rows)
    if all_rows:
        with open(OUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
            w.writeheader()
            w.writerows(all_rows)
        print(f"\n詳細結果已存成 {OUT_FILE}")


if __name__ == "__main__":
    main()
