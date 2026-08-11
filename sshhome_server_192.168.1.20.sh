#!/bin/bash
RED='\033[1;31m'
GREEN='\033[0;32m'
BLUE='\033[0;36m'
YELLOW='\033[1;33m'
ORANGE='\033[0;33m'
CYAN='\033[0;36m'


NC='\033[0m' # No Color


echo -e "ssh ${GREEN}root${RED}@${YELLOW}192.168.1.20${NC}"
ssh root@192.168.1.20

