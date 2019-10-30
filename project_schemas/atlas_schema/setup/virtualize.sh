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
