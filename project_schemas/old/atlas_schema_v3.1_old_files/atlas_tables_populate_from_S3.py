import datajoint as dj
import numpy as np
from minio import Minio
import json
import yaml
import sys, os

sys.path.append('./lib')
from utilities import *
from initialization_of_db import *

# Fp to file pointers assumes to be 'setup/credFiles.yaml', otherwise pass it directly
# Load AWS Credentials
# `creds` needs the following fields: 'access_key', 'secret_access_key
s3_client = get_s3_client()
# Load Datajoint Credentials
# `dj_creds` needs the following fields: 'user', 'passwd'
dj_creds = get_dj_creds()

# Connect to datajoint server
dj.conn()

# Define which schema you're using
schema = dj.schema('common_atlas_v3')
schema.spawn_missing_classes()


for brain_name in brain_names_list:

    print("\nAdding "+brain_name+' to the database')
    
    # Fill in MOUSE info for UCSD
    if brain_name == 'UCSD001':
        Mouse.insert1(dict(mouse=brain_name,
                   date_of_birth='2020-01-01',
                   sex='M',
                   genotype='C57',
                   weight=-1,
                   bred='Unknown')
                 ,skip_duplicates=True)
    else: # Fill in MOUSE info non-UCSD mice
        Mouse.insert1(dict(mouse=brain_name,
                       date_of_birth='2017-12-05',
                       sex='M',
                       genotype='C57',
                       weight=-1,
                       bred='Unknown')
                     ,skip_duplicates=True)
        
    # Fill in HISTOLOGY info
    Histology.insert1((brain_name,
                   'Unknown', # region
                   '20', # thickness
                   brain_names_dic[brain_name][3],  # orientation
                   brain_names_dic[brain_name][0],  # counter_stain
                   brain_names_dic[brain_name][1],  # lab
                   'unknown') # series  
                 ,skip_duplicates=True)
    
    # Try to load STACK_sorted_filenames.txt from AWS S3, on failure the default values are filled
    try:
        _, total_slices, valid_slices = get_sorted_filenames( s3_client, \
                                                             stack_name=brain_name, \
                                                             return_type="string" )
    except Exception as e:
        total_slices   = -1
        valid_slices   = -1
        print('No sorted_filenames.txt exists for '+brain_name)
        print(e)

    # Fill in STACK info for UCSD
    if brain_name == 'UCSD001':
        Stack.insert1(dict(mouse=brain_name,
                                stack_name=brain_name,
                                num_slices       = total_slices,
                                num_valid_slices = valid_slices,
                                channels         = brain_names_dic[brain_name][0].count('/') + 1,
                                human_annotated  = brain_names_dic[brain_name][2],
                                planar_resolution_um = 0.325,
                                section_thickness_um = 20)
                     ,skip_duplicates=True)
    else:# Fill in STACK info for non-UCSD brains
        Stack.insert1(dict(mouse=brain_name,
                                stack_name=brain_name,
                                num_slices       = total_slices,
                                num_valid_slices = valid_slices,
                                channels         = brain_names_dic[brain_name][0].count('/') + 1,
                                human_annotated  = brain_names_dic[brain_name][2],
                                planar_resolution_um = 0.46,
                                section_thickness_um = 20)
                     ,skip_duplicates=True)
        
    Slice.populate()