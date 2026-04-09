@echo off
echo ============================================
echo   Expense Ledger - Build Installer
echo ============================================
echo.

echo [1/4] Installing required packages...
pip install pyinstaller flask openpyxl reportlab pillow inno-setup

echo.
echo [2/4] Building .exe with PyInstaller...
pyinstaller --clean ExpenseLedger.spec

echo.
echo [3/4] Creating Windows Installer with Inno Setup...
echo.

REM Check if Inno Setup is installed
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
    echo.
    echo [4/4] Done! Installer created in installer_output folder
) else (
    echo.
    echo Inno Setup not found. Please install from:
    echo https://jrsoftware.org/isdl.php
    echo.
    echo The .exe application is ready in: dist\ExpenseLedger\
    echo Run setup.iss manually in Inno Setup to create the installer.
)

echo.
echo ============================================
echo   Build Complete!
echo ============================================
echo.
echo Application location: dist\ExpenseLedger\ExpenseLedger.exe
echo Installer location: installer_output\ExpenseLedger_Setup_v1.0.exe
echo.
pause
