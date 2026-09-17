@echo off
rem Randomise the Windows Terminal theme, then open Terminal.
rem Works from any folder: %~dp0 is the folder this .bat file lives in.
rem Any arguments are passed on, e.g.  WinTerminal_Run.bat --no-shader

set "PY=python"
where py >nul 2>nul && set "PY=py -3"

%PY% "%~dp0src\terminal_randomizer.py" %*
if errorlevel 1 (
    echo.
    echo Terminal Randomizer failed, see the message above.
    pause
)

rem wt.exe is an app alias that stays valid when Terminal updates,
rem unlike the versioned path under C:\Program Files\WindowsApps.
start "" wt.exe
