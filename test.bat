@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

:: 1. Check dynamic AppData location first (avoids WindowsApps stub)
if exist "%LOCALAPPDATA%\Programs\Python" (
    for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
        if exist "%%i\python.exe" (
            "%%i\python.exe" "%~dp0toast.py"
            exit /b 0
        )
    )
)

:: 2. Check python in PATH
where python >nul 2>nul
if %errorlevel% equ 0 (
    python "%~dp0toast.py"
    exit /b 0
)

:: 3. Check py launcher
where py >nul 2>nul
if %errorlevel% equ 0 (
    py "%~dp0toast.py"
    exit /b 0
)

echo [ERROR] Python not found in PATH or standard directories!
pause
exit /b 1