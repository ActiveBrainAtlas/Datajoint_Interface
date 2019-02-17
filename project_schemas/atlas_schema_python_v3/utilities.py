import datajoint as dj
import numpy as np
from minio import Minio
import json
import sys

def get_dj_client( credential_file_pointers='config/credFiles.yaml' ):
    """
    
    """
    credFiles = yaml.load(open( credential_file_pointers,'r'))
    
    # Load Datajoint Credentials
    with open( credFiles['dj_fp'] ) as f:
        dj_creds = json.load(f)
    return dj_creds

def get_s3_client( credential_file_pointers='config/credFiles.yaml' ):
    """
    
    """
    credFiles = yaml.load(open( credential_file_pointers,'r'))
    
    # Load AWS Credentials
    # `creds` needs the following fields: 'access_key', 'secret_access_key'
    with open( credFiles['aws_fp'] ) as f:
        creds = json.load(f)
        
    return Minio( 's3.amazonaws.com', secure=True, **creds)


def get_sorted_filenames( stack_name, return_type="string", client ): # string, dictionary, list
    """
    
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

def s3_dir_is_empty( bucket_name, filepath, client):
    objects = client.list_objects(bucket_name=bucket_name, \
                                prefix=filepath)
    
    objects_exist = False
    for object in objects:
            objects_exist = True
            break
    return not objects_exist



