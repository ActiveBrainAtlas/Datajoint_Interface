import datajoint as dj
import numpy as np
from minio import Minio
import json
import sys


def get_client():
    return Minio( 's3.amazonaws.com', secure=True, **creds)


global creds
# load S3 access_key and secret_key
# The file s3-creds.json should contain the following:
# {"access_key": "...", "secret_key": "..."}
if sys.platform=='darwin':
    with open('/Users/newberry/Desktop/atlas_data/alex_aws_credentials.json') as f:
        creds = json.load(f)
elif sys.platform=='linux':
    with open('/mnt/c/Users/Alex/Documents/json_credentials/alex_aws_credentials.json') as f:
        creds = json.load(f)
    
global client
client = get_client()


global brain_names_dic
# 'STACK': [ stain, source, human_annotated, orientation ]
brain_names_dic = {'MD585':['thionin','CSHL',True,'sagittal'],
                    'MD589':['thionin','CSHL',True,'sagittal'],
                    'MD590':['thionin','CSHL',False,'sagittal'],
                    'MD591':['thionin','CSHL',False,'sagittal'],
                    'MD592':['thionin','CSHL',False,'sagittal'],
                    'MD593':['thionin','CSHL',False,'sagittal'],
                    'MD594':['thionin','CSHL',True,'sagittal'],
                    'MD595':['thionin','CSHL',False,'sagittal'],
                    'MD598':['thionin','CSHL',False,'sagittal'],
                    'MD599':['thionin','CSHL',False,'sagittal'],
                    'MD602':['thionin','CSHL',False,'sagittal'],
                    'MD603':['thionin','CSHL',False,'sagittal'],
                    'CHATM2':['NTB/ChAT','UCSD',False,'sagittal'],
                    'CHATM3':['NTB/ChAT','UCSD',False,'sagittal'],
                    'CSHL2':['?','UCSD',False,'sagittal'],
                    'MD658':['NTB/PRV','CSHL',False,'sagittal'],
                    'MD661':['NTB/dGRV','CSHL',False,'sagittal'],
                    'MD662':['NTB/dGRV','CSHL',False,'sagittal'],
                    'MD635':['NTB','CSHL',False,'sagittal'],
                    'MD636':['thionin','CSHL',False,'horozontal'],
                    'MD639':['thionin','CSHL',False,'coronal'],
                    'MD642':['NTB/Thionin','CSHL',False,'sagittal'],
                    'MD652':['NTB/Thionin','CSHL',False,'sagittal'],
                    'MD653':['NTB/Thionin','CSHL',False,'sagittal'],
                    'MD657':['NTB/PRV-eGFP','CSHL',False,'sagittal'],
                    'MD175':['thionin','CSHL',False,'coronal'],
                    'UCSD001':['NTB','UCSD',False,'sagittal']}
brain_names_list = brain_names_dic.keys()


#                  OBJECT INFO
        # bucket_name: mousebraindata-open 
        # object_name: b'MD657/MD657-F1-2017.02.17-17.39.26_MD657_1_0001.png' 
        # last_modified: 2018-08-29 04:16:33+00:00 
        # etag: 2ea51d17c3b6ad95209ec65aa59325cc 
        # size: 900864 
        # content_type: None
        # is_dir: False
        # metadata: None
def get_raw_files( stack, returntype="string" ):
    client = get_client()
    bucket_name='mousebrainatlas-rawdata'
    if 'UCSD' in stack:
        rel_fp = 'UCSD_data/'+stack+'/'
    else: 
        rel_fp = 'CSHL_data/'+stack+'/'
    # 'Objects' contains information on every item in the specified path
    objects = client.list_objects(bucket_name=bucket_name, prefix=rel_fp)
    
    if returntype=="string":
        fp_data = ""
    elif returntype=="list":
        fp_data = []
        
    num_files = 0
    for object in objects:
        filename = object.object_name
        if filename.endswith('_raw.tif') or filename.endswith('_lossless.jp2'):
            num_files += 1
            if returntype=="string":
                if fp_data=="":
                    fp_data = filename
                else:
                    fp_data = fp_data+"|"+filename
            elif returntype=="list":
                fp_data.append(filename)

    return fp_data

def get_processed_files( stack, prep_id="2", version="", resol="thumbnail", returntype="string" ):
    # prep_id only used as a string
    prep_id = str(prep_id)
    # add the underscore prefix if does not currently exist
    if version!="" and version[0]!="_":
        version = "_"+version
    
    
    client = get_client()
    bucket_name='mousebrainatlas-data'
    rel_fp = 'CSHL_data_processed/'+stack+'/'+stack+'_prep'+prep_id+'_'+resol+'/'
    # 'Objects' contains information on every item in the specified path
    objects = client.list_objects(bucket_name=bucket_name, prefix=rel_fp)
    
    if returntype=="string":
        fp_data = ""
    elif returntype=="list":
        fp_data = []
    
    num_files = 0
    for object in objects:
        filename = object.object_name
        if filename.endswith('.tif'):
            num_files += 1
            if returntype=="string":
                if fp_data=="":
                    fp_data = filename
                else:
                    fp_data = fp_data+"|"+filename
            elif returntype=="list":
                fp_data.append(filename)
#             print(filename)
            
    # If no valid could be found, then try using "lossless" instead of "raw"
    if (fp_data=="" or fp_data==[]) and resol=="raw":
        fp_data = get_processed_files( stack, prep_id=prep_id, version=version, \
                                      resol="lossless", returntype=returntype )
    
    return fp_data


def get_sorted_filenames( stack_name, returntype="string" ): # string, dictionary, list
    sorted_filenames = client.get_object('mousebrainatlas-data', 'CSHL_data_processed/'+stack_name+\
                                         '/'+stack_name+'_sorted_filenames.txt').data.decode()
    separator = "|"

    if returntype=="string":
        sorted_fn_data = ""
    elif returntype=="dictionary":
        sorted_fn_data = {}
    elif returntype=="list":
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


        if returntype=="string":
            sorted_fn_data = sorted_fn_data + line + separator
        elif returntype=="dictionary":
            sorted_fn_data[ slice_number ] = slice_name
        elif returntype=="list":
            sorted_fn_data.append( str(line) )

    return [sorted_fn_data, total_slices, valid_slices]
