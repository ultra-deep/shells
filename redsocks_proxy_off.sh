#!/bin/bash

GROUP="cursorproxy"
GID=$(getent group $GROUP | cut -d: -f3)

echo "Disable proxy"

# Remove iptables rule
sudo iptables -t nat -D OUTPUT -p tcp -m owner --gid-owner $GID -j REDSOCKS 2>/dev/null

# Flush and remove chain
sudo iptables -t nat -F REDSOCKS 2>/dev/null
sudo iptables -t nat -X REDSOCKS 2>/dev/null

# Stop redsocks
sudo systemctl stop redsocks

echo "Proxy disabled"
