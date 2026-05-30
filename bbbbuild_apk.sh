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


INFO_COLOR=$CYAN

NC='\033[0m' # No Color

set -e

ARGS="$1"

build() {
  local environment=$1
  local buildType=$2
  local environmentCapitalized="${environment^}" # production -> Production
  local buildTypeCapitalized="${buildType^}" # release -> Release

    echo " "
    echo " "
    echo -e "${ORANGE}*******************************************************************************************${NC}"
    echo -e "            Building ${B}${BRIGHT_CYAN}${environmentCapitalized}${R}  ${B}${GREEN}${buildTypeCapitalized}${NC}${R}..."
    echo -e "${ORANGE}*******************************************************************************************${NC}"
    echo " "
    echo " "

    ./gradlew "assemble${environmentCapitalized}${buildTypeCapitalized}"
    mkdir -p "app/${environment}/$buildType" #app/production/debug
    mv "/home/x/AndroidStudioProjects/AndriodTraderApp/app/build/outputs/apk/${environment}/${buildType}/app-${environment}-${buildType}.apk" "app/${environment}/${buildType}/"
}



if [[ "$ARGS" == *"-pr"* ]]; then
    build "production" "release"
fi
if [[ "$ARGS" == *"-pd"* ]]; then
    build "production" "debug"
fi

if [[ "$ARGS" == *"-sr"* ]]; then
    build "staging" "release"
fi
if [[ "$ARGS" == *"-sd"* ]]; then
    build "staging" "debug"
fi

if [[ "$ARGS" == *"-dr"* ]]; then
    build "develop" "release"
fi
if [[ "$ARGS" == *"-dd"* ]]; then
    build "develop" "debug"
fi

if [[ -z "$ARGS" ]]; then
    echo "Usage:"
    echo "-pr    -> Production Release"
    echo "-pd    -> Production Debug"
    echo "-sr    -> Staging Release"
    echo "-sd    -> Staging Develop"
    echo "-dr    -> Develop Release"
    echo "-dd    -> Develop Debug"
    echo "--------------------------------------------------------------"
    echo "    Also, you can use composite of -pr -pd -sr -sd -dr -dd"
    echo "--------------------------------------------------------------"
    echo "-pr-sr-dr  -> All (Release)"
    echo "-pd-sd-dd  -> All (Debug)"
fi