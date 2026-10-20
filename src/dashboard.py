"""
台大 YouBike 擁擠預測：整合網頁
------------------------------------------------
把「預測查詢」「站點地圖」「驗證結果」做成一個網頁 output/dashboard.html，
執行後會自動用瀏覽器打開。資料更新後（例如多收了幾天 YouBike 資料）重跑一次即可。

用法：
  python dashboard.py                      # 產生網頁並用瀏覽器打開
  python dashboard.py --publish --no-open  # 同時更新網站首頁 index.html、不開瀏覽器（雲端每天自動執行）
需要網路（抓站點位置與地圖底圖）。只用到 Python 內建套件。
"""

import csv
import json
import os
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

import net_flow as nf
import validate as va
from periods import PERIODS, ORDER, SEMESTER_START, LAST_WEEK, SPECIAL_WEEKS, day_type

ROOT = Path(nf._ROOT)
SERIES_STEP = 6        # 網頁裡的車數記錄每幾分鐘留一筆
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"

COLORS = {"博雅普通區": "#d9480f", "共同教學館": "#1971c2", "新生教學館": "#2f9e44",
          "綜合體育館": "#9c36b5", "總圖區": "#c2255c"}

# 建築物座標（Google 地圖）
BUILDINGS = {
    "博雅普通區": {"博雅教學館": (25.01884, 121.53670), "普通教學館": (25.01856, 121.53672)},
    "共同教學館": {"共同教學館": (25.01585, 121.53757)},
    "新生教學館": {"新生教學館": (25.01974, 121.53847)},
    "綜合體育館": {"綜合體育館": (25.02169, 121.53512)},
    "總圖區": {"總圖書館": (25.01734, 121.54057), "農藝館": (25.01828, 121.54081),
             "綜合教學館": (25.01824, 121.53950), "第一學生活動中心": (25.01776, 121.54009)},
}


def load_stations():
    """讀 stations_map.csv，再從 YouBike API 補上座標和目前車數；抓不到就只回傳站名"""
    rows = []
    with open(DATA_DIR / "stations_map.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    live = {}
    try:
        from youbike_collector import fetch_stations
        live = {s["sno"]: s for s in fetch_stations()}
    except Exception as e:
        print(f"（抓不到 YouBike 即時資料，地圖上不會顯示站點：{e}）")
    out = []
    for r in rows:
        s = live.get(r["站號"])
        out.append({"sno": r["站號"], "name": r["站名"], "zone": r["區域"], "dist": int(r["距離(公尺)"]),
                    "lat": s["lat"] if s else None, "lng": s["lng"] if s else None,
                    "total": s["total"] if s else None, "rent": s["rent"] if s else None,
                    "ret": s["return"] if s else None})
    return out


def build_data():
    courses = nf.load_courses()
    # 每一週一張表（半學期課只算有上的週），門檻每區各自排名
    tables, ths = {}, {}
    for w in range(1, LAST_WEEK + 1):
        table = nf.build_table(courses, w)
        tables[w] = {f"{z}|{d}|{p}": list(v) for (z, d, p), v in table.items()}
        ths[w] = {z: list(t) for z, t in nf.thresholds(table).items()}
    valid, corrs = {}, {}
    dates = []
    for m in va.MARGINS:
        rows, status, dates = va.compute(m)
        valid[str(m)] = rows
        per_zone, pooled = va.correlations(rows)
        corrs[str(m)] = {"zones": per_zone, "pooled": pooled}

    # 每個時段的課程明細（查詢時顯示是哪些課造成的）；最後一欄是上課週次，網頁上再依週次篩選
    detail = {}
    for c in courses:
        for key, kind in [((c["區域"], c["星期"], c["開始節次"]), "到"),
                          ((c["區域"], c["星期"], nf.next_period(c["結束節次"])), "走")]:
            if key[2] is None:
                continue
            k = "|".join(map(str, key))
            detail.setdefault(k, []).append([kind, c["課名"], c["人數"], sorted(c["週次"]) if c["週次"] else None])
    for k in detail:
        detail[k].sort(key=lambda x: -x[2])

    status = va.load_zone_status(va.load_station_zones()) if va.has_log() else {}
    # 網頁只放每 6 分鐘一筆（夠畫圖和查歷史），不然收一學期後網頁會太大
    series = {}
    for z, st in status.items():
        seen = set()
        for t, v in sorted(st.items()):
            bucket = (t.date(), (t.hour * 60 + t.minute) // SERIES_STEP)
            if bucket not in seen:
                seen.add(bucket)
                series.setdefault(z, []).append([t.strftime("%Y-%m-%d %H:%M"), v[0], v[1]])
    return {
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "zones": nf.ZONES, "colors": COLORS, "order": ORDER, "periods": PERIODS,
        "tables": tables, "th": ths, "curWeek": nf.current_week(), "lastWeek": LAST_WEEK,
        "semStart": SEMESTER_START.isoformat(), "specialWeeks": SPECIAL_WEEKS, "near": nf.NEAR,
        "classDays": [d.isoformat() for d in dates if day_type(d)[0]],
        "dayNotes": {d.isoformat(): day_type(d)[1] for d in dates if day_type(d)[1]},
        "corr": corrs,
        "detail": detail,
        "stations": load_stations(),
        "buildings": [{"name": b, "zone": z, "lat": lat, "lng": lng}
                      for z, blds in BUILDINGS.items() for b, (lat, lng) in blds.items()],
        "nCourses": len(courses),
        "validation": valid,
        "margins": [str(m) for m in va.MARGINS],
        "series": series,
        "dates": [d.isoformat() for d in dates],
    }


HTML = r"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>台大 YouBike 擁擠預測</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
:root{--bg:#f3f6f4;--paper:#fff;--ink:#17201c;--muted:#5b6762;--line:#dbe2de;--accent:#0d6b57;--soft:#e2efea;
  --full:#d9480f;--empty:#1f55c7;--ok:#8a9691;--good:#1f7a4a;--bad:#b3261e}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Microsoft JhengHei","PingFang TC","Noto Sans TC",system-ui,sans-serif;font-size:15px;line-height:1.6}
header{background:var(--paper);border-bottom:1px solid var(--line);padding:16px max(16px,4vw) 0}
header h1{margin:0;font-size:22px}
header p{margin:4px 0 12px;color:var(--muted);font-size:13.5px}
nav{display:flex;gap:4px;flex-wrap:wrap}
nav button{font:inherit;border:0;background:none;padding:10px 16px;border-bottom:3px solid transparent;cursor:pointer;color:var(--muted);font-weight:700}
nav button.on{color:var(--accent);border-bottom-color:var(--accent)}
main{padding:20px max(16px,4vw) 40px;max-width:1280px;margin:0 auto}
.tab{display:none}.tab.on{display:block}
.grid{display:grid;grid-template-columns:minmax(0,360px) minmax(0,1fr);gap:18px;align-items:start}
@media(max-width:900px){.grid{grid-template-columns:minmax(0,1fr)}}
.card{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:18px;min-width:0}
.card h2{margin:0 0 10px;font-size:17px}
.muted{color:var(--muted)} .small{font-size:13px}
label{display:block;font-size:12.5px;color:var(--muted);margin:8px 0 3px}
select,input{font:inherit;width:100%;padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:#fff;color:var(--ink)}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.btn{font:inherit;margin-top:12px;width:100%;padding:10px;border:0;border-radius:8px;background:var(--accent);color:#fff;font-weight:700;cursor:pointer}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.chips button{font:inherit;font-size:12.5px;border:1px solid var(--line);background:#fff;border-radius:999px;padding:3px 10px;cursor:pointer}
.result{margin-top:16px;border-top:1px solid var(--line);padding-top:14px}
.pill{display:inline-block;color:#fff;font-weight:700;padding:3px 14px;border-radius:999px;font-size:17px}
.pill.難借{background:var(--empty)}.pill.難還{background:var(--full)}.pill.正常{background:var(--ok)}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:12px 0}
.stat{background:var(--bg);border-radius:8px;padding:8px 10px}
.stat b{display:block;font-size:20px;font-variant-numeric:tabular-nums}
.stat span{font-size:12px;color:var(--muted)}
.courses{margin:6px 0 0;padding-left:18px;font-size:13px}
.heatwrap{overflow-x:auto}
table.heat{border-collapse:separate;border-spacing:3px;min-width:640px}
.heat th{font-size:11.5px;color:var(--muted);font-weight:400;padding:0 2px}
.heat th.d{text-align:right;padding-right:6px;font-size:13px;white-space:nowrap}
.cell{width:100%;min-width:44px;height:38px;border:2px solid transparent;border-radius:6px;font:12px ui-monospace,Consolas,monospace;cursor:pointer;color:var(--ink)}
.cell.sel{border-color:var(--ink)}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12.5px;color:var(--muted);margin:6px 0}
.legend i{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:5px;vertical-align:-1px}
#mapgrid{display:grid;grid-template-columns:320px minmax(0,1fr);gap:0;height:72vh;min-height:480px;background:var(--paper);border:1px solid var(--line);border-radius:12px;overflow:hidden}
@media(max-width:900px){#mapgrid{grid-template-columns:minmax(0,1fr);height:auto}#map{height:60vh}}
#side{overflow-y:auto;padding:16px;border-right:1px solid var(--line);background:#f8faf9}
#map{min-height:400px}
.zone{background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin-bottom:10px}
.zone h3{margin:0 0 4px;font-size:14.5px;display:flex;gap:8px;align-items:center}
.dot{display:inline-block;width:11px;height:11px;border-radius:50%;flex:none}
.lab{font-size:11.5px;color:var(--muted);margin-top:6px}
ul.st{list-style:none;margin:2px 0 0;padding:0}
ul.st li{display:flex;justify-content:space-between;gap:8px;font-size:13px;padding:3px 6px;border-radius:6px;cursor:pointer}
ul.st li:hover{background:var(--soft)}
ul.st small{color:var(--muted);white-space:nowrap}
.bld{background:none;border:none}
.bld div{background:#222;color:#fff;font-size:12px;padding:2px 6px;border-radius:4px;white-space:nowrap;transform:translate(-50%,-140%);display:inline-block}
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:18px}
@media(max-width:800px){.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}}
.kpi b{display:block;font-size:26px;font-variant-numeric:tabular-nums}
.kpi span{font-size:13px;color:var(--muted)}
.bars div{display:grid;grid-template-columns:100px 1fr 70px;gap:8px;align-items:center;font-size:13px;margin:5px 0}
.bar{height:10px;background:var(--bg);border-radius:5px;overflow:hidden}.bar i{display:block;height:100%;background:var(--good)}
svg text{font-family:inherit}
.tbl{overflow-x:auto}
table.v{border-collapse:collapse;width:100%;font-size:13px;min-width:640px}
.v th,.v td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);font-variant-numeric:tabular-nums}
.v th{color:var(--muted);font-weight:400;font-size:12px}
.hit{color:var(--good);font-weight:700}.miss{color:var(--bad);font-weight:700}
.empty{padding:30px;text-align:center;color:var(--muted)}
footer{font-size:12.5px;color:var(--muted);padding:0 max(16px,4vw) 24px;max-width:1280px;margin:0 auto}
</style></head><body>
<header>
  <h1>台大 YouBike 擁擠預測</h1>
  <p id="sub"></p>
  <nav>
    <button data-tab="predict" class="on">預測查詢</button>
    <button data-tab="map">站點地圖</button>
    <button data-tab="valid">驗證結果</button>
  </nav>
</header>
<main>
  <!-- 預測 -->
  <section class="tab on" id="tab-predict">
    <div class="grid">
      <div class="card">
        <h2>什麼時候好借、好還？</h2>
        <form id="q">
          <div class="row2">
            <div><label for="zone">區域</label><select id="zone"></select></div>
            <div><label for="week">週次</label><select id="week"></select></div>
          </div>
          <div class="row2">
            <div><label for="day">星期</label><select id="day"></select></div>
            <div><label for="time">時間</label><input id="time" type="time" value="12:15"></div>
          </div>
          <button class="btn" type="submit">預測</button>
        </form>
        <div class="chips">
          <button data-ex="博雅普通區,4,12:15">週四 12:15 博雅</button>
          <button data-ex="博雅普通區,4,10:15">週四 10:15 博雅</button>
          <button data-ex="總圖區,2,10:15">週二 10:15 總圖</button>
        </div>
        <div class="result" id="result"></div>
      </div>
      <div class="card">
        <h2 id="heatTitle">一週熱度圖</h2>
        <p class="small muted" style="margin:0">每格是一段下課交換時間，數字是淨流量（來上課 − 下課離開的人數）。點一格可以查詢；上課中的時間會沿用最近一次下課的狀態。</p>
        <div class="legend"><span><i style="background:var(--full)"></i>難還（車會變多）</span><span><i style="background:var(--empty)"></i>難借（車會變少）</span><span><i style="background:#e7ecea"></i>正常</span></div>
        <div class="heatwrap"><table class="heat" id="heat"></table></div>
      </div>
    </div>
  </section>

  <!-- 地圖 -->
  <section class="tab" id="tab-map">
    <div id="mapgrid">
      <aside id="side">
        <h2 style="margin:0 0 4px;font-size:17px">目前已收錄的站點與建築物</h2>
        <p class="small muted" style="margin:0 0 10px">YouBike 站依距離分到 5 個區域，點站名可以在地圖上找到它。車數是產生網頁當下的狀態。</p>
        <div id="zones"></div>
      </aside>
      <div id="map"></div>
    </div>
  </section>

  <!-- 驗證 -->
  <section class="tab" id="tab-valid">
    <div id="validBody"></div>
  </section>
</main>
<footer id="foot"></footer>

<script>
const D = __DATA__;
const WD = {1:"一",2:"二",3:"三",4:"四",5:"五",6:"六",7:"日"};
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const toMin = s => { const [h,m] = s.split(":").map(Number); return h*60+m; };
const fmt = m => String(Math.floor(m/60)).padStart(2,"0")+":"+String(m%60).padStart(2,"0");
const SLOTS = D.order.slice(1);
const prevOf = p => D.order[D.order.indexOf(p)-1];
const win = p => [D.periods[prevOf(p)][1], D.periods[p][0]];
/* 每區各自排名的門檻；w＝第幾週 */
function judge(z,n,w){ const [hi,lo]=D.th[w][z]; if(n>=hi && n>0) return "難還"; if(n<=lo && n<0) return "難借"; return "正常"; }
const T = (w,z,d,p) => D.tables[w][`${z}|${d}|${p}`];
const weekOfDate = s => { const w=Math.floor((new Date(s+"T12:00")-new Date(D.semStart+"T12:00"))/864e5/7)+1; return w>=1&&w<=D.lastWeek?w:null; };
const curW = () => +$("week").value;
function timeToPeriod(hhmm){ const t=toMin(hhmm); let best=null,gap=1e9;
  for(const p of SLOTS){ const g=Math.abs(t-toMin(D.periods[p][0])); if(g<gap){gap=g;best=p;} } return gap<=20?best:null; }

$("sub").textContent = `依台大 115-1 學期課表（${D.nCourses} 個上課時段，人數採課程人數上限）推算 5 區的借還擁擠程度。網頁產生時間：${D.generated}`;
$("foot").textContent = `人數為課程人數上限；假設騎 YouBike 的比例各時段相同，因此每一區各自用全週排名判斷：該區淨流量排名前 20% 為難還、後 20% 為難借。半學期課只算在有上課的週。有歷史資料時，過去同時段平均剩 ${D.near} 台（空位）以下會直接判為難借（難還）。YouBike 資料來源：臺北市政府 YouBike 2.0 即時資訊。`;

/* 分頁 */
let mapReady=false;
document.querySelectorAll("nav button").forEach(b=>b.onclick=()=>{
  document.querySelectorAll("nav button").forEach(x=>x.classList.toggle("on",x===b));
  document.querySelectorAll(".tab").forEach(t=>t.classList.toggle("on",t.id==="tab-"+b.dataset.tab));
  if(b.dataset.tab==="map"){ if(!mapReady) initMap(); else setTimeout(()=>map.invalidateSize(),50); }
});

/* ---------- 預測查詢 ---------- */
D.zones.forEach(z=>$("zone").insertAdjacentHTML("beforeend",`<option>${z}</option>`));
[1,2,3,4,5].forEach(d=>$("day").insertAdjacentHTML("beforeend",`<option value="${d}">星期${WD[d]}</option>`));
for(let w=1;w<=D.lastWeek;w++) $("week").insertAdjacentHTML("beforeend",`<option value="${w}">第 ${w} 週${w===D.curWeek?"（本週）":""}${D.specialWeeks[w]?"・"+D.specialWeeks[w]:""}</option>`);
$("week").value=D.curWeek;
function latestPeriod(hhmm){ const t=toMin(hhmm); if(t>toMin(D.periods[D.order[D.order.length-1]][1])) return null;
  let last=null; for(const p of SLOTS){ if(toMin(D.periods[p][0])<=t) last=p; } return last; }
const CLASS_DAYS=new Set(D.classDays);
function historyAt(z,d,hhmm){ const t=toMin(hhmm), byDate={};
  for(const [ts,rent,ret] of (D.series[z]||[])){ if(!CLASS_DAYS.has(ts.slice(0,10))) continue;
    const dt=new Date(ts.slice(0,10)+"T12:00"); const wd=dt.getDay()||7; if(wd!==d) continue;
    const g=Math.abs(toMin(ts.slice(11,16))-t); const day=ts.slice(0,10); if(g<=10&&(!byDate[day]||g<byDate[day][0])) byDate[day]=[g,rent,ret]; }
  const v=Object.values(byDate); if(!v.length) return null;
  return [v.reduce((s,x)=>s+x[1],0)/v.length, v.reduce((s,x)=>s+x[2],0)/v.length, v.length]; }
/* 結合課表和歷史：歷史平均剩 near 台（空位）以下就直接判難借（難還），否則用課表 */
function combine(lv,h){
  if(h&&h[0]<=D.near) return [ "難借", `歷史資料：過去 ${h[2]} 天這時平均只剩 ${h[0].toFixed(1)} 台` ];
  if(h&&h[1]<=D.near) return [ "難還", `歷史資料：過去 ${h[2]} 天這時平均只剩 ${h[1].toFixed(1)} 個空位` ];
  return [lv,"課表預測"];
}
function predict(){
  const z=$("zone").value, d=+$("day").value, t=$("time").value||"12:15", w=curW();
  let p=timeToPeriod(t); const inClass=!p; if(inClass) p=latestPeriod(t);
  const h=historyAt(z,d,t);
  const hist=h?`<p class="small" style="margin:10px 0 0"><b>歷史資料</b>：過去 ${h[2]} 個星期${WD[d]}（上課日）的這個時間，平均可借 <b>${h[0].toFixed(0)}</b> 台、可還 <b>${h[1].toFixed(0)}</b> 位${h[2]<3?"（天數少，僅供參考）":""}</p>`
              :`<p class="small muted" style="margin:10px 0 0">歷史資料：這個時間還沒有收集到記錄</p>`;
  if(!p){ const [lv,why]=combine("正常",h);
    $("result").innerHTML=`<span class="pill ${h?lv:"正常"}">${h?lv:"無法預測"}</span><p>${z}　星期${WD[d]} ${t}：不在課表涵蓋的時間（第 1 節前或 22:00 後）${h?"，依歷史資料判斷":""}。</p>${hist}`; drawHeat(z,d,null); return; }
  const [a,l,n]=T(w,z,d,p); const slv=judge(z,n,w); const [lv,why]=combine(slv,h); const [s,e]=win(p);
  const tip={難借:"車會被借光，建議提早出門，或走到附近其他區的站借車。",難還:"車位會停滿，建議提早到，或停在附近其他區的站。",正常:"來的人和走的人差不多，借還應該都沒問題。"}[lv];
  const det=(D.detail[`${z}|${d}|${p}`]||[]).filter(x=>!x[3]||x[3].includes(w));
  const li=k=>det.filter(x=>x[0]===k).slice(0,12).map(x=>`<li>${esc(x[1])}（${x[2]} 人${x[3]?"，只上第 "+x[3][0]+"–"+x[3][x[3].length-1]+" 週":""}）</li>`).join("")||"<li class='muted'>無</li>";
  const when=inClass?`上課中，沿用最近一次下課（${s}–${e}）的狀態`:`${s}–${e} 下課，第 ${p} 節開始前`;
  $("result").innerHTML=`<span class="pill ${lv}">${lv}</span>
    <p class="small muted" style="margin:6px 0 0">${z}　第 ${w} 週星期${WD[d]} ${t}（${when}）</p>
    <p class="small" style="margin:4px 0 0">課表預測：<b>${slv}</b>　判斷依據：${why}</p>
    <div class="stats"><div class="stat"><b>${a}</b><span>來上課</span></div><div class="stat"><b>${l}</b><span>下課離開</span></div><div class="stat"><b>${n>0?"+":""}${n}</b><span>淨流量</span></div></div>
    <p style="margin:0">${tip}</p>${hist}
    <details style="margin-top:10px"><summary class="small">是哪些課造成的</summary>
      <p class="small" style="margin:8px 0 0"><b>這時開始上課</b></p><ul class="courses">${li("到")}</ul>
      <p class="small" style="margin:8px 0 0"><b>這時剛下課</b></p><ul class="courses">${li("走")}</ul></details>`;
  drawHeat(z,d,p);
}
function drawHeat(z,selD,selP){
  const w=curW();
  $("heatTitle").textContent=`一週熱度圖 · ${z} · 第 ${w} 週`;
  const maxAbs=Math.max(...Object.entries(D.tables[w]).filter(([k])=>k.startsWith(z+"|")).map(([,v])=>Math.abs(v[2])),1);
  let h="<thead><tr><th></th>"+SLOTS.map(p=>`<th>${win(p)[1]}</th>`).join("")+"</tr></thead><tbody>";
  for(let d=1;d<=5;d++){
    h+=`<tr><th class="d">週${WD[d]}</th>`;
    for(const p of SLOTS){
      const [a,l,n]=T(w,z,d,p); const lv=judge(z,n,w);
      const col=n>0?"var(--full)":"var(--empty)";
      const pct=n===0?0:Math.round(Math.min(1,Math.abs(n)/maxAbs)*(lv==="正常"?30:85))+(lv==="正常"?6:15);
      const bg=n===0?"#f3f5f4":`color-mix(in srgb, ${col} ${pct}%, white)`;
      const dark=lv!=="正常"&&pct>55;
      h+=`<td><button class="cell${d===selD&&p===selP?" sel":""}" data-d="${d}" data-p="${p}" title="週${WD[d]} ${win(p).join("–")}：到 ${a}、走 ${l}，${lv}" style="background:${bg};${dark?"color:#fff;font-weight:700":""}">${n===0?"·":(n>0?"+":"")+n}</button></td>`;
    }
    h+="</tr>";
  }
  $("heat").innerHTML=h+"</tbody>";
}
$("heat").onclick=e=>{const c=e.target.closest(".cell"); if(!c)return; $("day").value=c.dataset.d; $("time").value=fmt(toMin(D.periods[c.dataset.p][0])-5); predict();};
$("q").onsubmit=e=>{e.preventDefault();predict();};
["zone","day","time","week"].forEach(id=>$(id).onchange=predict);
document.querySelectorAll("[data-ex]").forEach(b=>b.onclick=()=>{const [z,d,t]=b.dataset.ex.split(",");$("zone").value=z;$("day").value=d;$("time").value=t;predict();});
predict();

/* ---------- 地圖 ---------- */
let map;
function initMap(){
  mapReady=true;
  map=L.map("map").setView([25.0185,121.5385],16);
  L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",{maxZoom:19,attribution:"Tiles &copy; Esri"}).addTo(map);
  const pts=[],mk={};
  D.buildings.forEach(b=>{
    L.circleMarker([b.lat,b.lng],{radius:7,color:"#222",weight:2,fillColor:D.colors[b.zone],fillOpacity:1}).addTo(map).bindPopup(`<b>${b.name}</b><br>${b.zone}`);
    if(b.name!=="普通教學館") L.marker([b.lat,b.lng],{icon:L.divIcon({className:"bld",html:`<div>${b.name==="博雅教學館"?"博雅／普通教學館":b.name}</div>`})}).addTo(map);
    pts.push([b.lat,b.lng]);
  });
  D.stations.forEach((s,i)=>{ if(s.lat==null) return;
    mk[i]=L.circleMarker([s.lat,s.lng],{radius:9,color:"#fff",weight:2,fillColor:D.colors[s.zone],fillOpacity:.9}).addTo(map)
      .bindTooltip(`${s.name}（${s.dist} 公尺）`).bindPopup(`<b>${s.name}</b><br>區域：${s.zone}<br>總車位：${s.total}<br>可借：${s.rent}　可還：${s.ret}`);
    pts.push([s.lat,s.lng]);
  });
  map.fitBounds(pts,{padding:[30,30]});
  $("zones").innerHTML=D.zones.map(z=>{
    const bl=D.buildings.filter(b=>b.zone===z).map(b=>b.name).join("、");
    const st=D.stations.map((s,i)=>[s,i]).filter(([s])=>s.zone===z);
    return `<div class="zone"><h3><span class="dot" style="background:${D.colors[z]}"></span>${z}</h3>
      <div class="lab">建築物</div><div class="small">${bl}</div>
      <div class="lab">YouBike 站（${st.length}）</div><ul class="st">${st.map(([s,i])=>`<li data-i="${i}"><span>${s.name}</span><small>${s.dist} m${s.total!=null?" · "+s.total+" 位":""}</small></li>`).join("")}</ul></div>`;
  }).join("");
  document.querySelectorAll("ul.st li").forEach(li=>li.onclick=()=>{const m=mk[li.dataset.i]; if(m){map.setView(m.getLatLng(),18); m.openPopup();}});
}

/* ---------- 驗證 ---------- */
let MARGIN=D.margins[0];
function renderValid(){
  const R=D.validation[MARGIN]||[], box=$("validBody");
  const nDays=D.dates.length, cdays=D.classDays.length;
  if(!R.length){ box.innerHTML=`<div class="card empty">目前收到 ${nDays} 天的 YouBike 資料，其中正常上課日 ${cdays} 天，還對不上任何下課時段。<br>上課日白天收集幾個小時後，重新執行 <b>python dashboard.py</b> 就會出現驗證結果。</div>`; return; }
  const pick=lv=>R.filter(r=>r["預測"]===lv);
  const pct=(k,n)=>n?Math.round(k/n*100):null;
  /* Wilson 95% 信賴區間 */
  const ci=(k,n)=>{ if(!n) return ""; const z=1.96,p=k/n,d=1+z*z/n,c=p+z*z/(2*n),r=z*Math.sqrt(p*(1-p)/n+z*z/(4*n*n)); return `${Math.round((c-r)/d*100)}～${Math.round((c+r)/d*100)}%`; };
  const cnt=(a,key)=>a.filter(r=>r[key]).length;
  const rate=a=>pct(a.filter(r=>r["結果"]==="符合").length,a.length);
  const avg=a=>a.length?(a.reduce((s,r)=>s+r["車數變化"],0)/a.length):0;
  const B=pick("難借"),H=pick("難還"),N=pick("正常"),judged=R.filter(r=>r["結果"]);
  const C=D.corr[MARGIN]||{zones:{},pooled:null}, f2=v=>v==null?"—":v.toFixed(2);
  const kB=cnt(B,"車變少或借光"), kH=cnt(H,"車變多或停滿"), nB=cnt(N,"車變少或借光"), nH=cnt(N,"車變多或停滿");
  box.innerHTML=`
  <div class="chips" style="margin:0 0 14px">${D.margins.map(m=>`<button data-m="${m}" style="${m===MARGIN?"background:var(--accent);color:#fff;border-color:var(--accent)":""}">下課前後 ${m} 分鐘</button>`).join("")}</div>
  <div class="kpis">
    <div class="card kpi"><b>${rate(judged)??"—"}%</b><span>整體命中率（${judged.length} 個難借／難還時段）</span></div>
    <div class="card kpi"><b>${pct(kB,B.length)??"—"}%</b><span>預測難借，車真的變少或剩 ≤ ${D.near} 台（${kB}/${B.length}，95% 區間 ${ci(kB,B.length)}）<br>比較基準：正常時段也這樣的比例 ${pct(nB,N.length)??"—"}%（${ci(nB,N.length)}）</span></div>
    <div class="card kpi"><b>${pct(kH,H.length)??"—"}%</b><span>預測難還，車真的變多或空位 ≤ ${D.near}（${kH}/${H.length}，95% 區間 ${ci(kH,H.length)}）<br>比較基準：正常時段也這樣的比例 ${pct(nH,N.length)??"—"}%（${ci(nH,N.length)}）</span></div>
    <div class="card kpi"><b>${f2(C.pooled)}</b><span>淨流量與車數變化的相關係數（各區標準化後合併，越接近 1 越準）</span></div>
  </div>
  <p class="small muted" style="margin:-6px 0 16px">資料期間 ${D.dates[0]} ～ ${D.dates[D.dates.length-1]}（正常上課日 ${cdays} 天；週末、放假、停課不算），共比對 ${R.length} 個下課時段。每區的車數是區內所有站加總，比較「下課前 ${MARGIN} 分鐘」到「上課後 ${MARGIN} 分鐘」這段期間。命中率要明顯高於比較基準，預測才算有用；區間很寬代表樣本還不夠。</p>
  <div class="grid" style="grid-template-columns:minmax(0,340px) minmax(0,1fr)">
    <div class="card"><h2>各區命中率</h2><div class="bars">${D.zones.map(z=>{const a=judged.filter(r=>r["區域"]===z);const r=rate(a);return `<div><span>${z}</span><span class="bar"><i style="width:${r??0}%;background:${D.colors[z]}"></i></span><span class="small">${r==null?"無資料":r+"%（"+a.length+"）"}</span></div>`;}).join("")}</div>
      <p class="small muted" style="margin:10px 0 0">各區相關係數：${D.zones.map(z=>`${z} ${f2(C.zones[z])}`).join("、")}</p></div>
    <div class="card"><h2>某一天的車數變化</h2>
      <div class="row2"><div><label for="vz">區域</label><select id="vz">${D.zones.map(z=>`<option>${z}</option>`).join("")}</select></div>
      <div><label for="vd">日期</label><select id="vd">${D.dates.map(d=>`<option value="${d}">${d}${D.dayNotes[d]?"（"+D.dayNotes[d]+"）":""}</option>`).join("")}</select></div></div>
      <div class="legend" style="margin-top:10px"><span><i style="background:var(--empty);opacity:.35"></i>預測難借的時段</span><span><i style="background:var(--full);opacity:.35"></i>預測難還的時段</span></div>
      <div id="chart"></div></div>
  </div>
  <div class="card" style="margin-top:18px"><h2>車數變化最大的時段</h2><div class="tbl"><table class="v"><thead><tr><th>日期</th><th>區域</th><th>時段</th><th>預測</th><th>淨流量</th><th>車數（前 → 後）</th><th>期間最低～最高</th><th>變化</th><th>說明</th><th>結果</th></tr></thead><tbody>
  ${[...R].sort((a,b)=>Math.abs(b["車數變化"])-Math.abs(a["車數變化"])).slice(0,15).map(r=>`<tr><td>${r["日期"]}（${WD[r["星期"]]}）</td><td>${r["區域"]}</td><td>${r["時段"]}</td><td>${r["預測"]}</td><td>${r["淨流量"]>0?"+":""}${r["淨流量"]}</td><td>${r["之前車數"]} → ${r["之後車數"]}</td><td>${r["期間最低"]}～${r["期間最高"]}</td><td>${r["車數變化"]>0?"+":""}${r["車數變化"]}</td><td>${r["說明"]||""}${r["下雨"]===1?" 下雨":""}</td><td class="${r["結果"]==="符合"?"hit":r["結果"]?"miss":""}">${r["結果"]||"—"}</td></tr>`).join("")}
  </tbody></table></div></div>`;
  if(D.classDays.length) $("vd").value=D.classDays[D.classDays.length-1];
  box.querySelectorAll("[data-m]").forEach(b=>b.onclick=()=>{const z=$("vz").value,d=$("vd").value;MARGIN=b.dataset.m;renderValid();$("vz").value=z;$("vd").value=d;drawChart();});
  $("vz").onchange=$("vd").onchange=drawChart; drawChart();
}
function drawChart(){
  const z=$("vz").value, day=$("vd").value, pts=(D.series[z]||[]).filter(p=>p[0].startsWith(day)).map(p=>[toMin(p[0].slice(11)),p[1]]);
  const M=+MARGIN, W=720,H=260,L=40,Rr=26,T0=12,Bm=28, x0=7*60,x1=22*60;
  if(!pts.length){$("chart").innerHTML="<p class='muted small'>這一天這一區沒有記錄。</p>";return;}
  const vmax=Math.max(...pts.map(p=>p[1]))*1.1||10, X=m=>L+(m-x0)/(x1-x0)*(W-L-Rr), Y=v=>T0+(1-v/vmax)*(H-T0-Bm);
  const wdN=new Date(day+"T12:00").getDay(), wk=weekOfDate(day);
  let s=`<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto;display:block">`;
  if(CLASS_DAYS.has(day)&&wk) for(const p of SLOTS){const lv=judge(z,T(wk,z,wdN,p)[2],wk); if(lv==="正常")continue; const [a,b]=win(p);
    s+=`<rect x="${X(toMin(a)-M)}" y="${T0}" width="${X(toMin(b)+M)-X(toMin(a)-M)}" height="${H-T0-Bm}" fill="${lv==="難借"?"#1f55c7":"#d9480f"}" opacity=".16"/>`;}
  if(D.near) s+=`<line x1="${L}" x2="${W-Rr}" y1="${Y(D.near)}" y2="${Y(D.near)}" stroke="#b3261e" stroke-dasharray="4 3"/>`;
  for(let i=0;i<=4;i++){const v=Math.round(vmax*i/4); s+=`<line x1="${L}" x2="${W-Rr}" y1="${Y(v)}" y2="${Y(v)}" stroke="#e3e8e5"/><text x="${L-6}" y="${Y(v)+4}" font-size="11" text-anchor="end" fill="#5b6762">${v}</text>`;}
  for(let h=8;h<=22;h+=2) s+=`<text x="${X(h*60)}" y="${H-8}" font-size="11" text-anchor="middle" fill="#5b6762">${h}:00</text>`;
  s+=`<polyline fill="none" stroke="${D.colors[z]}" stroke-width="2.2" points="${pts.filter(p=>p[0]>=x0&&p[0]<=x1).map(p=>X(p[0])+","+Y(p[1])).join(" ")}"/>`;
  s+=`<text x="${L}" y="${T0+2}" font-size="11" fill="#5b6762" dy="-2">可借車數（台）${CLASS_DAYS.has(day)?"":"　※這天不是正常上課日"}</text></svg>`;
  $("chart").innerHTML=s;
}
renderValid();
</script></body></html>"""


def main():
    data = build_data()
    OUTPUT_DIR.mkdir(exist_ok=True)
    out = OUTPUT_DIR / "dashboard.html"
    data_js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")   # 避免資料裡的 </ 提早結束 <script>
    out.write_text(HTML.replace("__DATA__", data_js), encoding="utf-8")
    n = "、".join(f"前後 {m} 分鐘 {len(r)} 個" for m, r in data["validation"].items())
    print(f"已產生 {out}")
    print(f"  站點 {len(data['stations'])} 個、YouBike 記錄 {len(data['dates'])} 天、驗證時段：{n}")
    if "--publish" in sys.argv:          # 同時更新網站首頁（GitHub Pages 用專案最外層的 index.html）
        (ROOT / "index.html").write_text(HTML.replace("__DATA__", data_js), encoding="utf-8")
        print(f"  已更新網站首頁 {ROOT / 'index.html'}")
    if "--no-open" not in sys.argv:
        webbrowser.open(out.resolve().as_uri())


if __name__ == "__main__":
    main()
