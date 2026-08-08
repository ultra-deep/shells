#!/bin/bash

set -e

# مسیر پوشه‌ای که این اسکریپت داخل آن قرار دارد
APP_DIR="$(cd "$(dirname "$0")" && pwd)"

DESKTOP_FILE="$APP_DIR/v2rayN.desktop"

if [ ! -d "$DESKTOP_FILE" ]; then
    cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=v2rayN
Comment=v2rayN Client
Exec=$APP_DIR/v2rayN
Icon=$APP_DIR/v2rayN.png
Terminal=false
Categories=Network;
StartupNotify=true
EOF
echo "Shortcut created:"
echo "$DESKTOP_FILE"
fi

chmod +x "$DESKTOP_FILE"

sudo desktop-file-install "$DESKTOP_FILE"

echo "desktop file installed"
