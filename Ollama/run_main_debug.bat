@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

if not defined RUN_MAIN_LOGGING (
    if not exist "Logs" mkdir "Logs"

    for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "LOG_STAMP=%%I"
    set "LOG_FILE=%CD%\Logs\run_main_!LOG_STAMP!.txt"
    set "RUN_MAIN_BAT=%~f0"
    set "RUN_MAIN_LOGGING=1"

    echo Logging command output to:
    echo !LOG_FILE!
    echo.

    powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\run_with_log.ps1" -BatchFile "!RUN_MAIN_BAT!" -LogFile "!LOG_FILE!"
    set EXIT_CODE=%ERRORLEVEL%

    echo.
    echo Log saved to:
    echo !LOG_FILE!
    echo.
    pause
    endlocal
    exit /b %EXIT_CODE%
)

echo ========================================
echo Running main.py with debug output
echo Folder: %CD%
echo ========================================
echo.

if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "venv\Scripts\activate.bat"
) else (
    echo WARNING: venv\Scripts\activate.bat not found.
    echo Using system Python instead.
)

echo.
echo Python path:
where python
echo.
echo Python version:
python --version
echo.

echo Starting main.py...
echo ========================================
python -u "main.py"
set EXIT_CODE=%ERRORLEVEL%
echo ========================================
echo.

if not "%EXIT_CODE%"=="0" (
    echo main.py exited with error code %EXIT_CODE%.
    echo Check the traceback above for details.
) else (
    echo main.py finished successfully.
)

echo.
endlocal
