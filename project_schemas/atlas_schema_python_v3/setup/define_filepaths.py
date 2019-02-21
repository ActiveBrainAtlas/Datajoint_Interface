from sys import version_info

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


print('\n** The environment directory is the absolute filepath to the `Datajoint_Interface` github repo. **')
env_dir = ask_for_input( prompt="Please enter the environment directory: ")
env_dir = remove_spaces( env_dir )

print('\n** The default download directory is where files from S3 will download to. **')
download_dir = ask_for_input( prompt="Please enter the default download directory: ")
download_dir = remove_spaces( download_dir )

print()
print( env_dir)
print( download_dir)

with open('../../../.setup_files/filepaths.yaml', 'w' ) as file:
    file.write(line_1+env_dir+'\n')
    file.write(line_2+env_dir)