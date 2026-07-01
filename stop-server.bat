@echo off
setlocal enabledelayedexpansion

echo Searching for Free Claude Code server on port 8082...
set "found=0"

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8082 ^| findstr LISTENING') do (
    echo Terminating server process with PID %%a...
    taskkill /f /pid %%a >nul 2>&1
    set "found=1"
)

rem Also terminate any command window with the launcher title
taskkill /fi "windowtitle eq FCC_SERVER_WINDOW" /f >nul 2>&1

if "%found%"=="1" (
    echo Proxy server successfully terminated.
) else (
    echo No proxy server was active on port 8082.
)
