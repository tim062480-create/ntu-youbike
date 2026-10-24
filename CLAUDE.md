# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# 台大 YouBike 擁擠預測

用台大課表推算各區 YouBike 站在下課時段會偏空或偏滿，再用實際收集的車數驗證。網站：https://tim062480-create.github.io/ntu-youbike/ 。使用者用繁體中文溝通，文件、註解、commit 訊息也都用繁體中文。

另一個專案「附近抱石館地圖」在獨立的 repo `tim062480-create/climbing-map`，不要在這裡加它的檔案。

## 慣例

- Python 只用內建套件（urllib、csv、json），沒有 requirements.txt、沒有測試框架、沒有 linter。要確認程式能跑就直接執行它。
- 各來源的欄位名稱常常不同，用 `get(d, *keys)` 依序嘗試多個欄位名稱。
- 車數「可借、可還都是 0」視為資料不明（`youbike_collector.counts_valid()`）：不記錄、不驗證、不算歷史平均。2026-10-23 起官方資料曾整批回傳 0。
- Actions 寫回 repo 的方式：`git add` → commit（沒變更就略過）→ `git pull --rebase` 再 push，失敗就重試。`collect.yml` 每 30 分鐘就會 commit 到 main，所以本機 push 前一定要先 pull。
- `schedule` 只在預設分支（main）上執行；開發分支上的 workflow 靠 `push` 觸發。
- 雲端開發環境的網路被限制，常連不到 YouBike、OpenStreetMap、Google 等網站；需要外部資料的步驟寫成程式交給 Actions 跑。

## 架構與指令

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
