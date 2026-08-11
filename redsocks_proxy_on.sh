#!/bin/bash

set -e

GROUP="cursorproxy"
PORT=12345

echo "Enable proxy for Cursor only"

# Restart redsocks
sudo systemctl enable redsocks
sudo systemctl restart redsocks

# Get group id
GID=$(getent group $GROUP | cut -d: -f3)

# Create chain if missing
if ! sudo iptables -t nat -L REDSOCKS -n &>/dev/null; then
    sudo iptables -t nat -N REDSOCKS
fi

# Flush old rules
sudo iptables -t nat -F REDSOCKS

# Ignore local/private networks
sudo iptables -t nat -A REDSOCKS -d 0.0.0.0/8 -j RETURN
sudo iptables -t nat -A REDSOCKS -d 10.0.0.0/8 -j RETURN
sudo iptables -t nat -A REDSOCKS -d 127.0.0.0/8 -j RETURN
sudo iptables -t nat -A REDSOCKS -d 169.254.0.0/16 -j RETURN
sudo iptables -t nat -A REDSOCKS -d 172.16.0.0/12 -j RETURN
sudo iptables -t nat -A REDSOCKS -d 192.168.0.0/16 -j RETURN

# Redirect TCP traffic to redsocks
sudo iptables -t nat -A REDSOCKS -p tcp -j REDIRECT --to-ports $PORT

# Attach only for target group
if ! sudo iptables -t nat -C OUTPUT -p tcp -m owner --gid-owner $GID -j REDSOCKS &>/dev/null; then
    sudo iptables -t nat -A OUTPUT -p tcp -m owner --gid-owner $GID -j REDSOCKS
fi

echo "Proxy enabled"
