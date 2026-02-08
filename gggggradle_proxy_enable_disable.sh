#!/bin/bash
RED='\033[1;31m'
GREEN='\033[0;32m'
BLUE='\033[0;36m'
YELLOW='\033[1;33m'
ORANGE='\033[0;33m'
CYAN='\033[0;36m'


NC='\033[0m' # No Color

if [[ $1 ]]; then


	if [[ "$1" == o* ]]; then
	   echo "opening gradle.properties"
	   	if [ -f ~/.gradle/gradle.properties ]; then
       			/home/x/Public/android-studio/bin/studio ~/.gradle/gradle.properties
   		else
	        	/home/x/Public/android-studio/bin/studio ~/.gradle/gradle.properties_
	   	fi
	   exit 1
	fi
	
   if [ ! -f ~/.gradle/gradle.properties ]; then
       echo -e "${RED}[STATE] PROXY IS DISABLE${NC}"
   else
        echo -e "${GREEN}[STATE] *** PROXY IS ENABLED${NC}"
   fi
   
else
   if [ -f ~/.gradle/gradle.properties ]; then
       mv ~/.gradle/gradle.properties ~/.gradle/gradle.properties_
       echo -e "${RED}PROXY DISABLE${NC}"
   else
       mv ~/.gradle/gradle.properties_ ~/.gradle/gradle.properties
        echo -e "${GREEN}*** PROXY ENABLED ***${NC}"
   fi

fi