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
REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo === HCS Builder Setup ===

REM 1. Create .venv directory (Python's venv module creates it, but we check first)
if exist ".venv" (
    echo .venv directory already exists.
) else (
    echo Creating .venv directory...
    REM mkdir .venv is handled by python module usually, but good to be explicit
    mkdir .venv
)

REM 2. Create virtual environment
echo Initializing virtual environment...
python -m venv .venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)

REM 3. Activate virtual environment (optional in batch if we just call the binary, but sticking to logic)
echo Activating virtual environment...
call .venv\Scripts\activate

REM 4. Install requirements
if exist "requirements.txt" (
    echo Installing requirements from requirements.txt...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install requirements.
        pause
        exit /b 1
    )
) else (
    echo WARNING: requirements.txt not found!
)

echo.
echo === Setup Complete ===
echo You can now run the builder using: hcsbuilder.bat
echo.
pause
