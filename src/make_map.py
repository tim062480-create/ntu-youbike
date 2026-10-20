"""
產生台大 YouBike 追蹤站點地圖
------------------------------------------------
用法：放在和 youbike_collector.py、stations_map.csv 同一個資料夾，直接執行。
會產生 ntu_youbike_map.html 並自動用瀏覽器打開（需要網路才看得到底圖）。
只用到 Python 內建套件。
"""

import csv
import json
import webbrowser
from datetime import datetime
from pathlib import Path

from youbike_collector import ZONES, fetch_stations

_HERE = Path(__file__).resolve().parent
# 程式放在 src 資料夾時，資料在旁邊的 data、地圖存到 output
_ROOT = _HERE.parent if _HERE.name.lower() == "src" else _HERE
MAP_FILE = _ROOT / "data" / "stations_map.csv"
OUTPUT_DIR = _ROOT / "output"

COLORS = {  # 每區一個顏色
    "博雅普通區": "#d9480f",
    "共同教學館": "#1971c2",
    "新生教學館": "#2f9e44",
    "綜合體育館": "#9c36b5",
    "總圖區": "#c2255c",
}

HTML = """<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>台大 YouBike 追蹤站點地圖</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
html,body{margin:0;height:100%;font-family:"Microsoft JhengHei","PingFang TC",sans-serif;color:#1c2421}
.layout{display:flex;height:100%}
#side{width:330px;flex:none;overflow-y:auto;background:#f6f8f7;border-right:1px solid #dde3e0;padding:18px 18px 28px;box-sizing:border-box}
#map{flex:1;min-width:0}
h1{font-size:19px;margin:0 0 6px}
.sub{font-size:13px;color:#5b6762;line-height:1.6;margin:0 0 14px}
.stats{display:flex;gap:8px;margin-bottom:14px}
.stat{flex:1;background:#fff;border:1px solid #dde3e0;border-radius:8px;padding:8px 10px}
.stat b{display:block;font-size:20px}
.stat span{font-size:12px;color:#5b6762}
.zone{background:#fff;border:1px solid #dde3e0;border-radius:10px;padding:12px 14px;margin-bottom:10px}
.zone h2{font-size:15px;margin:0 0 6px;display:flex;align-items:center;gap:8px}
.label{font-size:11.5px;color:#5b6762;letter-spacing:.05em;margin:8px 0 3px}
.blds{font-size:13px;line-height:1.6}
ul{list-style:none;margin:0;padding:0}
li.st{display:flex;justify-content:space-between;gap:8px;font-size:13px;padding:4px 6px;border-radius:6px;cursor:pointer}
li.st:hover,li.st:focus{background:#eef3f1;outline:none}
li.st small{color:#5b6762;white-space:nowrap}
.dot{display:inline-block;width:11px;height:11px;border-radius:50%;flex:none}
.key{font-size:12.5px;color:#5b6762;line-height:1.8;margin-top:12px}
.key .ring{display:inline-block;width:9px;height:9px;border-radius:50%;border:2px solid #222;vertical-align:-1px;margin-right:4px}
.key .big{display:inline-block;width:12px;height:12px;border-radius:50%;background:#888;border:2px solid #fff;box-shadow:0 0 0 1px #bbb;vertical-align:-2px;margin-right:4px}
.bld{background:none;border:none}
.bld div{background:#222;color:#fff;font-size:12px;padding:2px 6px;border-radius:4px;white-space:nowrap;transform:translate(-50%,-140%);display:inline-block}
@media (max-width:760px){.layout{flex-direction:column}#side{width:auto;max-height:45%;border-right:none;border-bottom:1px solid #dde3e0}#map{flex:1}}
</style></head><body><div class="layout">
<aside id="side">
  <h1>台大 YouBike 追蹤站點</h1>
  <p class="sub">目前已收錄的 YouBike 站和台大建築物。站點依距離分到 5 個區域，點清單裡的站名可以在地圖上找到它。</p>
  <div class="stats">
    <div class="stat"><b id="nSt"></b><span>YouBike 站</span></div>
    <div class="stat"><b id="nBld"></b><span>建築物</span></div>
    <div class="stat"><b id="nZone"></b><span>區域</span></div>
  </div>
  <div id="zones"></div>
  <div class="key"><span class="big"></span>YouBike 站（顏色＝所屬區域）<br><span class="ring"></span>建築物<br>車數為 <span id="upd"></span> 產生地圖時的狀態</div>
</aside>
<div id="map"></div></div>
<script>
const DATA = __DATA__;
const map = L.map('map').setView([25.0185, 121.5385], 17);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
  {maxZoom: 19, attribution: 'Tiles &copy; Esri'}).addTo(map);
const all = [], markers = {};
DATA.buildings.forEach(b => {
  L.circleMarker([b.lat, b.lng], {radius: 7, color: '#222', weight: 2, fillColor: b.color, fillOpacity: 1})
    .addTo(map).bindPopup('<b>' + b.name + '</b><br>' + b.zone);
  if (b.name !== '普通教學館')
    L.marker([b.lat, b.lng], {icon: L.divIcon({className: 'bld',
      html: '<div>' + (b.name === '博雅教學館' ? '博雅／普通教學館' : b.name) + '</div>'})}).addTo(map);
  all.push([b.lat, b.lng]);
});
DATA.stations.forEach((s, i) => {
  markers[i] = L.circleMarker([s.lat, s.lng], {radius: 9, color: '#fff', weight: 2, fillColor: s.color, fillOpacity: 0.9})
    .addTo(map).bindTooltip(s.name + '（' + s.dist + ' 公尺）')
    .bindPopup('<b>' + s.name + '</b><br>區域：' + s.zone + '<br>總車位：' + s.total +
               '<br>目前可借：' + s.rent + '　可還：' + s.ret);
  all.push([s.lat, s.lng]);
});
map.fitBounds(all, {padding: [40, 40]});

document.getElementById('nSt').textContent = DATA.stations.length;
document.getElementById('nBld').textContent = DATA.buildings.length;
document.getElementById('nZone').textContent = DATA.zones.length;
document.getElementById('upd').textContent = DATA.updated;
document.getElementById('zones').innerHTML = DATA.zones.map(z => {
  const blds = DATA.buildings.filter(b => b.zone === z.name).map(b => b.name).join('、');
  const sts = DATA.stations.map((s, i) => [s, i]).filter(([s]) => s.zone === z.name);
  return '<div class="zone"><h2><span class="dot" style="background:' + z.color + '"></span>' + z.name + '</h2>' +
    '<div class="label">建築物</div><div class="blds">' + blds + '</div>' +
    '<div class="label">YouBike 站（' + sts.length + '）</div><ul>' +
    sts.map(([s, i]) => '<li class="st" tabindex="0" data-i="' + i + '"><span>' + s.name +
      '</span><small>' + s.dist + ' m · ' + s.total + ' 位</small></li>').join('') + '</ul></div>';
}).join('');
document.querySelectorAll('li.st').forEach(li => {
  const go = () => { const m = markers[li.dataset.i]; map.setView(m.getLatLng(), 18); m.openPopup(); };
  li.addEventListener('click', go);
  li.addEventListener('keydown', e => { if (e.key === 'Enter') go(); });
});
</script></body></html>"""


def main():
    with open(MAP_FILE, encoding="utf-8-sig") as f:
        mapping = list(csv.DictReader(f))
    live = {s["sno"]: s for s in fetch_stations()}

    stations = []
    for row in mapping:
        s = live.get(row["站號"])
        if not s:
            print("找不到站點：", row["站名"])
            continue
        zone = row["區域"]
        stations.append({"name": s["name"], "zone": zone, "dist": row["距離(公尺)"],
                         "lat": s["lat"], "lng": s["lng"], "total": s["total"],
                         "rent": s["rent"], "ret": s["return"], "color": COLORS.get(zone, "#555")})

    buildings = [{"name": b, "zone": z, "lat": lat, "lng": lng, "color": COLORS.get(z, "#555")}
                 for z, blds in ZONES.items() for b, (lat, lng) in blds.items()]
    zones = [{"name": z, "color": COLORS.get(z, "#555")} for z in ZONES]

    updated = datetime.now().strftime("%m/%d %H:%M")
    data = json.dumps({"stations": stations, "buildings": buildings, "zones": zones, "updated": updated}, ensure_ascii=False)
    OUTPUT_DIR.mkdir(exist_ok=True)
    out = OUTPUT_DIR / "ntu_youbike_map.html"
    out.write_text(HTML.replace("__DATA__", data), encoding="utf-8")
    print(f"已產生 {out.resolve()}，正在用瀏覽器打開...")
    webbrowser.open(out.resolve().as_uri())


if __name__ == "__main__":
    main()
