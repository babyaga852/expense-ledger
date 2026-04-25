#!/bin/bash
# Expense Ledger - Mac Installer
# Run this script on Mac to build and install the app

set -e

echo "Installing Expense Ledger..."

# Check if Python installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Install from https://python.org"
    exit 1
fi

# Create app directory
APP_DIR="$HOME/Applications/ExpenseLedger"
mkdir -p "$APP_DIR"

# Copy project files (assumes this script is in expense-ledger folder)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cp -r "$SCRIPT_DIR"/* "$APP_DIR/"

# Create venv and install dependencies
cd "$APP_DIR"
python3 -m venv venv
source venv/bin/activate
pip install flask werkzeug openpyxl reportlab pyinstaller pillow

# Build app
rm -rf dist/ExpenseLedger
pyinstaller ExpenseLedger.spec

# Install
rm -rf "$HOME/Applications/ExpenseLedger.App"
cp -r dist/ExpenseLedger "$HOME/Applications/ExpenseLedger.App"

# Make executable
chmod +x "$HOME/Applications/ExpenseLedger.App/ExpenseLedger"

# Create LaunchAgent for auto-start (optional)
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$HOME/Library/LaunchAgents/com.expenseledger.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.expenseledger</string>
    <key>ProgramArguments</key>
    <array>
        <string>$HOME/Applications/ExpenseLedger.App/ExpenseLedger</string>
    </array>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

echo "✓ Installed to: $HOME/Applications/ExpenseLedger.App"
echo ""
echo "Run app:"
echo "$HOME/Applications/ExpenseLedger.App/ExpenseLedger"
echo ""
echo "Or double-click: $HOME/Applications/ExpenseLedger.App/ExpenseLedger"