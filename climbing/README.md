# 附近抱石館地圖

用手機定位，自動列出附近的室內抱石館；點開可以看價格、營業時間、影片、留言和交通建議（大眾運輸、YouBike）。

- 網址（合併到 main 後）：https://tim062480-create.github.io/ntu-youbike/climbing/
- 資料怎麼來的、怎麼驗證：[資料來源紀錄.md](資料來源紀錄.md)

## 資料夾

```
climbing/
├─ index.html  app.js  style.css   網頁（純靜態，Leaflet ＋ OpenStreetMap 底圖，不用金鑰）
├─ config.js                        留言區（giscus）設定
├─ 資料來源紀錄.md                  資料來源、搜尋紀錄、待確認清單
├─ data/
│  ├─ gyms_seed.json        ★ 人工整理的館資料（唯一要手動改的檔案），每個欄位附來源代號
│  ├─ gyms.json             網頁讀的資料（enrich.py 產生：seed ＋ 經緯度 ＋ OSM 比對）
│  ├─ enrich_report.md      座標來源與 OSM 交叉比對報告
│  ├─ youbike_stations.json 全台 YouBike 站點位置
│  ├─ youbike_near.json     各館附近站的最新車數
│  ├─ youbike_pattern.json  各站平日／假日每 30 分鐘的平均車數（預測用）
│  └─ youbike_log/日期.csv  館附近站的車數記錄
└─ scripts/
   ├─ enrich.py             補經緯度（OSM Overpass → Nominatim）
   └─ youbike_near.py       YouBike 車數記錄與歷史平均
```

資料由 `.github/workflows/climbing-data.yml` 自動更新（YouBike 每 20 分鐘、座標每週一次或改了 seed 之後）。

## 常用操作

| 做什麼 | 怎麼做 |
|---|---|
| 新增／修改館 | 改 `data/gyms_seed.json` 後 push，Actions 會自動重新補座標 |
| 座標不對 | 在 seed 該館加上 `"lat": 25.0, "lng": 121.5`（手動座標優先），或改 `osm_keywords` |
| 本機看網頁 | 在 `climbing` 資料夾執行 `python -m http.server 8000`，打開 http://localhost:8000 （定位需要 https 或 localhost） |
| 本機跑資料程式 | `python climbing/scripts/enrich.py`、`python climbing/scripts/youbike_near.py --stations`（只用 Python 內建套件） |

## 開啟留言區（giscus，要登入 GitHub 才能留言）

1. repo 的 **Settings → General → Features** 勾選 **Discussions**
2. 到 **Discussions** 新增一個分類，名稱「抱石館留言」，格式選 **Announcement**（只有 giscus 能開新討論串）
3. 安裝 giscus App：https://github.com/apps/giscus ，只選這個 repo
4. 打開 https://giscus.app/zh-TW ，填入 `tim062480-create/ntu-youbike`、選「抱石館留言」分類，頁面下方會出現 `data-repo-id` 和 `data-category-id`
5. 把這兩個值填進 `config.js` 的 `repoId`、`categoryId`，push 後每間館就有自己的留言串
