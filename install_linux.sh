#!/bin/bash
set -e

APP_NAME="ExpenseLedger"
APP_DIR="$HOME/Applications/$APP_NAME"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)/dist/ExpenseLedger"

if [ ! -d "$SRC_DIR" ]; then
    echo "Build not found. Run: pyinstaller ExpenseLedger.spec"
    exit 1
fi

echo "Installing Expense Ledger..."

rm -rf "$APP_DIR"
mkdir -p "$APP_DIR"
cp -r "$SRC_DIR"/* "$APP_DIR/"

mkdir -p "$HOME/.local/share/icons"
cp "$(dirname "$0")/expense_ledger_logo.png" "$HOME/.local/share/icons/$APP_NAME.png" 2>/dev/null || true

chmod +x "$APP_DIR/ExpenseLedger" 2>/dev/null || true

DESKTOP_FILE="$HOME/.local/share/applications/$APP_NAME.desktop"
mkdir -p "$HOME/.local/share/applications"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=Expense Ledger
Comment=Personal Finance Tracker
Exec=$APP_DIR/ExpenseLedger
Icon=$HOME/.local/share/icons/$APP_NAME.png
Terminal=false
Type=Application
Categories=Office;Finance;
EOF

echo "✓ Installed to: $APP_DIR"
echo "✓ Desktop entry created"
echo ""
echo "Run: $APP_DIR/ExpenseLedger"