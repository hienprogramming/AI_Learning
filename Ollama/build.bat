@echo off
REM Build Pipeline for Embedded C Code
REM Compile, detect errors, and auto-fix

setlocal enabledelayedexpansion

echo.
echo ================================================================
echo   EMBEDDED C BUILD PIPELINE
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python 3.8+
    exit /b 1
)

REM Run the build script
python build.py %*

exit /b %errorlevel%
