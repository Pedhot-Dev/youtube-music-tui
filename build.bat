@echo off
REM Build script for YouTube Music TUI (Windows)

echo Building YouTube Music TUI...

REM Check if virtual environment exists
if not exist ".venv\" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Build with PyInstaller
echo Building executable...
pyinstaller youtube-music-tui.spec

echo Build complete! Binary located at: dist\youtube-music-tui.exe
pause
