#!/bin/bash

###### Step 1: Add your custom keybinding path to the list
#gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/ppproxy-disable/']"

###### Step 2: Set the name
#gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/ppproxy-disable/ name 'Disable Proxy'

###### Step 3: Set the command
#gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/ppproxy-disable/ command 'your-command-here'

###### Step 4: Set the keybinding
#gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/ppproxy-disable/ binding '<Shift><Ctrl>0'

set_shortcut() {
    local name=$1
    local binding=$2
    local command=$3

    local base_path="/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/"
    local path="${base_path}${name}/"

    # Read current keybindings array
    local current
    current=$(gsettings get org.gnome.settings-daemon.plugins.media-keys custom-keybindings)
    
    echo "raw current=$current"

    # If empty array
    if [[ "$current" == "@as []" ]] || [[ "$current" == "[]" ]];then
        new_array="['$path']"
    else
        # Remove brackets
        current="${current#[}"
        current="${current%]}"
        # Append new path properly
        new_array="[$current, '$path']"
    fi

    # Set the updated array
    gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "$new_array"

    # Set name, command, and binding
    gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$path name "$name"
    gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$path command "$command"
    gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$path binding "$binding"

    echo "Shortcut '$name' set: $binding -> $command"
}


set_shortcut ppproxy-disable "<Shift><Ctrl>Escape" "ppproxy 0"
set_shortcut ppproxy-1 "<Shift><Ctrl>1" "ppproxy 1"
set_shortcut ppproxy-2 "<Shift><Ctrl>2" "ppproxy 2"
set_shortcut ppproxy-3 "<Shift><Ctrl>3" "ppproxy 3"
set_shortcut ppproxy-3 "<Shift><Ctrl>4" "ppproxy 4"




