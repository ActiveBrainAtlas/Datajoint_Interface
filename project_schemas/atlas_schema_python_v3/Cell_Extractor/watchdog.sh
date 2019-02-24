#!/usr/bin/env bash
export PATH="/home/ubuntu/bin:/home/ubuntu/.local/bin:/home/ubuntu/KDU7A2_Demo_Apps_for_Centos7-x86-64_170827/:/home/ubuntu/shapeology_code/scripts/:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin"
export LD_LIBRARY_PATH=/home/ubuntu/KDU7A2_Demo_Apps_for_Centos7-x86-64_170827/
export yaml=/home/ubuntu/shapeology_code/scripts/shape_params-aws.yaml
echo $LD_LIBRARY_PATH >> /home/ubuntu/watchdog.log
source /home/ubuntu/Datajoint_Interface/project_schemas/atlas_schema_python_v3/setup/config.sh

cd /home/ubuntu/Datajoint_Interface/project_schemas/atlas_schema_python_v3/Cell_Extractor
./watchdog.py >> /home/ubuntu/watchdog.log
