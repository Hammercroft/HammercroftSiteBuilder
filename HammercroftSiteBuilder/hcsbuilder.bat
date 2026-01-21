REM TODO UNTESTED CODE
REM TODO UNTESTED CODE
REM TODO UNTESTED CODE
REM TODO UNTESTED CODE
REM TODO UNTESTED CODE
REM TODO UNTESTED CODE
REM TODO UNTESTED CODE
REM TODO UNTESTED CODE
REM TODO UNTESTED CODE
REM TODO UNTESTED CODE
REM TODO UNTESTED CODE
REM TODO UNTESTED CODE
REM TODO UNTESTED CODE
REM TODO UNTESTED CODE
REM TODO UNTESTED CODE
REM TODO UNTESTED CODE

@echo off
REM HCS Builder launcher script for Windows
REM This script checks for Python 3 and runs hcsbuilder.py

setlocal

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "PYTHON_SCRIPT=%SCRIPT_DIR%hcsbuilder.py"
set "VENV_PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe"

REM Check if virtual environment exists and use it
if exist "%VENV_PYTHON%" (
    "%VENV_PYTHON%" "%PYTHON_SCRIPT%" %*
    exit /b %ERRORLEVEL%
)

REM Virtual environment not found, try system Python
REM Check if Python 3 is available (try python3 first, then python)
where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo WARNING: Virtual environment not found, using system Python 3
    python3 "%PYTHON_SCRIPT%" %*
    exit /b %ERRORLEVEL%
)

REM Try 'python' command (might be Python 3 on Windows)
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    REM Check if it's Python 3
    python -c "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo WARNING: Virtual environment not found, using system Python 3
        python "%PYTHON_SCRIPT%" %*
        exit /b %ERRORLEVEL%
    )
)

REM Python 3 not found
echo ERROR: Python 3 is not installed or not in your PATH.
echo.
echo Please install Python 3 to use HCS Builder:
echo   - Download from: https://www.python.org/downloads/
echo   - Make sure to check "Add Python to PATH" during installation
echo.
exit /b 1
