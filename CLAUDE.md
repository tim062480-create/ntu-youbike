# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

這個 repo 有三個互相獨立的專案，都用 GitHub Pages 發布、用 GitHub Actions 自動抓資料。使用者用繁體中文溝通，文件、註解、commit 訊息也都用繁體中文。

| 專案 | 位置 | 網址 |
|---|---|---|
| 台大 YouBike 擁擠預測 | repo 根目錄（`src/`、`data/`、`index.html`） | https://tim062480-create.github.io/ntu-youbike/ |
| 附近抱石館地圖 | 全部在 `climbing/` | https://tim062480-create.github.io/ntu-youbike/climbing/ |
| 新聞資料專案 | 全部在 `news/`，規則見 `news/CLAUDE.md` | — |

各專案共用的只有 `.github/workflows/`（GitHub 規定的位置）。改其中一個專案時不要動到另一個的檔案。

## 共同慣例

- Python 只用內建套件（urllib、csv、json），沒有 requirements.txt、沒有測試框架、沒有 linter。要確認程式能跑就直接執行它。
- 各來源的欄位名稱常常不同，用 `get(d, *keys)` 依序嘗試多個欄位名稱（兩個專案都是這樣寫）。
- Actions 寫回 repo 的方式：`git add` → commit（沒變更就略過）→ `git pull --rebase` 再 push，失敗就重試。`collect.yml` 每 30 分鐘、`climbing-data.yml` 每 20 分鐘都會 commit 到 main，所以本機 push 前一定要先 pull。
- `schedule` 只在預設分支（main）上執行；開發分支上的 workflow 靠 `push` 觸發。
- 雲端開發環境的網路被限制，常連不到 YouBike、OpenStreetMap、Google 等網站；需要外部資料的步驟寫成程式交給 Actions 跑。

## 台大 YouBike 擁擠預測（根目錄）

詳細目標、方法、決策紀錄都在 `專案紀錄.md`，每次有修改或決定都要在它的「決策紀錄」「修改紀錄」加一條並註明日期。

指令（在 `src/` 執行）：

| 做什麼 | 指令 |
|---|---|
| 抓一次 YouBike 測試 | `python youbike_collector.py --once` |
| 文字版預測查詢 | `python net_flow.py`、`python net_flow.py --summary --week 9` |
| 驗證預測 | `python validate.py`（產生 `data/validation.csv`） |
| 產生網頁 | `python dashboard.py --publish --no-open`（`--publish` 會覆蓋根目錄 `index.html`） |
| 重新產生課表 CSV | `python fetch_courses.py 115-1 --from-json` |
| 更新天氣 | `python fetch_weather.py` |

資料流：`fetch_courses.py` 把課程網資料轉成 `data/courses_zones.csv`（5 區的課，含上課週次）→ `net_flow.py` 用課表算每個下課時段的淨流量並分級（每區各自排名，有歷史資料時用同星期同時段的平均車數覆蓋）→ `validate.py` 拿 `data/youbike_log/日期.csv` 的實際車數驗證 → `dashboard.py` 把全部整合成單一 HTML。`periods.py` 是共用的節次時間和學期行事曆（週次、放假日）；`youbike_collector.py` 的 `ZONES` 定義 5 區的建築物座標，`data/stations_map.csv` 是區域和站點的對應表。

排程：`collect.yml` 每 30 分鐘排一次，每次跑約 5.5 小時、每 2 分鐘抓一次，用 concurrency 排隊接力；`update-site.yml` 每天 22:30（台灣時間）驗證並更新網站。不要在本機同時跑收集程式，同一天的檔案會衝突。

## 附近抱石館地圖（`climbing/`）

說明在 `climbing/README.md`，資料來源和搜尋紀錄在 `climbing/資料來源紀錄.md`（補資料時要在「操作紀錄」加一段）。

資料流：
1. `climbing/data/gyms_seed.json` 是唯一要手動改的資料。每間館的每個欄位用 `src` 對應到最上面的 `sources` 代號；`verify` 列待確認事項；`osm_keywords` 是比對 OpenStreetMap 名稱用的關鍵字組（每組的字要全部出現在 OSM 名稱裡）。座標不寫，除非要手動覆蓋。
2. `climbing/scripts/enrich.py` 補座標：先比對 OSM（Overpass），對不到再用 Nominatim 查地址（門牌 → 路段 → 地標 → 館名），輸出 `gyms.json`（網頁讀這個，不要手動改）和 `enrich_report.md`。座標可信度看 `coord_source`。連不到 OSM 時沿用上一次的座標。
3. `climbing/scripts/youbike_near.py` 抓全台 YouBike（`apis.youbike.com.tw` 非正式 API）和臺北市開放資料，「可借、可還都是 0」視為沒有資料（2026-10-23 起北部資料源都回 0），記錄每館附近站的車數到 `data/youbike_log/`，並算出 `youbike_pattern.json`（站號 → 平日 `wd`／假日 `we` → 30 分鐘時段編號 `slot = 小時*2 + 分//30` → `[平均可借, 平均可還, 樣本數]`）。加 `--stations` 才會更新全台站點位置檔。
4. 網頁（`index.html`、`app.js`、`style.css`）是純靜態，Leaflet 和 OSM 底圖從 unpkg 載入，沒有建置步驟。`app.js` 讀 `data/` 下的 JSON；交通建議用直線距離乘上繞路係數估時間，路線本身交給 Google 地圖網址（`/maps/dir/?api=1&travelmode=...`）。留言用 giscus（`config.js` 的 `repoId`、`categoryId` 空著時不顯示）。

本機預覽：在 `climbing/` 執行 `python -m http.server 8000`。

原則（使用者確認過的）：
- 只收室內館，以抱石為主。
- 不爬 Google 地圖（違反使用條款），只附搜尋連結讓人手動對照；要顯示 Google 評論、照片需要 Places API 金鑰，使用者還沒申請。
- 不能確認的資料寫進 `verify`，不要猜。
