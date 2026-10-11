@echo off
chcp 65001 >nul
title Antigravity Notifier
echo Запуск Antigravity Notifier (System Tray)...
start "" "C:\Users\storm\AppData\Local\Programs\Python\Python314\pythonw.exe" "%~dp0app.py"