from sys import version_info

import os
from os import mkdir
from os.path import isdir,isfile,expanduser

py3 = version_info[0] > 2 #creates boolean value for test that Python major version > 2

line_1 = 'ENV_DIR : '
line_2 = 'DWNLD_ROOT_DIR : '


def ask_for_input( prompt ):
    if py3:
        response = input( prompt )
    else:
        response = raw_input( prompt )
    return response

def remove_spaces( response ):
    response = response.replace(' ','')
    return response

# No longer necessary to ask for environment directory as it can be computed
# print('\n** The environment directory is the absolute filepath to the `Datajoint_Interface` github repo. **')
# env_dir = ask_for_input( prompt="Please enter the environment directory: ")
# env_dir = remove_spaces( env_dir )

print('\n** The default download directory is where files from S3 will download to. **')
download_dir = ask_for_input( prompt="Please enter the default download directory: ")
download_dir = remove_spaces( download_dir )


home = expanduser('~')
conf_dir=home+'/.orofacial'

if not isdir(conf_dir):
    mkdir(conf_dir)
    
    
# This code will find the 'env_dir' automatically
# Get the absolute filepath of this python script regardless of working directory
script_dir = os.path.abspath(__file__)
# Remove the filename of this python script from the string (/define_filepaths.py)
index_of_fn = script_dir.rfind('/')
script_dir=script_dir[:index_of_fn]
# Remove the last folder name from the string (setup)
index_of_last_folder = script_dir.rfind('/')
env_dir = script_dir[:index_of_last_folder+1]

print('')
print( 'Atlas ENV_DIR: ',env_dir )
print( 'default DWNLD_ROOT_DIR: ',download_dir)

with open(conf_dir+'/filepaths.yaml', 'w' ) as file:
    file.write(line_1+env_dir+'\n')
    file.write(line_2+download_dir)
