# ntu-youbike｜台大 YouBike 擁擠預測

用台大課表推算每個下課時段騎來上課、下課騎走的人數，預測校內各區 YouBike 站會偏空（難借）還是偏滿（難還），
再用實際收集的車數驗證預測。

- 網站（每天 22:30 自動更新）：https://tim062480-create.github.io/ntu-youbike/
- 專案說明、決策與修改紀錄：[專案紀錄.md](專案紀錄.md)
- YouBike 資料由 GitHub Actions 每 2 分鐘自動收集，存在 `data/youbike_log/`

資料來源：臺大課程網、臺北市 YouBike 2.0 即時資訊、Open-Meteo 天氣資料。
