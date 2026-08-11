#!/usr/bin/env bash

#!/bin/bash
RED='\033[1;31m'
GREEN='\033[0;32m'
BLUE='\033[0;36m'
YELLOW="\033[33m"
ORANGE='\033[0;33m'
CYAN='\033[0;36m'
MAGENTA="\033[35m"


# Bright foreground colors
BRIGHT_BLACK="\033[90m"
BRIGHT_RED="\033[91m"
BRIGHT_GREEN="\033[92m"
BRIGHT_YELLOW="\033[93m"
BRIGHT_BLUE="\033[94m"
BRIGHT_MAGENTA="\033[95m"
BRIGHT_CYAN="\033[96m"
BRIGHT_WHITE="\033[97m"

# styles
# Text styles
B="\033[1m"
DIM="\033[2m"
I="\033[3m"
U="\033[4m"
BLINK="\033[5m"
REVERSE="\033[7m"
HIDDEN="\033[8m"
STRIKETHROUGH="\033[9m"
R='\e[0m' # Reser or Regular Text



willRemoveString="$1"

if [[ -z "$willRemoveString" ]]; then
  echo "use params for REMOVING from names of files on current path..."
  exit 1
fi

for file in *; do
  [[ -f "$file" ]] || continue

  name="${file%.*}"
  ext="${file##*.}"

  newname="${name//$willRemoveString/}"

  if [[ -n "$newname" ]]; then
    #mv -- "$file" "$newname.$ext"
    echo -e "${ORANGE}$file${NC}"
    echo -e "${B}${GREEN}${newname}.${ext}${NC}${R}"
    echo " "
  fi
done
#######################################################
####################### READ ##########################
#######################################################
echo ""
echo ""
echo "#######################################################"
echo -e "Press ${B}${GREEN}Enter${NC}${R} to continue or any other key to cancel..."
echo "#######################################################"
read -n 1 -s key

echo " "
echo " "
if [[ $key == "" ]]; then
    echo "Renaming started..."
else
    echo -e "${RED}Canceled"
    exit 1
fi
echo " "
echo " "

#######################################################
#######################################################
#######################################################

for file in *; do
  [[ -f "$file" ]] || continue

  name="${file%.*}"
  ext="${file##*.}"

  newname="${name//$willRemoveString/}"

  if [[ -n "$newname" ]]; then
    mv -- "$file" "$newname.$ext"
  fi
done


echo -e "${GREEN}Renaming completed...{$NC}"
