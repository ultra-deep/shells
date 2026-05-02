#!/bin/bash

echo "Setting GNOME workspace shortcuts..."

# -------------------------------
# Move window between workspaces
# -------------------------------
gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-left "['<Shift><Super>Left']"
gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-right "['<Shift><Super>Right']"

# -------------------------------
# Switch workspace
# -------------------------------
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-left "['<Super>Left']"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-right "['<Super>Right']"

# -------------------------------
# Split view (tile windows)
# -------------------------------
gsettings set org.gnome.desktop.wm.keybindings move-to-side-left "['<Super><Ctrl><Shift>Left']"
gsettings set org.gnome.desktop.wm.keybindings move-to-side-right "['<Super><Ctrl><Shift>Right']"

echo "Workspace shortcuts configured."

# -------------------------------
# Create Transparent Terminal Profile
# -------------------------------
echo "Creating transparent terminal profile..."

PROFILE_ID=$(uuidgen)

# Clone default profile
DEFAULT_PROFILE=$(gsettings get org.gnome.Terminal.ProfilesList default | tr -d \')

dconf write /org/gnome/terminal/legacy/profiles:/:$PROFILE_ID/visible-name "'Transparent'"
dconf write /org/gnome/terminal/legacy/profiles:/:$PROFILE_ID/use-transparent-background "true"
dconf write /org/gnome/terminal/legacy/profiles:/:$PROFILE_ID/background-transparency-percent "30"

# Add profile to list
PROFILE_LIST=$(gsettings get org.gnome.Terminal.ProfilesList list)
NEW_LIST=$(echo $PROFILE_LIST | sed "s/]$/, '$PROFILE_ID']/")
gsettings set org.gnome.Terminal.ProfilesList list "$NEW_LIST"

echo "Transparent profile created."

# -------------------------------
# Create Super+T Shortcut
# -------------------------------
echo "Creating Super+T shortcut..."

CUSTOM_KEYBINDINGS_PATH="/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/"

gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings \
"['$CUSTOM_KEYBINDINGS_PATH']"

gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$CUSTOM_KEYBINDINGS_PATH name "Transparent Terminal"

gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$CUSTOM_KEYBINDINGS_PATH command \
"gnome-terminal --window-with-profile=Transparent"

gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$CUSTOM_KEYBINDINGS_PATH binding "<Super>t"

echo "✅ All shortcuts configured successfully!"

