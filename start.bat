@echo off
setlocal
cd /d "%~dp0"

:: 1. Check standard AppData location dynamically for current user first (avoids WindowsApps stub)
if exist "%LOCALAPPDATA%\Programs\Python" (
    for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
        if exist "%%i\pythonw.exe" (
            start "" "%%i\pythonw.exe" "%~dp0notifier_service.py"
            goto success
        )
        if exist "%%i\python.exe" (
            start /min "" "%%i\python.exe" "%~dp0notifier_service.py"
            goto success
        )
    )
)

:: 2. Check pythonw in PATH (runs completely without terminal window)
where pythonw >nul 2>nul
if %errorlevel% equ 0 (
    start "" pythonw "%~dp0notifier_service.py"
    goto success
)

:: 3. Check py launcher
where py >nul 2>nul
if %errorlevel% equ 0 (
    start "" py -3 "%~dp0notifier_service.py"
    goto success
)

:: 4. Check python in PATH
where python >nul 2>nul
if %errorlevel% equ 0 (
    start /min "" python "%~dp0notifier_service.py"
    goto success
)

echo [ERROR] Python not found in PATH or standard directories!
echo Please make sure Python is installed and added to PATH.
pause
exit /b 1

:success
echo Antigravity Notifier launched in background.