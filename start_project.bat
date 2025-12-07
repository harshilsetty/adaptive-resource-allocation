@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM Start Flask server in new window
start "Flask Server" cmd /k "cd /d %~dp0 & .\venv\Scripts\activate & python test_server.py"

REM Wait a moment then open frontend
timeout /t 2 /nobreak >nul
start "" "%~dp0frontend\index.html"
exit
