@echo off
REM Expense Ledger - Windows Installer
REM Run this script to build and install the app

echo Installing Expense Ledger...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Install from python.org
    pause
    exit /b 1
)

REM Create venv
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
pip install flask werkzeug openpyxl reportlab pyinstaller pillow

REM Build
pyinstaller ExpenseLedger.spec

REM Install
if exist "dist\ExpenseLedger" (
    xcopy /E /Y "dist\ExpenseLedger" "%USERPROFILE%\Applications\ExpenseLedger\"
    echo.
    echo Installed to: %USERPROFILE%\Applications\ExpenseLedger
    echo.
    echo Run: %USERPROFILE%\Applications\ExpenseLedger\ExpenseLedger.exe
) else (
    echo Build failed!
)

pause