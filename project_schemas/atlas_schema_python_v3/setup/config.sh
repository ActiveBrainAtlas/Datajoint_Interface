#!/bin/bash

##################################################
## LOADING ENVIRONMENT VARIABLES FROM YAML FILE ##
# Load contents of yaml file into a string
file=`cat ../../../.setup_files/filepaths.yaml`
contents=`echo $file`

# Defining some strings that need to be replaced in the file contents of the yaml file
blank_string=''
replace_1='ENV_DIR : '
replace_2='DWNLD_ROOT_DIR : '

# Replace strings in the yaml file with a blank string, essentially removing it
# Removes 'ENV_DIR : '
contents="${contents/$replace_1/$blank_string}"
# Removes 'DWNLD_ROOT_DIR : '
contents="${contents/$replace_2/$blank_string}"

# Set equal to $contents, excluding everything after the first space
export ENV_DIR=${contents% *}
# Set equal to $contents, excluding everything before the last space
export DWNLD_ROOT_DIR=${contents#* }

# User must change the beginning on ENV_DIR to match where this project is located
echo 'ENV_DIR:'
echo $ENV_DIR
# User must change DWNLD_ROOT_DIR to where they files downloaded from AWS S3 by default
echo 'DWNLD_ROOT_DIR:'
echo $DWNLD_ROOT_DIR
echo ''
## DONE LOADING ENVIRONMENT VARIABLES FROM YAML FILE ##
##################################################

export BUCKET_RAWDATA="mousebrainatlas-rawdata-backup"
export BUCKET_DATA="mousebrainatlas-data"

virtualenvdir="VirtEnv"
##################################################
## Defining colors ##
red='\e[1;31m'
purple='\e[1;35m'
green='\e[1;32m'
cyan='\e[1;36m'
NC='\033[0m' # No Color
## Done defining colors ##
##################################################

if [ ! -d $virtualenvdir ]; then
	echo ""
	echo -e "${red}Creating a virtual environment${NC}"
	virtualenv -p python3 $ENV_DIR/$virtualenvdir
fi

source $ENV_DIR/$virtualenvdir/bin/activate

pip3 install -r $ENV_DIR/setup/requirements.txt
PATH=$PATH:$ENV_DIR/$virtualenvdir/lib/python3.6/site-packages/
