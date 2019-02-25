import datajoint as dj  # automatically loads dj.config from the file `dj_local_conf.json` if it exists
import numpy as np
import json
from subprocess import call
import yaml
import sys, os
import pandas as pd
import traceback

# import orofacial utilities
sys.path.append('../lib')
from utilities import *
from initialization_of_db import *

sys.path.append('./Cell_Extraction_Scripts/')

from process_file import process_file
from lib.utils import *

yaml=os.environ['yaml']
config = configuration(yaml)
params=config.getParams()

#print(params)
#sys.exit()

scripts_dir=params['paths']['scripts_dir']
local_data=params['paths']['data_dir']
bucket=os.environ['BUCKET_RAWDATA']
# Connect to datajoint server
dj.conn()

# Define which schema you're using
schema = dj.schema('common_atlas_v3')
schema.spawn_missing_classes()

@schema
class ExtractedCells(dj.Computed):
    definition="""
    -> Slice
    ---
    patches_fn: varchar(200) # pointer to log and visualization tgz file.
    extracted_fn: varchar(200) # pointer to extracted patches tgz file.
    extracted_size: int # size of extracted file (in MB)
    """
    def make(self,key):
        print('extracting for',key)
        raw_s3_fp = (Slice & key).fetch1('raw_s3_fp')

        if len(raw_s3_fp)>0:
            first_slash=raw_s3_fp.rfind('/')
            s3_directory='s3://'+bucket+'/'+raw_s3_fp[:first_slash]
            stem=raw_s3_fp[first_slash+1:-4]
            print('processing %s, local_data=%s, s3_directory=%s, scripts_dir=%s'%(stem,local_data,s3_directory,scripts_dir))
            try:
                patches_fn, extracted_fn, extracted_size =process_file(local_data,s3_directory,stem,scripts_dir,params,yaml)
                key['patches_fn']=patches_fn
                key['extracted_fn']=extracted_fn
                key['extracted_size']=int(extracted_size/1000000)
# could not insert key= {'extracted_size': 56, 'slice_num': 10, 'extracted_fn': 'MD585-IHC4-2015.07.18-07.01.12_MD585_1_0010_lossless_extracted.tgz', 'mouse': 'MD585', 'patches_fn': 'MD585-IHC4-2015.07.18-07.01.12_MD585_1_0010_lossless_patches.tgz'
            except Exception:
                traceback.print_exc(file=sys.stderr)

            print('Trying to insert key=',key)
            try:
                self.insert1(key)
            except Exception:
                print('could not insert key=',key)
                traceback.print_exc(file=sys.stderr)

    
extraction=ExtractedCells()
#extraction.make({'mouse': 'MD585', 'slice_num': 10})
extraction.populate(reserve_jobs=True)

