@echo off
echo ============================================
echo   Expense Ledger - Build Installer
echo ============================================
echo.

echo [1/3] Installing required packages...
pip install pyinstaller flask openpyxl reportlab pillow

echo.
echo [2/3] Building .exe with PyInstaller...
pyinstaller --onedir --windowed ^
  --name "ExpenseLedger" ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --add-data "tracker.py;." ^
  --add-data "app.py;." ^
  --add-data "project.py;." ^
  --hidden-import flask ^
  --hidden-import openpyxl ^
  --hidden-import reportlab ^
  launcher.py

echo.
echo [3/3] Done! 
echo.
echo Next steps:
echo  1. Download and install Inno Setup from https://jrsoftware.org/isdl.php
echo  2. Open setup.iss in Inno Setup
echo  3. Click Build - Compile
echo  4. Your installer will be in the installer_output folder
echo.
pause
