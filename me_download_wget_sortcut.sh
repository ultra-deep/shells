#!/bin/bash
# Script to take the text from clipboard, replace all non-alphanumeric characters with a single dash,
# and put the processed text back into the clipboard

## Check if xclip is installed
#if ! command -v xclip &> /dev/null
#then
#    echo "xclip is not installed. Please install it first: sudo apt install xclip"
#    exit 1
#fi

# Check if xclip is installed
if ! command -v xclip >/dev/null 2>&1; then
  echo "Error: xclip is not installed."
  echo "Please install it using your package manager, for example:"
  echo "  sudo apt install xclip"
  exit 1
fi


## Copy the selected text to clipboard
#xclip -o -selection primary | xclip -selection clipboard
## Get text from clipboard, process it, and put it back into the clipboard
#xclip -o -selection clipboard | \
#perl -pe 's/[^a-zA-Z0-9]+/-/g' | \
#xclip -i -selection clipboard

#!/bin/bash

# Read text from clipboard
text=$(xclip -selection clipboard -o)

# Remove "task" from the beginning (case-insensitive)
text=$(echo "$text" | sed -E 's/^[Tt][Aa][Ss][Kk][[:space:]]*//')


x-terminal-emulator -e bash -c "wget -P /media/x/apps/TEMPLATE/ -c \"$text\" ;echo; echo 'Press Enter to close...'; read"
