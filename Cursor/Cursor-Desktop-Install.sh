#!/usr/bin/env bash

set -e

APP_NAME="Cursor"
APPIMAGE="$(pwd)/Cursor-3.17.8-x86_64.AppImage"
ICON="$(pwd)/Cursor.png"
DESKTOP_DIR="$HOME/.local/share/applications"
DESKTOP_FILE="$DESKTOP_DIR/$APP_NAME.desktop"

if [[ ! -f "$APPIMAGE" ]]; then
    echo "Error: $APPIMAGE not found."
    exit 1
fi

if [[ ! -f "$ICON" ]]; then
    echo "Error: $ICON not found."
    exit 1
fi

chmod +x "$APPIMAGE"

mkdir -p "$DESKTOP_DIR"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=$APP_NAME
Comment=$APP_NAME AppImage
Exec=$APPIMAGE
Icon=$ICON
Terminal=false
Type=Application
Categories=Utility;
StartupWMClass=$APP_NAME
EOF

chmod +x "$DESKTOP_FILE"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
fi

echo "Installed successfully:"
echo "$DESKTOP_FILE"
