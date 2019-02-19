#!/bin/bash

# User must change the beginning on ENV_DIR to match where this project is located
# export ENV_DIR="/home/alexn/github_repos/Datajoint_Interface/project_schemas/atlas_schema_python_v3"
export ENV_DIR="/Users/newberry/code/git_projects/Datajoint_Interface/project_schemas/atlas_schema_python_v3"
# User must change DWNLD_ROOT_DIR to where they files downloaded from AWS S3 by default
# export DWNLD_ROOT_DIR="/mnt/c/Users/Alex/Documents/Atlas_Files/"
export DWNLD_ROOT_DIR="/Users/newberry/Documents/ATLAS_DOWNLOADS/"

###---###---### Don't change anything below here ###---###---###
export BUCKET_RAWDATA="mousebrainatlas-rawdata-backup"
export BUCKET_DATA="mousebrainatlas-data"

virtualenvdir="VirtEnv"
##################################################
# Defining colors
red='\e[1;31m'
purple='\e[1;35m'
green='\e[1;32m'
cyan='\e[1;36m'
NC='\033[0m' # No Color
##################################################

if [ ! -d $virtualenvdir ]; then
	echo ""
	echo -e "${red}Creating a virtual environment${NC}"
	virtualenv -p python3 $ENV_DIR/$virtualenvdir
fi

source $ENV_DIR/$virtualenvdir/bin/activate

pip3 install -r $ENV_DIR/setup/requirements.txt
PATH=$PATH:$ENV_DIR/$virtualenvdir/lib/python3.6/site-packages/
