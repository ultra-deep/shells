#!/bin/bash

## --- Check dependencies and install missing ones ---
for pkg in wmctrl picom; do
  if ! command -v "$pkg" >/dev/null 2>&1; then
    echo "🔧 Installing missing package: $pkg ..."
    sudo apt update -qq
    sudo apt install -y "$pkg"
  fi
done

# Only start picom if no compositor (optional)
if ! pgrep -x picom >/dev/null && ! pgrep -x mutter >/dev/null && ! pgrep -x kwin_x11 >/dev/null && ! pgrep -x xfwm4 >/dev/null; then
    picom --daemon >/dev/null 2>&1
    sleep 0.5
fi

wid=$(xprop -root _NET_ACTIVE_WINDOW | awk '{print $5}')

if [[ -z "$wid" || "$wid" == "0x0" ]]; then
    echo "No active window found."
    exit 1
fi

FULL_DEC=4294967295
LOW_DEC=1288490188   # about 30%

current=$(xprop -id "$wid" _NET_WM_WINDOW_OPACITY 2>/dev/null | awk -F' = ' '{print $2}')

if [[ -z "$current" ]]; then
    current=$FULL_DEC
fi

# Convert hex to decimal if needed
if [[ "$current" =~ ^0x ]]; then
    current=$((current))
fi

if (( current >= FULL_DEC - 1 )); then
    xprop -id "$wid" -f _NET_WM_WINDOW_OPACITY 32c -set _NET_WM_WINDOW_OPACITY "$LOW_DEC"
 #   echo "Set window opacity to 30%"
else
    xprop -id "$wid" -f _NET_WM_WINDOW_OPACITY 32c -set _NET_WM_WINDOW_OPACITY "$FULL_DEC"
#    echo "Set window opacity to 100%"
fi

