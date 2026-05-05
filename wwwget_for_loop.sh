#!/bin/bash

RED='\033[1;31m'
GREEN='\033[0;32m'
BLUE='\033[0;36m'
YELLOW='\033[1;33m'
ORANGE='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

BASE_URL=$1
COUNT=$2

if [[ "$BASE_URL" != *"@"* ]]; then
  echo "The @ Not found in url..."
  exit 4041
fi

if [[ -z "$COUNT" || ! "$COUNT" =~ ^[0-9]+$ ]]; then
  echo "The count is empty or not a digit"
fi

download() {
  URL=$1
  for attempt in 1 2 3; do
    filename=$(basename "${URL%%\?*}")
    echo -e "${BLUE}Attempt $attempt for downlaoding ${YELLOW} $filename ${NC}"
    if wget -nc "$URL"; then
      echo -e "${GREEN} $filename ${GREEN}Downloaded successfully${NC}"
      echo -e "${GREEN} ------------------------------------------ ${NC}"
      break
    else
      echo -e "${RED}Downloaded failed! $filename ${NC}"
    fi
    sleep 2
  done
}

for i in $(seq 1 "$COUNT"); do
  # find count of @ serially
  ats=$(grep -o '@\+' <<<"$BASE_URL" | head -n1)
  at_count=${#ats}

  num=$(printf "%0${at_count}d" "$i")
  ORIGIN_URL=${BASE_URL/$ats/$num}

  echo -e "downloading $ORIGIN_URL"
  #download "$ORIGIN_URL"
done

echo
echo -e "${CYAN}*********************************${NC}"
echo -e "${CYAN}     Press Enter to close...${NC}"
echo -e "${CYAN}*********************************${NC}"
read
