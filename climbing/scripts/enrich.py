"""
補上抱石館的經緯度，並用 OpenStreetMap 交叉比對
------------------------------------------------
輸入：climbing/data/gyms_seed.json（人工整理，有來源）
輸出：
  climbing/data/gyms.json          網頁讀的資料（seed ＋ 經緯度 ＋ OSM 補充欄位 ＋ OSM 上有但我們沒列的地點）
  climbing/data/enrich_report.md   每間館的座標怎麼來的、OSM 和地址定位差多少，給人工驗證

做法：
  1. Overpass API 抓台灣所有 sport=climbing 或名稱有「攀岩／抱石／climb／boulder」的地點
  2. 每間館用 osm_keywords（每組關鍵字要全部出現在 OSM 名稱裡）比對，對到就用 OSM 的座標
  3. 對不到的用 Nominatim 查地址：完整地址 → 去掉樓層括號 → 只到「號」→ 路名＋行政區 → 館名
     （Nominatim 規定每秒最多 1 次，要帶 User-Agent）
  4. OSM 有、我們沒列的地點放進 osm_unmatched，網頁上用灰色標示「未人工確認」

只用 Python 內建套件。容器／本機連不到 OSM 時會保留上一次 gyms.json 的座標。
用法：python climbing/scripts/enrich.py
"""

import json
import math
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "gyms_seed.json"
OUT = ROOT / "data" / "gyms.json"
REPORT = ROOT / "data" / "enrich_report.md"

UA = "ntu-youbike-climbing-map/1.0 (https://github.com/tim062480-create/ntu-youbike)"
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_QUERY = """
[out:json][timeout:180];
area["ISO3166-1"="TW"][admin_level=2]->.tw;
(
  nwr["sport"~"climbing|bouldering"](area.tw);
  nwr["name"~"攀岩|抱石|[Cc]limb|[Bb]oulder"](area.tw);
);
out center tags;
"""
TW_BBOX = (21.8, 119.3, 25.4, 122.1)   # 南、西、北、東（含澎湖、金門以外的本島周邊）
OUTDOOR_TAGS = {("natural", "cliff"), ("climbing", "crag"), ("climbing", "route"),
                ("climbing", "route_bottom"), ("climbing", "route_top"), ("natural", "peak")}


def http_get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def distance_m(lat1, lng1, lat2, lng2):
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin(math.radians(lat2 - lat1) / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lng2 - lng1) / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(a))


def norm(s):
    """比對用：小寫、臺→台、去掉空白與符號"""
    s = (s or "").lower().replace("臺", "台")
    return re.sub(r"[\s\-_·•・.()（）]", "", s)


def fetch_osm():
    body = urllib.parse.urlencode({"data": OVERPASS_QUERY}).encode()
    for url in OVERPASS_URLS:
        try:
            req = urllib.request.Request(url, data=body, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=200) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            print(f"Overpass OK（{url}）：{len(data.get('elements', []))} 筆")
            return data.get("elements", [])
        except Exception as e:
            print(f"Overpass 失敗（{url}）：{e}")
    return None


def osm_place(el):
    tags = el.get("tags", {})
    lat = el.get("lat") or el.get("center", {}).get("lat")
    lng = el.get("lon") or el.get("center", {}).get("lon")
    names = [tags.get(k, "") for k in ("name", "name:zh", "name:zh-Hant", "name:en", "alt_name", "brand", "official_name")]
    return {
        "osm": f"{el['type']}/{el['id']}",
        "url": f"https://www.openstreetmap.org/{el['type']}/{el['id']}",
        "name": tags.get("name") or tags.get("name:en") or "",
        "names": [n for n in names if n],
        "lat": lat, "lng": lng,
        "outdoor": any((k, v) in OUTDOOR_TAGS for k, v in tags.items()),
        "tags": {k: v for k, v in tags.items()
                 if k in ("sport", "leisure", "climbing", "website", "contact:website", "phone", "contact:phone",
                          "opening_hours", "addr:city", "addr:district", "addr:street", "addr:housenumber",
                          "addr:full", "indoor", "climbing:boulder", "climbing:toprope", "climbing:sport",
                          "facebook", "contact:facebook", "instagram", "contact:instagram", "fee", "charge")},
    }


def match_osm(gym, places, geo=None, used=()):
    """osm_keywords 的任一組關鍵字全部出現在 OSM 名稱裡就算對到。
    多筆時：沒被別間用過的優先，再來離地址定位近的、同縣市的優先；
    離門牌定位超過 5 公里的不採用（同品牌不同分店）"""
    hits = []
    for p in places:
        if p["lat"] is None or p["outdoor"]:
            continue
        joined = norm(" ".join(p["names"]))
        if any(all(norm(k) in joined for k in group) for group in gym.get("osm_keywords", [])):
            hits.append(p)
    city = norm(gym.get("city", ""))

    def score(p):
        d = distance_m(p["lat"], p["lng"], geo["lat"], geo["lng"]) if geo else 0
        same_city = city and city in norm(p["tags"].get("addr:city", "") + " ".join(p["names"]))
        return (p["osm"] in used, d, not same_city)

    if geo and geo["coord_source"] == "nominatim:address":
        hits = [p for p in hits if distance_m(p["lat"], p["lng"], geo["lat"], geo["lng"]) <= 5000]
    return min(hits, key=score) if hits else None


def address_candidates(gym):
    addr = gym.get("address", "") or ""
    addr = re.sub(r"（.*?）|\(.*?\)", "", addr).strip()
    out = []
    if addr and "待確認" not in addr:
        out.append(("address", addr))
        no_floor = re.sub(r"(B\d+|\d+樓|\d+F|地下\S*樓)$", "", addr, flags=re.I).strip()
        if no_floor != addr:
            out.append(("address", no_floor))
        m = re.match(r"(.*?\d+號)", addr)
        if m and m.group(1) not in (addr, no_floor):
            out.append(("address", m.group(1)))
        m = re.match(r"(.*?[路街道](?:[一二三四五六七八九十]+段)?)", addr)
        if m:
            out.append(("road", m.group(1)))
        if not re.search(r"\d", addr):   # 「臺北市內湖運動中心」這種地標名稱
            out.append(("place", addr))
    if gym.get("name"):
        out.append(("name", f"{gym['name']} {gym.get('city', '')}"))
    seen, uniq = set(), []
    for kind, q in out:
        if q not in seen:
            seen.add(q)
            uniq.append((kind, q))
    return uniq


def in_taiwan(lat, lng):
    s, w, n, e = TW_BBOX
    return s <= lat <= n and w <= lng <= e


def geocode(gym):
    city = norm(gym.get("city", ""))
    for kind, q in address_candidates(gym):
        url = NOMINATIM_URL + "?" + urllib.parse.urlencode(
            {"q": q, "format": "jsonv2", "countrycodes": "tw", "limit": 1, "accept-language": "zh-TW"})
        time.sleep(1.1)
        try:
            res = http_get(url, timeout=30)
        except Exception as e:
            print(f"  Nominatim 失敗（{q}）：{e}")
            continue
        if not res:
            continue
        lat, lng = float(res[0]["lat"]), float(res[0]["lon"])
        disp = res[0].get("display_name", "")
        if not in_taiwan(lat, lng) or (city and city[:2] not in norm(disp)):
            continue   # 跑到別的縣市，不採用
        return {"lat": lat, "lng": lng, "coord_source": f"nominatim:{kind}", "coord_query": q, "coord_match": disp}
    return None


def main():
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    old = {}
    if OUT.exists():
        try:
            old = {g["id"]: g for g in json.loads(OUT.read_text(encoding="utf-8")).get("gyms", [])}
        except (ValueError, KeyError):
            old = {}

    elements = fetch_osm()
    places = [osm_place(e) for e in elements] if elements is not None else None
    used = set()
    gyms = []
    for g in seed["gyms"]:
        g = dict(g)
        if g.get("lat") is not None:          # seed 裡手動填的座標優先
            g["coord_source"] = g.get("coord_source", "manual")
        else:
            geo = None
            if g.get("status") != "已停業" and (places is not None or not old.get(g["id"], {}).get("lat")):
                geo = geocode(g)
            hit = match_osm(g, places, geo, used) if places else None
            if hit:
                used.add(hit["osm"])
                g.update({"lat": hit["lat"], "lng": hit["lng"], "coord_source": "osm"})
                g["osm"] = {"id": hit["osm"], "url": hit["url"], "name": hit["name"], "tags": hit["tags"]}
                if geo:
                    g["osm"]["dist_to_address_m"] = round(distance_m(hit["lat"], hit["lng"], geo["lat"], geo["lng"]))
                    g["coord_check"] = geo
            elif geo:
                g.update(geo)
            elif old.get(g["id"], {}).get("lat") is not None:   # 這次連不到，沿用上次結果
                for k in ("lat", "lng", "coord_source", "coord_query", "coord_match", "osm"):
                    if k in old[g["id"]]:
                        g[k] = old[g["id"]][k]
            else:
                g.update({"lat": None, "lng": None, "coord_source": "none"})
        gyms.append(g)
        print(f"{g['id']:24s} {g.get('coord_source')}")

    unmatched = []
    if places:
        for p in places:
            if p["osm"] in used or p["lat"] is None or p["outdoor"]:
                continue
            unmatched.append({k: p[k] for k in ("osm", "url", "name", "lat", "lng", "tags")})
    elif OUT.exists() and old:
        unmatched = json.loads(OUT.read_text(encoding="utf-8")).get("osm_unmatched", [])

    out = {
        "_說明": "由 scripts/enrich.py 產生，不要手動改；要改資料請改 gyms_seed.json",
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "checked": seed.get("checked"),
        "osm_ok": places is not None,
        "sources": seed["sources"],
        "gyms": gyms,
        "osm_unmatched": unmatched,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    write_report(out)
    n = sum(1 for g in gyms if g.get("lat") is not None)
    print(f"\n完成：{n}/{len(gyms)} 間有座標；OSM 上另有 {len(unmatched)} 個未列入的攀岩地點")


def write_report(out):
    lines = [
        "# 座標與 OpenStreetMap 交叉比對報告",
        "",
        f"產生時間：{out['generated']}（由 `climbing/scripts/enrich.py` 在 GitHub Actions 上產生）",
        f"OSM 連線：{'成功' if out['osm_ok'] else '失敗（沿用上次結果）'}",
        "",
        "座標來源說明：`osm` ＝ OSM 上有這間館（最準）；`nominatim:address` ＝ 用門牌定位；"
        "`nominatim:road` ＝ 只定位到路段（可能差幾百公尺）；`nominatim:place`／`nominatim:name` ＝ 用地標或館名定位；"
        "`none` ＝ 找不到，網頁上列在「位置待補」。",
        "",
        "| 館 | 狀態 | 座標來源 | 查詢字串／OSM 名稱 | OSM 與地址定位相差 | 驗證連結 |",
        "|---|---|---|---|---|---|",
    ]
    for g in out["gyms"]:
        src = g.get("coord_source", "")
        q = g.get("osm", {}).get("name") if src == "osm" else g.get("coord_query", "")
        diff = g.get("osm", {}).get("dist_to_address_m")
        diff = f"{diff} 公尺" if diff is not None else ""
        link = ""
        if g.get("lat") is not None:
            link = f"[OSM](https://www.openstreetmap.org/?mlat={g['lat']}&mlon={g['lng']}#map=18/{g['lat']}/{g['lng']})"
        gq = urllib.parse.quote(f"{g['name']} {g.get('address') or g.get('city', '')}")
        link += f" [Google 地圖](https://www.google.com/maps/search/?api=1&query={gq})"
        lines.append(f"| {g['name']} | {g.get('status', '')} | {src} | {q or ''} | {diff} | {link} |")
    lines += ["", f"## OSM 上有、但人工清單沒有的攀岩地點（{len(out['osm_unmatched'])} 個，可能是漏掉的館或已停業）", "",
              "| 名稱 | 標籤 | 連結 |", "|---|---|---|"]
    for p in out["osm_unmatched"]:
        tags = ", ".join(f"{k}={v}" for k, v in p["tags"].items() if k in ("sport", "leisure", "climbing", "website"))
        lines.append(f"| {p['name'] or '（無名稱）'} | {tags} | [OSM]({p['url']}) |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
