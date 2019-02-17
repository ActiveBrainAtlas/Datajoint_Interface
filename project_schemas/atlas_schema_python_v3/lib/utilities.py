import datajoint as dj
import numpy as np
from minio import Minio
import json
import sys
import yaml

def get_dj_creds( credential_file_pointers='setup/credFiles.yaml' ):
    """
    Returns Datajoint credentials which are used for initial connection to a database.
    
    Takes in fp to credential file pointers, defaults to 'setup/credFiles.yaml'.
    """
    credFiles = yaml.load(open( credential_file_pointers,'r'))
    
    # Load Datajoint Credentials
    with open( credFiles['dj_fp'] ) as f:
        dj_creds = json.load(f)
    return dj_creds

def get_s3_client( credential_file_pointers='setup/credFiles.yaml' ):
    """
    Return the AWS S3 client which must be passed to every function that accesses it.
    
    Takes in fp to credential file pointers, defaults to 'setup/credFiles.yaml'.
    """
    credFiles = yaml.load(open( credential_file_pointers,'r'))
    
    # Load AWS Credentials
    # `creds` needs the following fields: 'access_key', 'secret_access_key'
    with open( credFiles['aws_fp'] ) as f:
        creds = json.load(f)
        
    return Minio( 's3.amazonaws.com', secure=True, **creds)


def get_sorted_filenames( s3_client, stack_name, return_type="string" ): # string, dictionary, list
    """
    Pass in the stack_name and s3_client loaded from 'get_s3_client()'. Accesses S3 and returns the 'sorted_filenames.txt' file, which is the master list of all slices in a stack.
    
    Third argument is 'return_type', which can be a string, dictionary, or list. Defaults to string with '|' as a seperator.
    """
    client = get_s3_client()
    sorted_filenames = client.get_object('mousebrainatlas-data', 'CSHL_data_processed/'+stack_name+\
                                         '/'+stack_name+'_sorted_filenames.txt').data.decode()
    separator = "|"

    if return_type=="string":
        sorted_fn_data = ""
    elif return_type=="dictionary":
        sorted_fn_data = {}
    elif return_type=="list":
        sorted_fn_data = []


    # Convert to a list containing each line
    sorted_filenames_list = sorted_filenames.split('\n')

    total_slices = len(sorted_filenames_list)
    valid_slices = 0


    for line in sorted_filenames_list:
        line = line.rstrip()
        line.replace("\n","")
        line.replace("\r","")

        if len(line.split(' ')) != 2:
            continue

        slice_name, slice_number = line.split(' ')
        slice_name = slice_name.replace(" ", "")
        slice_number = slice_number.replace(" ", "")
        if slice_name != 'Placeholder':
                     valid_slices += 1


        if return_type=="string":
            sorted_fn_data = sorted_fn_data + line + separator
        elif return_type=="dictionary":
            sorted_fn_data[ slice_number ] = slice_name
        elif return_type=="list":
            sorted_fn_data.append( str(line) )

    return [sorted_fn_data, total_slices, valid_slices]

def s3_dir_is_empty( s3_client, bucket_name, filepath ):
    """
    Pass in the s3_client, bucket_name, and filepath. This function will return False if there are no files present, True if there are.
    """
    objects = client.list_objects(bucket_name=bucket_name, \
                                prefix=filepath)
    
    objects_exist = False
    for object in objects:
            objects_exist = True
            break
    return not objects_exist



