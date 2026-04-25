#!/bin/bash
# Expense Ledger - Build for Mac
# Run on Mac to create .app bundle

set -e

echo "Building for Mac..."

cd "$(dirname "$0")"

# Activate venv
source venv/bin/activate

# Clean old build
rm -rf dist/ExpenseLedger build/ExpenseLedger

# Build for Mac
pyinstaller ExpenseLedger.spec --onedir

# Create .app bundle structure
APP_DIR="dist/ExpenseLedger.App"
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# Copy executable
cp dist/ExpenseLedger/ExpenseLedger "$APP_DIR/Contents/MacOS/"

# Copy resources
cp -r dist/ExpenseLedger/_internal "$APP_DIR/Contents/Resources/"
cp expense_ledger_logo.png "$APP_DIR/Contents/Resources/"

# Create Info.plist
cat > "$APP_DIR/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>ExpenseLedger</string>
    <key>CFBundleIdentifier</key>
    <string>com.expenseledger.app</string>
    <key>CFBundleName</key>
    <string>Expense Ledger</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleIconFile</key>
    <string>expense_ledger_logo.png</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.9</string>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category-finance</string>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeName</key>
            <string>Expense Ledger Data</string>
        </dict>
    </array>
</dict>
</plist>
EOF

echo "✓ Mac app created: dist/ExpenseLedger.App"
echo ""
echo "To package as DMG:"
echo "hdiutil create -volname ExpenseLedger -srcfolder dist/ExpenseLedger.App -ovf ExpenseLedger.dmg"