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
FROM=$3
TIME_RANGE=$4

if [[ "$BASE_URL" != *"@"* ]]; then
    echo "The @ Not found in url..."
    exit 404
fi

if [[ -z "$COUNT" || ! "$COUNT" =~ ^[0-9]+$ ]]; then
    echo "The count is empty or not a digit... set default 30 for it"
   COUNT=30
fi

if [[ -z "$FROM" || ! "$FROM" =~ ^[0-9]+$ ]]; then
    echo "The FROM is empty or not a digit, set defalut 1 for it"
    FROM=1
fi

time_to_minutes() {
    local t="$1"
    local h=${t%:*}
    local m=${t#*:}
    echo $((10#$h * 60 + 10#$m))
}


is_time_in_specified_range() {

    [[ -z "$TIME_RANGE" ]] && return 0

    if [[ ! "$TIME_RANGE" =~ ^([0-9]{2}):([0-9]{2})-([0-9]{2}):([0-9]{2})$ ]]; then
        echo "Invalid time range format. Example: 02:10-07:45"
        exit 1
    fi

    local start_time=${TIME_RANGE%-*}
    local end_time=${TIME_RANGE#*-}

    local start=$(time_to_minutes "$start_time")
    local end=$(time_to_minutes "$end_time")

    local now=$(date +%H:%M)
    local current=$(time_to_minutes "$now")

    if (( start <= end )); then
        # example: 02:00-07:00
        (( current >= start && current < end ))
    else
        # example: 23:00-06:00
        (( current >= start || current < end ))
    fi
}

enforce_download_schedule() {

    [[ -z "$TIME_RANGE" ]] && return 0

    while ! is_time_in_specified_range; do
        now=$(date +%H:%M)
        echo -e "${YELLOW}Current time $now is outside $TIME_RANGE. Waiting 60 seconds...${NC}"
        sleep 60
    done
}

download() {
	URL=$1
	for ((attempt=1; attempt<=10; attempt++)); do

	    
	    enforce_download_schedule

	    if (( attempt > 1 )); then
	        sleep 30
      fi
	    filename=$(basename "${URL%%\?*}")
	    echo -e "${BLUE}Attempt $attempt for downloading ${YELLOW} $filename ${NC}"
	    if wget -c --no-check-certificate "$URL"; then
		echo -e "${GREEN} $filename ${GREEN}Downloaded successfully${NC}"
		echo -e "${GREEN} ------------------------------------------ ${NC}"
		break
	    else
	       	echo -e "${RED}Downloaded failed! $filename ${NC}"
	    fi
	done
}

for i in $(seq "$FROM" "$COUNT"); do
  # find count of @ serially
  ats=$(grep -o '@\+' <<<"$BASE_URL" | head -n1)
  at_count=${#ats}

  num=$(printf "%0${at_count}d" "$i")
  ORIGIN_URL=${BASE_URL/$ats/$num}

  #echo -e "downloading $ORIGIN_URL"
  download "$ORIGIN_URL"
done

echo;
echo -e "${CYAN}*********************************${NC}";
echo -e "${CYAN}     Press Enter to close...${NC}";
echo -e "${CYAN}*********************************${NC}";
read;

