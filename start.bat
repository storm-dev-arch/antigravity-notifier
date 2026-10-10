@echo off
cd /d "%~dp0"
start /min "" "C:\Users\storm\AppData\Local\Programs\Python\Python314\python.exe" "%~dp0notifier_service.py"
echo Antigravity Notifier launched in background.