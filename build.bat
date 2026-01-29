@echo off
echo ========================================
echo XML Test Viewer - Windows Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Build executable
echo Building executable...
pyinstaller --onefile --windowed --name "XMLTestViewer" --icon=NONE main.py

echo.
echo ========================================
echo Build complete!
echo Executable location: dist\XMLTestViewer.exe
echo ========================================
pause
