@echo off
chcp 65001 >nul
cd /d "%~dp0"
powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*notifier_service.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Output ('?????????? ???????????: ' + $_.ProcessId) }"