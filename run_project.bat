@echo off
title Nexus RAG Chatbot - Live Viva Launcher
color 0A
echo ========================================================
echo       Starting Nexus RAG Chatbot for Viva Demo
echo ========================================================
echo.

set PATH=C:\Users\vivek halnure\anaconda3;C:\Users\vivek halnure\anaconda3\Scripts;C:\Users\vivek halnure\anaconda3\Library\bin;%PATH%

echo [1/2] Starting Flask Backend Server on http://127.0.0.1:5000...
start "Nexus RAG Backend" cmd /k "cd /d "%~dp0backend" && python app.py"

echo [2/2] Opening Web UI in Default Browser...
timeout /t 2 >nul
start "" "%~dp0frontend\index.html"

echo.
echo ========================================================
echo  System is LIVE! Both backend and frontend are running.
echo ========================================================
pause
