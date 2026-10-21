@echo off
title Nexus RAG Chatbot - Live Launcher
color 0A
echo ========================================================
echo       Starting Nexus RAG Chatbot for Live Demo
echo ========================================================
echo.

:: 1. Check if virtual environment exists
if exist "%~dp0backend\venv\Scripts\python.exe" (
    set "PYTHON_CMD="%~dp0backend\venv\Scripts\python.exe""
    goto :RUN_APP
)

:: 2. Check for Anaconda installation
if exist "C:\Users\vivek halnure\anaconda3\python.exe" (
    set PATH=C:\Users\vivek halnure\anaconda3;C:\Users\vivek halnure\anaconda3\Scripts;C:\Users\vivek halnure\anaconda3\Library\bin;%PATH%
    set "PYTHON_CMD=python"
    goto :RUN_APP
)

:: 3. Default system python
set "PYTHON_CMD=python"

:RUN_APP
echo [1/2] Starting Flask Backend Server on http://127.0.0.1:5000...
start "Nexus RAG Backend" cmd /k "cd /d "%~dp0backend" && %PYTHON_CMD% app.py"

echo [2/2] Opening Web UI in Default Browser...
timeout /t 2 >nul
start "" "%~dp0frontend\index.html"

echo.
echo ========================================================
echo  System is LIVE! Both backend and frontend are running.
echo ========================================================
pause
