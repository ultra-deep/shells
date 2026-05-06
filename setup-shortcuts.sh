#!/bin/bash

# Disable shortcuts
gsettings set org.gnome.shell.keybindings toggle-quick-settings "[]"
gsettings set org.gnome.shell.keybindings toggle-message-tray "[]"

gsettings set org.gnome.desktop.wm.keybindings maximize "[]"
gsettings set org.gnome.desktop.wm.keybindings unmaximize "[]"

# Split view
gsettings set org.gnome.desktop.wm.keybindings move-to-side-west "['<Super><Alt>Left']"
gsettings set org.gnome.desktop.wm.keybindings move-to-side-east "['<Super><Alt>Right']"

# Launchers
gsettings set org.gnome.settings-daemon.plugins.media-keys control-center "['<Super>s']"

# Disable monitor movement
gsettings set org.gnome.desktop.wm.keybindings move-to-monitor-down "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-monitor-left "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-monitor-right "[]"
gsettings set org.gnome.desktop.wm.keybindings move-to-monitor-up "[]"

# Workspace movement (move window)
gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-left "['<Super><Shift>Left']"
gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-right "['<Super><Shift>Right']"

# Workspace switching
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-left "['<Super>Left']"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-right "['<Super>Right']"

echo "All shortcuts updated successfully."