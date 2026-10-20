@echo off
chcp 65001 >nul
title YouBike 收資料（請不要關閉這個視窗）
cd /d "%~dp0"
echo 正在收集台大 YouBike 資料，每 2 分鐘記錄一次。
echo 要停止時，按 Ctrl+C 或直接關掉這個視窗。
echo.
python youbike_collector.py
echo.
echo 收資料程式已經停止。
pause
