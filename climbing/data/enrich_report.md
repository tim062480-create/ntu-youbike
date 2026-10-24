# 座標與 OpenStreetMap 交叉比對報告

產生時間：2026-10-24 14:11（由 `climbing/scripts/enrich.py` 在 GitHub Actions 上產生）
OSM 連線：成功

座標來源說明：`osm` ＝ OSM 上有這間館（最準）；`nominatim:address` ＝ 用門牌定位；`nominatim:road` ＝ 只定位到路段（可能差幾百公尺）；`nominatim:place`／`nominatim:name` ＝ 用地標或館名定位；`none` ＝ 找不到，網頁上列在「位置待補」。

| 館 | 狀態 | 座標來源 | 查詢字串／OSM 名稱 | OSM 與地址定位相差 | 驗證連結 |
|---|---|---|---|---|---|
| 角 • 攀岩館 中山 | 營業中 | osm | 角 · 攀岩館 - 中山 | 366 公尺 | [OSM](https://www.openstreetmap.org/?mlat=25.0569486&mlon=121.5225824#map=18/25.0569486/121.5225824) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E8%A7%92%20%E2%80%A2%20%E6%94%80%E5%B2%A9%E9%A4%A8%20%E4%B8%AD%E5%B1%B1%20%E8%87%BA%E5%8C%97%E5%B8%82%E4%B8%AD%E5%B1%B1%E5%8D%80%E4%B8%AD%E5%B1%B1%E5%8C%97%E8%B7%AF%E4%BA%8C%E6%AE%B568%E8%99%9FB1) |
| 角 • 攀岩館 華山 | 營業中 | none |  |  |  [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E8%A7%92%20%E2%80%A2%20%E6%94%80%E5%B2%A9%E9%A4%A8%20%E8%8F%AF%E5%B1%B1%20%E8%87%BA%E5%8C%97%E5%B8%82%E4%B8%AD%E5%B1%B1%E5%8D%80%E6%96%B0%E7%94%9F%E5%8C%97%E8%B7%AF%E4%B8%80%E6%AE%B586%E8%99%9F) |
| 原岩攀岩館 萬華店 | 營業中 | osm | 原岩攀岩館-萬華店 | 60 公尺 | [OSM](https://www.openstreetmap.org/?mlat=25.0342851&mlon=121.496916#map=18/25.0342851/121.496916) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%8E%9F%E5%B2%A9%E6%94%80%E5%B2%A9%E9%A4%A8%20%E8%90%AC%E8%8F%AF%E5%BA%97%20%E8%87%BA%E5%8C%97%E5%B8%82%E8%90%AC%E8%8F%AF%E5%8D%80%E5%A4%A7%E7%90%86%E8%A1%97149%E8%99%9F) |
| 原岩攀岩館 明德店 | 營業中 | osm | 原岩攀岩館-明德店 | 102 公尺 | [OSM](https://www.openstreetmap.org/?mlat=25.1082962&mlon=121.5142184#map=18/25.1082962/121.5142184) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%8E%9F%E5%B2%A9%E6%94%80%E5%B2%A9%E9%A4%A8%20%E6%98%8E%E5%BE%B7%E5%BA%97%20%E8%87%BA%E5%8C%97%E5%B8%82%E5%8C%97%E6%8A%95%E5%8D%80%E6%96%87%E6%9E%97%E5%8C%97%E8%B7%AF222%E8%99%9FB1) |
| 原岩攀岩館 南港店 | 營業中 | nominatim:road | 臺北市南港區南港路二段 |  | [OSM](https://www.openstreetmap.org/?mlat=25.0537865&mlon=121.5984943#map=18/25.0537865/121.5984943) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%8E%9F%E5%B2%A9%E6%94%80%E5%B2%A9%E9%A4%A8%20%E5%8D%97%E6%B8%AF%E5%BA%97%20%E8%87%BA%E5%8C%97%E5%B8%82%E5%8D%97%E6%B8%AF%E5%8D%80%E5%8D%97%E6%B8%AF%E8%B7%AF%E4%BA%8C%E6%AE%B5147%E8%99%9F) |
| 原岩攀岩館 中和店 | 營業中 | osm | 原岩中和店 | 42 公尺 | [OSM](https://www.openstreetmap.org/?mlat=25.0062525&mlon=121.4860912#map=18/25.0062525/121.4860912) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%8E%9F%E5%B2%A9%E6%94%80%E5%B2%A9%E9%A4%A8%20%E4%B8%AD%E5%92%8C%E5%BA%97%20%E6%96%B0%E5%8C%97%E5%B8%82%E4%B8%AD%E5%92%8C%E5%8D%80%E7%AB%8B%E8%A8%80%E8%A1%9741%E8%99%9F) |
| 原岩攀岩館 新店店 | 營業中 | nominatim:road | 新北市新店區中興路三段 |  | [OSM](https://www.openstreetmap.org/?mlat=24.9856719&mlon=121.5422127#map=18/24.9856719/121.5422127) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%8E%9F%E5%B2%A9%E6%94%80%E5%B2%A9%E9%A4%A8%20%E6%96%B0%E5%BA%97%E5%BA%97%20%E6%96%B0%E5%8C%97%E5%B8%82%E6%96%B0%E5%BA%97%E5%8D%80%E4%B8%AD%E8%88%88%E8%B7%AF%E4%B8%89%E6%AE%B570%E8%99%9F7%E6%A8%93%EF%BC%88YES%21LIFE%20%E8%A3%95%E9%9A%86%E5%9F%8E%EF%BC%89) |
| 原岩攀岩館 A19店（搬遷中） | 待確認 | nominatim:road | 桃園市中壢區高鐵南路二段 |  | [OSM](https://www.openstreetmap.org/?mlat=25.0039617&mlon=121.2059456#map=18/25.0039617/121.2059456) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%8E%9F%E5%B2%A9%E6%94%80%E5%B2%A9%E9%A4%A8%20A19%E5%BA%97%EF%BC%88%E6%90%AC%E9%81%B7%E4%B8%AD%EF%BC%89%20%E6%A1%83%E5%9C%92%E5%B8%82%E4%B8%AD%E5%A3%A2%E5%8D%80%E9%AB%98%E9%90%B5%E5%8D%97%E8%B7%AF%E4%BA%8C%E6%AE%B5352%E8%99%9F4%E6%A8%93%EF%BC%88Global%20Mall%20%E7%92%B0%E7%90%83%E8%B3%BC%E7%89%A9%E4%B8%AD%E5%BF%83%EF%BC%89) |
| 原岩攀岩館 楊梅店 | 可能已停業 | osm | 原岩攀岩館-楊梅店 | 445 公尺 | [OSM](https://www.openstreetmap.org/?mlat=24.9200421&mlon=121.1451743#map=18/24.9200421/121.1451743) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%8E%9F%E5%B2%A9%E6%94%80%E5%B2%A9%E9%A4%A8%20%E6%A5%8A%E6%A2%85%E5%BA%97%20%E6%A1%83%E5%9C%92%E5%B8%82%E6%A5%8A%E6%A2%85%E5%8D%80%E6%A2%85%E9%AB%98%E8%B7%AF99%E5%B7%B720%E8%99%9F) |
| 市民抱石攀岩館 | 營業中 | nominatim:road | 臺北市南港區市民大道八段 |  | [OSM](https://www.openstreetmap.org/?mlat=25.0531814&mlon=121.6067087#map=18/25.0531814/121.6067087) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%B8%82%E6%B0%91%E6%8A%B1%E7%9F%B3%E6%94%80%E5%B2%A9%E9%A4%A8%20%E8%87%BA%E5%8C%97%E5%B8%82%E5%8D%97%E6%B8%AF%E5%8D%80%E5%B8%82%E6%B0%91%E5%A4%A7%E9%81%93%E5%85%AB%E6%AE%B5548%E8%99%9F) |
| 奇岩攀岩館 | 營業中 | nominatim:road | 臺北市南港區忠孝東路七段 |  | [OSM](https://www.openstreetmap.org/?mlat=25.0521753&mlon=121.6072066#map=18/25.0521753/121.6072066) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%A5%87%E5%B2%A9%E6%94%80%E5%B2%A9%E9%A4%A8%20%E8%87%BA%E5%8C%97%E5%B8%82%E5%8D%97%E6%B8%AF%E5%8D%80%E5%BF%A0%E5%AD%9D%E6%9D%B1%E8%B7%AF%E4%B8%83%E6%AE%B5512%E8%99%9F) |
| 紅石攀岩 士林館 | 營業中 | nominatim:road | 臺北市士林區承德路四段 |  | [OSM](https://www.openstreetmap.org/?mlat=25.0904048&mlon=121.5174523#map=18/25.0904048/121.5174523) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E7%B4%85%E7%9F%B3%E6%94%80%E5%B2%A9%20%E5%A3%AB%E6%9E%97%E9%A4%A8%20%E8%87%BA%E5%8C%97%E5%B8%82%E5%A3%AB%E6%9E%97%E5%8D%80%E6%89%BF%E5%BE%B7%E8%B7%AF%E5%9B%9B%E6%AE%B5261%E8%99%9FB1) |
| 紅石攀岩 新竹館 | 營業中 | none |  |  |  [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E7%B4%85%E7%9F%B3%E6%94%80%E5%B2%A9%20%E6%96%B0%E7%AB%B9%E9%A4%A8%20%E6%96%B0%E7%AB%B9%E5%B8%82) |
| double8 岩究所 | 營業中 | nominatim:address | 臺北市大同區迪化街 |  | [OSM](https://www.openstreetmap.org/?mlat=25.0561728&mlon=121.5102161#map=18/25.0561728/121.5102161) [Google 地圖](https://www.google.com/maps/search/?api=1&query=double8%20%E5%B2%A9%E7%A9%B6%E6%89%80%20%E8%87%BA%E5%8C%97%E5%B8%82%E5%A4%A7%E5%90%8C%E5%8D%80%E8%BF%AA%E5%8C%96%E8%A1%97%EF%BC%88%E5%A4%A7%E7%A8%BB%E5%9F%95%E8%80%81%E6%B4%8B%E6%88%BF%E5%85%A7%EF%BC%8C%E9%96%80%E7%89%8C%E5%BE%85%E7%A2%BA%E8%AA%8D%EF%BC%89) |
| Camp4 達文西攀岩館 | 營業中 | none |  |  |  [Google 地圖](https://www.google.com/maps/search/?api=1&query=Camp4%20%E9%81%94%E6%96%87%E8%A5%BF%E6%94%80%E5%B2%A9%E9%A4%A8%20%E8%87%BA%E5%8C%97%E5%B8%82) |
| 小岩館 | 營業中 | osm | The little rock | 9968 公尺 | [OSM](https://www.openstreetmap.org/?mlat=25.1088442&mlon=121.5298068#map=18/25.1088442/121.5298068) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%B0%8F%E5%B2%A9%E9%A4%A8%20%E8%87%BA%E5%8C%97%E5%B8%82) |
| Y17 Climbing Gym | 待確認 | none |  |  |  [Google 地圖](https://www.google.com/maps/search/?api=1&query=Y17%20Climbing%20Gym%20%E8%87%BA%E5%8C%97%E5%B8%82) |
| 內湖運動中心攀岩館（光合作用） | 營業中 | nominatim:address | 臺北市內湖運動中心 |  | [OSM](https://www.openstreetmap.org/?mlat=25.0772346&mlon=121.5753648#map=18/25.0772346/121.5753648) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%85%A7%E6%B9%96%E9%81%8B%E5%8B%95%E4%B8%AD%E5%BF%83%E6%94%80%E5%B2%A9%E9%A4%A8%EF%BC%88%E5%85%89%E5%90%88%E4%BD%9C%E7%94%A8%EF%BC%89%20%E8%87%BA%E5%8C%97%E5%B8%82%E5%85%A7%E6%B9%96%E9%81%8B%E5%8B%95%E4%B8%AD%E5%BF%83) |
| 南港運動中心攀岩場 | 營業中 | nominatim:address | 臺北市南港運動中心 |  | [OSM](https://www.openstreetmap.org/?mlat=25.0489041&mlon=121.5818903#map=18/25.0489041/121.5818903) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%8D%97%E6%B8%AF%E9%81%8B%E5%8B%95%E4%B8%AD%E5%BF%83%E6%94%80%E5%B2%A9%E5%A0%B4%20%E8%87%BA%E5%8C%97%E5%B8%82%E5%8D%97%E6%B8%AF%E9%81%8B%E5%8B%95%E4%B8%AD%E5%BF%83) |
| 萬華運動中心攀岩場 | 營業中 | nominatim:address | 臺北市萬華運動中心 |  | [OSM](https://www.openstreetmap.org/?mlat=25.0474308&mlon=121.5065669#map=18/25.0474308/121.5065669) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E8%90%AC%E8%8F%AF%E9%81%8B%E5%8B%95%E4%B8%AD%E5%BF%83%E6%94%80%E5%B2%A9%E5%A0%B4%20%E8%87%BA%E5%8C%97%E5%B8%82%E8%90%AC%E8%8F%AF%E9%81%8B%E5%8B%95%E4%B8%AD%E5%BF%83) |
| 北投運動中心攀岩場 | 待確認 | nominatim:address | 臺北市北投運動中心 |  | [OSM](https://www.openstreetmap.org/?mlat=25.11666&mlon=121.50962#map=18/25.11666/121.50962) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%8C%97%E6%8A%95%E9%81%8B%E5%8B%95%E4%B8%AD%E5%BF%83%E6%94%80%E5%B2%A9%E5%A0%B4%20%E8%87%BA%E5%8C%97%E5%B8%82%E5%8C%97%E6%8A%95%E9%81%8B%E5%8B%95%E4%B8%AD%E5%BF%83) |
| 趣攀岩 TitoRock（永和國民運動中心） | 營業中 | nominatim:address | 新北市永和國民運動中心 |  | [OSM](https://www.openstreetmap.org/?mlat=25.00317&mlon=121.52407#map=18/25.00317/121.52407) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E8%B6%A3%E6%94%80%E5%B2%A9%20TitoRock%EF%BC%88%E6%B0%B8%E5%92%8C%E5%9C%8B%E6%B0%91%E9%81%8B%E5%8B%95%E4%B8%AD%E5%BF%83%EF%BC%89%20%E6%96%B0%E5%8C%97%E5%B8%82%E6%B0%B8%E5%92%8C%E5%9C%8B%E6%B0%91%E9%81%8B%E5%8B%95%E4%B8%AD%E5%BF%836%E6%A8%93) |
| MegaSTONE Climbing Gym | 營業中 | nominatim:road | 新北市新莊區中正路 |  | [OSM](https://www.openstreetmap.org/?mlat=25.0346843&mlon=121.4455471#map=18/25.0346843/121.4455471) [Google 地圖](https://www.google.com/maps/search/?api=1&query=MegaSTONE%20Climbing%20Gym%20%E6%96%B0%E5%8C%97%E5%B8%82%E6%96%B0%E8%8E%8A%E5%8D%80%E4%B8%AD%E6%AD%A3%E8%B7%AF56%E5%B7%B75%E8%99%9F) |
| POGO Bouldering Gym | 待確認 | nominatim:address | 新北市新莊區 |  | [OSM](https://www.openstreetmap.org/?mlat=25.0357722&mlon=121.4502478#map=18/25.0357722/121.4502478) [Google 地圖](https://www.google.com/maps/search/?api=1&query=POGO%20Bouldering%20Gym%20%E6%96%B0%E5%8C%97%E5%B8%82%E6%96%B0%E8%8E%8A%E5%8D%80%EF%BC%88%E6%8D%B7%E9%81%8B%E8%BC%94%E5%A4%A7%E7%AB%99%E6%AD%A5%E8%A1%8C%E7%B4%84%205%20%E5%88%86%E9%90%98%EF%BC%8C%E9%96%80%E7%89%8C%E5%BE%85%E7%A2%BA%E8%AA%8D%EF%BC%89) |
| 千手抱石 | 營業中 | nominatim:road | 桃園市桃園區龍壽街 |  | [OSM](https://www.openstreetmap.org/?mlat=25.0106703&mlon=121.3875031#map=18/25.0106703/121.3875031) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%8D%83%E6%89%8B%E6%8A%B1%E7%9F%B3%20%E6%A1%83%E5%9C%92%E5%B8%82%E6%A1%83%E5%9C%92%E5%8D%80%E9%BE%8D%E5%A3%BD%E8%A1%97162%E8%99%9F2%E6%A8%93) |
| iClimb 風城攀岩館 | 營業中 | osm | 風城攀岩館 iClimb |  | [OSM](https://www.openstreetmap.org/?mlat=24.8197808&mlon=121.0241394#map=18/24.8197808/121.0241394) [Google 地圖](https://www.google.com/maps/search/?api=1&query=iClimb%20%E9%A2%A8%E5%9F%8E%E6%94%80%E5%B2%A9%E9%A4%A8%20%E6%96%B0%E7%AB%B9%E7%B8%A3) |
| B-Plus 攀岩館（本館） | 營業中 | nominatim:road | 臺中市西屯區環中路二段 |  | [OSM](https://www.openstreetmap.org/?mlat=24.1791542&mlon=120.6347984#map=18/24.1791542/120.6347984) [Google 地圖](https://www.google.com/maps/search/?api=1&query=B-Plus%20%E6%94%80%E5%B2%A9%E9%A4%A8%EF%BC%88%E6%9C%AC%E9%A4%A8%EF%BC%89%20%E8%87%BA%E4%B8%AD%E5%B8%82%E8%A5%BF%E5%B1%AF%E5%8D%80%E7%92%B0%E4%B8%AD%E8%B7%AF%E4%BA%8C%E6%AE%B5982-1%E8%99%9F) |
| B-Plus 攀岩館（太原館） | 營業中 | none |  |  |  [Google 地圖](https://www.google.com/maps/search/?api=1&query=B-Plus%20%E6%94%80%E5%B2%A9%E9%A4%A8%EF%BC%88%E5%A4%AA%E5%8E%9F%E9%A4%A8%EF%BC%89%20%E8%87%BA%E4%B8%AD%E5%B8%82) |
| Dapro 室內攀岩場 | 營業中 | nominatim:road | 臺中市南屯區永春東七路 |  | [OSM](https://www.openstreetmap.org/?mlat=24.1304329&mlon=120.6301684#map=18/24.1304329/120.6301684) [Google 地圖](https://www.google.com/maps/search/?api=1&query=Dapro%20%E5%AE%A4%E5%85%A7%E6%94%80%E5%B2%A9%E5%A0%B4%20%E8%87%BA%E4%B8%AD%E5%B8%82%E5%8D%97%E5%B1%AF%E5%8D%80%E6%B0%B8%E6%98%A5%E6%9D%B1%E4%B8%83%E8%B7%AF700%E8%99%9F) |
| 二廠攀岩 | 待確認 | nominatim:road | 臺中市烏日區健行路 |  | [OSM](https://www.openstreetmap.org/?mlat=24.109511&mlon=120.600509#map=18/24.109511/120.600509) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E4%BA%8C%E5%BB%A0%E6%94%80%E5%B2%A9%20%E8%87%BA%E4%B8%AD%E5%B8%82%E7%83%8F%E6%97%A5%E5%8D%80%E5%81%A5%E8%A1%8C%E8%B7%AF131%E8%99%9F) |
| 攀吶攀岩館 | 待確認 | none |  |  |  [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E6%94%80%E5%90%B6%E6%94%80%E5%B2%A9%E9%A4%A8%20%E8%87%BA%E4%B8%AD%E5%B8%82) |
| The Depot City | 已停業 | none |  |  |  [Google 地圖](https://www.google.com/maps/search/?api=1&query=The%20Depot%20City%20%E8%87%BA%E4%B8%AD%E5%B8%82) |
| 破舊工廠 Shabby Factory | 營業中 | nominatim:road | 彰化縣員林市新義街 |  | [OSM](https://www.openstreetmap.org/?mlat=23.9584466&mlon=120.5677345#map=18/23.9584466/120.5677345) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E7%A0%B4%E8%88%8A%E5%B7%A5%E5%BB%A0%20Shabby%20Factory%20%E5%BD%B0%E5%8C%96%E7%B8%A3%E5%93%A1%E6%9E%97%E5%B8%82%E6%96%B0%E7%BE%A9%E8%A1%97104%E8%99%9F) |
| 嘉義攀岩會館（鐵道藝術村） | 營業中 | nominatim:address | 嘉義市鐵道藝術村 |  | [OSM](https://www.openstreetmap.org/?mlat=23.4838312&mlon=120.4416239#map=18/23.4838312/120.4416239) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%98%89%E7%BE%A9%E6%94%80%E5%B2%A9%E6%9C%83%E9%A4%A8%EF%BC%88%E9%90%B5%E9%81%93%E8%97%9D%E8%A1%93%E6%9D%91%EF%BC%89%20%E5%98%89%E7%BE%A9%E5%B8%82%E9%90%B5%E9%81%93%E8%97%9D%E8%A1%93%E6%9D%91) |
| 嘉義市國民運動中心 8a 攀岩場 | 營業中 | osm | 嘉義市國民運動中心 | 0 公尺 | [OSM](https://www.openstreetmap.org/?mlat=23.471551&mlon=120.4628704#map=18/23.471551/120.4628704) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%98%89%E7%BE%A9%E5%B8%82%E5%9C%8B%E6%B0%91%E9%81%8B%E5%8B%95%E4%B8%AD%E5%BF%83%208a%20%E6%94%80%E5%B2%A9%E5%A0%B4%20%E5%98%89%E7%BE%A9%E5%B8%82%E5%9C%8B%E6%B0%91%E9%81%8B%E5%8B%95%E4%B8%AD%E5%BF%83) |
| High Fun 嗨翻綜合體能館 | 營業中 | osm | 嗨翻 | 363 公尺 | [OSM](https://www.openstreetmap.org/?mlat=23.011325&mlon=120.1900737#map=18/23.011325/120.1900737) [Google 地圖](https://www.google.com/maps/search/?api=1&query=High%20Fun%20%E5%97%A8%E7%BF%BB%E7%B6%9C%E5%90%88%E9%AB%94%E8%83%BD%E9%A4%A8%20%E8%87%BA%E5%8D%97%E5%B8%82%E5%8C%97%E5%8D%80%E5%A4%A7%E5%92%8C%E8%B7%AF121%E8%99%9F) |
| High Fun 嗨翻攀岩館 仁德店 | 營業中 | nominatim:road | 臺南市仁德區文心路 |  | [OSM](https://www.openstreetmap.org/?mlat=22.9728213&mlon=120.2410907#map=18/22.9728213/120.2410907) [Google 地圖](https://www.google.com/maps/search/?api=1&query=High%20Fun%20%E5%97%A8%E7%BF%BB%E6%94%80%E5%B2%A9%E9%A4%A8%20%E4%BB%81%E5%BE%B7%E5%BA%97%20%E8%87%BA%E5%8D%97%E5%B8%82%E4%BB%81%E5%BE%B7%E5%8D%80%E6%96%87%E5%BF%83%E8%B7%AF80%E8%99%9F) |
| B-TOPIA 攀岩館 | 營業中 | nominatim:address | 高雄市 |  | [OSM](https://www.openstreetmap.org/?mlat=22.6203348&mlon=120.3120375#map=18/22.6203348/120.3120375) [Google 地圖](https://www.google.com/maps/search/?api=1&query=B-TOPIA%20%E6%94%80%E5%B2%A9%E9%A4%A8%20%E9%AB%98%E9%9B%84%E5%B8%82%EF%BC%88%E6%8D%B7%E9%81%8B%E4%B8%89%E5%A4%9A%E5%95%86%E5%9C%88%E7%AB%99%203%20%E8%99%9F%E5%87%BA%E5%8F%A3%E6%AD%A5%E8%A1%8C%E7%B4%84%201%20%E5%88%86%E9%90%98%EF%BC%8C%E9%96%80%E7%89%8C%E5%BE%85%E7%A2%BA%E8%AA%8D%EF%BC%89) |
| 抱石基地 | 營業中 | nominatim:name | 抱石基地 高雄市 |  | [OSM](https://www.openstreetmap.org/?mlat=22.6439399&mlon=120.3052953#map=18/22.6439399/120.3052953) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E6%8A%B1%E7%9F%B3%E5%9F%BA%E5%9C%B0%20%E9%AB%98%E9%9B%84%E5%B8%82) |
| 圓石空間 Boulder Space（左營店） | 營業中 | none |  |  |  [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%9C%93%E7%9F%B3%E7%A9%BA%E9%96%93%20Boulder%20Space%EF%BC%88%E5%B7%A6%E7%87%9F%E5%BA%97%EF%BC%89%20%E9%AB%98%E9%9B%84%E5%B8%82) |
| Qingchang Climbing Life Center（中文名待確認） | 待確認 | none |  |  |  [Google 地圖](https://www.google.com/maps/search/?api=1&query=Qingchang%20Climbing%20Life%20Center%EF%BC%88%E4%B8%AD%E6%96%87%E5%90%8D%E5%BE%85%E7%A2%BA%E8%AA%8D%EF%BC%89%20%E9%AB%98%E9%9B%84%E5%B8%82) |
| 久淘攀岩館 宜大殿 | 營業中 | osm | 久淘攀岩館 | 206 公尺 | [OSM](https://www.openstreetmap.org/?mlat=24.7527054&mlon=121.7496109#map=18/24.7527054/121.7496109) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E4%B9%85%E6%B7%98%E6%94%80%E5%B2%A9%E9%A4%A8%20%E5%AE%9C%E5%A4%A7%E6%AE%BF%20%E5%AE%9C%E8%98%AD%E7%B8%A3%E5%AE%9C%E8%98%AD%E5%B8%82%E5%81%A5%E5%BA%B7%E8%B7%AF%E4%B8%89%E6%AE%B566%E8%99%9F) |
| 舞岩抱石攀岩館 | 待確認 | nominatim:road | 宜蘭縣冬山鄉冬山路二段 |  | [OSM](https://www.openstreetmap.org/?mlat=24.6508939&mlon=121.7825909#map=18/24.6508939/121.7825909) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E8%88%9E%E5%B2%A9%E6%8A%B1%E7%9F%B3%E6%94%80%E5%B2%A9%E9%A4%A8%20%E5%AE%9C%E8%98%AD%E7%B8%A3%E5%86%AC%E5%B1%B1%E9%84%89%E5%86%AC%E5%B1%B1%E8%B7%AF%E4%BA%8C%E6%AE%B5534%E8%99%9F) |
| 歪仔歪攀岩館 | 營業中 | nominatim:address | 宜蘭縣員山鄉 |  | [OSM](https://www.openstreetmap.org/?mlat=24.743183&mlon=121.723372#map=18/24.743183/121.723372) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E6%AD%AA%E4%BB%94%E6%AD%AA%E6%94%80%E5%B2%A9%E9%A4%A8%20%E5%AE%9C%E8%98%AD%E7%B8%A3%E5%93%A1%E5%B1%B1%E9%84%89) |
| 宜蘭運動中心攀岩館 | 營業中 | osm | 宜蘭國民運動中心 | 2059 公尺 | [OSM](https://www.openstreetmap.org/?mlat=24.7389332&mlon=121.7557822#map=18/24.7389332/121.7557822) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%AE%9C%E8%98%AD%E9%81%8B%E5%8B%95%E4%B8%AD%E5%BF%83%E6%94%80%E5%B2%A9%E9%A4%A8%20%E5%AE%9C%E8%98%AD%E7%B8%A3%E5%AE%9C%E8%98%AD%E9%81%8B%E5%8B%95%E4%B8%AD%E5%BF%83) |
| 崩NUS（BONUS）抱石館 | 營業中 | osm | 崩岩館 | 123 公尺 | [OSM](https://www.openstreetmap.org/?mlat=23.9877651&mlon=121.6018246#map=18/23.9877651/121.6018246) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%B4%A9NUS%EF%BC%88BONUS%EF%BC%89%E6%8A%B1%E7%9F%B3%E9%A4%A8%20%E8%8A%B1%E8%93%AE%E7%B8%A3%E8%8A%B1%E8%93%AE%E5%B8%82%E5%9C%8B%E6%B0%91%E4%B8%80%E8%A1%9738%E8%99%9F3F) |
| B-Plus 抱石館（花蓮吉安） | 待確認 | nominatim:address | 花蓮縣吉安鄉自強路300巷30弄 |  | [OSM](https://www.openstreetmap.org/?mlat=23.9813111&mlon=121.5892998#map=18/23.9813111/121.5892998) [Google 地圖](https://www.google.com/maps/search/?api=1&query=B-Plus%20%E6%8A%B1%E7%9F%B3%E9%A4%A8%EF%BC%88%E8%8A%B1%E8%93%AE%E5%90%89%E5%AE%89%EF%BC%89%20%E8%8A%B1%E8%93%AE%E7%B8%A3%E5%90%89%E5%AE%89%E9%84%89%E8%87%AA%E5%BC%B7%E8%B7%AF300%E5%B7%B730%E5%BC%84) |
| 禾匠體驗學習（攀岩） | 營業中 | nominatim:road | 臺東縣臺東市中興路四段 |  | [OSM](https://www.openstreetmap.org/?mlat=22.7745057&mlon=121.0877917#map=18/22.7745057/121.0877917) [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E7%A6%BE%E5%8C%A0%E9%AB%94%E9%A9%97%E5%AD%B8%E7%BF%92%EF%BC%88%E6%94%80%E5%B2%A9%EF%BC%89%20%E8%87%BA%E6%9D%B1%E7%B8%A3%E8%87%BA%E6%9D%B1%E5%B8%82%E4%B8%AD%E8%88%88%E8%B7%AF%E5%9B%9B%E6%AE%B5434%E8%99%9F) |
| 加壹岩館 | 已停業 | none |  |  |  [Google 地圖](https://www.google.com/maps/search/?api=1&query=%E5%8A%A0%E5%A3%B9%E5%B2%A9%E9%A4%A8%20%E8%87%BA%E5%8C%97%E5%B8%82) |

## OSM 上有、但人工清單沒有的攀岩地點（84 個，可能是漏掉的館或已停業）

| 名稱 | 標籤 | 連結 |
|---|---|---|
| 根抱石 |  | [OSM](https://www.openstreetmap.org/node/4070047136) |
| 攀岩場 | sport=climbing | [OSM](https://www.openstreetmap.org/node/4074616534) |
| 唭哩岸攀岩場 |  | [OSM](https://www.openstreetmap.org/node/4164220050) |
| 樹抱石 |  | [OSM](https://www.openstreetmap.org/node/4221005940) |
| 瑠公攀岩基地 | leisure=fitness_centre, sport=climbing | [OSM](https://www.openstreetmap.org/node/4526316791) |
| 峭壁雄風地圖(攀岩低繞叉路走) |  | [OSM](https://www.openstreetmap.org/node/4991509849) |
| 龍洞攀岩場 鐘塔 | sport=climbing | [OSM](https://www.openstreetmap.org/node/5162170086) |
| 龍洞攀岩場 黃金谷 | sport=climbing | [OSM](https://www.openstreetmap.org/node/5162170087) |
| 龍洞攀岩場 第一洞 | sport=climbing | [OSM](https://www.openstreetmap.org/node/5162170088) |
| 龍洞攀岩場 校門口 | sport=climbing | [OSM](https://www.openstreetmap.org/node/5162170089) |
| 龍洞攀岩場 長巷 | sport=climbing | [OSM](https://www.openstreetmap.org/node/5162170090) |
| 龍洞攀岩場 後門 | sport=climbing | [OSM](https://www.openstreetmap.org/node/5162170091) |
| 龍洞攀岩場 音樂廳 | sport=climbing | [OSM](https://www.openstreetmap.org/node/5162170092) |
| 龍洞攀岩場 第二洞 | sport=climbing | [OSM](https://www.openstreetmap.org/node/5162170093) |
| 龍洞攀岩場 大禮堂 | sport=climbing | [OSM](https://www.openstreetmap.org/node/5162170094) |
| （無名稱） | leisure=pitch, sport=climbing | [OSM](https://www.openstreetmap.org/node/5377430582) |
| Decathlon | sport=fitness;table_tennis;climbing;swimming;soccer;basketball;multi;tennis;gymnastics;equestrian;baseball;yoga;shooting;skateboard;exercise;canoe;billiards;volleyball;skiing;disc_golf | [OSM](https://www.openstreetmap.org/node/5419599921) |
| 南港山攀岩路線登山口 |  | [OSM](https://www.openstreetmap.org/node/5593526988) |
| 攀岩塔 | leisure=pitch, sport=climbing | [OSM](https://www.openstreetmap.org/node/5655150586) |
| The Bivy | sport=climbing, website=https://www.taiwanrockclimbing.com | [OSM](https://www.openstreetmap.org/node/6794354109) |
| 樹抱石 |  | [OSM](https://www.openstreetmap.org/node/7259943041) |
| 樹抱石 |  | [OSM](https://www.openstreetmap.org/node/8569322985) |
| passion climbing爬森攀岩館 | leisure=sports_centre, sport=climbing | [OSM](https://www.openstreetmap.org/node/9316739471) |
| （無名稱） | leisure=sports_centre, sport=climbing | [OSM](https://www.openstreetmap.org/node/9467562650) |
| 壽山岩場 | leisure=sports_centre, sport=climbing | [OSM](https://www.openstreetmap.org/node/9481324542) |
| 攀岩場 | sport=climbing | [OSM](https://www.openstreetmap.org/node/9501881753) |
| 迪卡儂 | sport=fitness;soccer;exercise;basketball;cycling;baseball;camping;climbing, website=https://www.decathlon.tw/ | [OSM](https://www.openstreetmap.org/node/9524456390) |
| 攀岩場 | leisure=sports_centre, sport=climbing | [OSM](https://www.openstreetmap.org/node/9862100448) |
| Rock Climbers |  | [OSM](https://www.openstreetmap.org/node/10277714385) |
| 樹抱石神木 |  | [OSM](https://www.openstreetmap.org/node/10968481771) |
| 得從事攀岩活動地區 (一線天 (迴旋谷)) |  | [OSM](https://www.openstreetmap.org/node/12358486373) |
| 得從事攀岩活動地區 (一線天 (迴旋谷)) |  | [OSM](https://www.openstreetmap.org/node/12681239911) |
| BABO PAPAK | leisure=sports_centre, sport=climbing, website=https://linktr.ee/babopapak | [OSM](https://www.openstreetmap.org/node/13295191398) |
| 原岩攀岩館-明德店 | leisure=sports_centre, sport=climbing | [OSM](https://www.openstreetmap.org/node/13417522409) |
| （無名稱） | leisure=sports_centre, sport=climbing | [OSM](https://www.openstreetmap.org/node/13437893337) |
| 階梯攀岩區 | leisure=playground | [OSM](https://www.openstreetmap.org/node/14272888127) |
| #4攀岩天梯 |  | [OSM](https://www.openstreetmap.org/way/136977257) |
| 體育活動中心 | sport=climbing | [OSM](https://www.openstreetmap.org/way/193248286) |
| 體育館 | sport=multi;basketball;volleyball;climbing;bedminton | [OSM](https://www.openstreetmap.org/way/193249153) |
| 大安運動中心 | leisure=sports_centre, sport=badminton;basketball;climbing;golf;roller_skating;swimming;table_tennis, website=https://dasc.cyc.org.tw/ | [OSM](https://www.openstreetmap.org/way/194580871) |
| 南港山峭壁攀岩線橫向步道 |  | [OSM](https://www.openstreetmap.org/way/233130268) |
| #2攀岩 |  | [OSM](https://www.openstreetmap.org/way/233130276) |
| #3攀岩 |  | [OSM](https://www.openstreetmap.org/way/233130286) |
| 攀岩場地 | leisure=pitch, sport=climbing | [OSM](https://www.openstreetmap.org/way/286922783) |
| #5攀岩 |  | [OSM](https://www.openstreetmap.org/way/319679956) |
| #1攀岩 |  | [OSM](https://www.openstreetmap.org/way/319679961) |
| 南港山峭壁電視塔攀岩線 |  | [OSM](https://www.openstreetmap.org/way/319737754) |
| 探索教學體驗場地 | sport=climbing_adventure | [OSM](https://www.openstreetmap.org/way/335698567) |
| 三重國民運動中心 | leisure=stadium, sport=basketball;swimming;climbing;badminton;running | [OSM](https://www.openstreetmap.org/way/344665661) |
| （無名稱） | leisure=pitch, sport=climbing | [OSM](https://www.openstreetmap.org/way/356901118) |
| （無名稱） | leisure=sports_centre, sport=climbing | [OSM](https://www.openstreetmap.org/way/362518883) |
| （無名稱） | sport=climbing_adventure | [OSM](https://www.openstreetmap.org/way/362518900) |
| 攀岩場 | leisure=pitch | [OSM](https://www.openstreetmap.org/way/368190046) |
| 攀岩段 |  | [OSM](https://www.openstreetmap.org/way/399020621) |
| 攀岩場 | leisure=sports_centre, sport=climbing | [OSM](https://www.openstreetmap.org/way/402105183) |
| 南港山峭壁電視塔攀岩線 |  | [OSM](https://www.openstreetmap.org/way/412969272) |
| 攀岩垂降練習場 | leisure=common | [OSM](https://www.openstreetmap.org/way/421731155) |
| 北投天然攀岩場 | leisure=common | [OSM](https://www.openstreetmap.org/way/421731169) |
| 2號攀岩繩索30米 |  | [OSM](https://www.openstreetmap.org/way/425714408) |
| 1號攀岩繩索30公尺 |  | [OSM](https://www.openstreetmap.org/way/425714411) |
| 峭壁雄風攀岩繩索 |  | [OSM](https://www.openstreetmap.org/way/425714413) |
| 雷朗極限探索園區 | leisure=sports_centre, sport=climbing_adventure | [OSM](https://www.openstreetmap.org/way/452709117) |
| 攀岩場 | leisure=pitch, sport=climbing | [OSM](https://www.openstreetmap.org/way/496585246) |
| 獨立峰攀岩繩索 |  | [OSM](https://www.openstreetmap.org/way/510047685) |
| 探索教育場 | leisure=pitch, sport=climbing | [OSM](https://www.openstreetmap.org/way/527264957) |
| 體育館 | sport=multi;basketball;volleyball;climbing;bedminton | [OSM](https://www.openstreetmap.org/way/545409736) |
| 體育館 | sport=multi;basketball;volleyball;climbing;bedminton | [OSM](https://www.openstreetmap.org/way/545409737) |
| 體育館 | sport=multi;basketball;volleyball;climbing;bedminton | [OSM](https://www.openstreetmap.org/way/546233037) |
| 霞雲探索教育基地 | leisure=sports_centre, sport=climbing;溜索 | [OSM](https://www.openstreetmap.org/way/673602573) |
| 南港山峭壁攀岩線橫向步道 |  | [OSM](https://www.openstreetmap.org/way/700650798) |
| #4攀岩天梯 |  | [OSM](https://www.openstreetmap.org/way/700650801) |
| 山訓攀岩場 |  | [OSM](https://www.openstreetmap.org/way/733467687) |
| （無名稱） | leisure=sports_centre, sport=climbing | [OSM](https://www.openstreetmap.org/way/819112651) |
| （無名稱） | leisure=sports_centre, sport=climbing | [OSM](https://www.openstreetmap.org/way/820113975) |
| 桃園青年體驗學習園區 | leisure=sports_centre, sport=climbing_adventure, website=https://www.tyacamps.com.tw/ | [OSM](https://www.openstreetmap.org/way/1012320346) |
| 安樂社區攀爬樂園 | leisure=sports_centre, sport=climbing | [OSM](https://www.openstreetmap.org/way/1158096957) |
| iClimb風城攀岩 勝利館 |  | [OSM](https://www.openstreetmap.org/way/1220419515) |
| 攀岩場 |  | [OSM](https://www.openstreetmap.org/way/1245787756) |
| 攀岩段 |  | [OSM](https://www.openstreetmap.org/way/1266231362) |
| 攀岩運動區 | leisure=sports_centre, sport=climbing | [OSM](https://www.openstreetmap.org/way/1377997014) |
| 攀岩段 |  | [OSM](https://www.openstreetmap.org/way/1413619748) |
| 永和獅子攀岩廣場 | sport=climbing | [OSM](https://www.openstreetmap.org/way/1467096805) |
| （無名稱） | leisure=pitch, sport=climbing | [OSM](https://www.openstreetmap.org/way/1567346215) |
| （無名稱） | leisure=sports_centre, sport=climbing | [OSM](https://www.openstreetmap.org/relation/13707059) |
