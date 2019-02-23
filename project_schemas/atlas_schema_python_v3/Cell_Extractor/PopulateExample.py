
import datajoint as dj  # automatically loads dj.config from the file `dj_local_conf.json` if it exists
import numpy as np
import json
from subprocess import call
import yaml
import sys, os
import pandas as pd

sys.path.append('../lib')
from utilities import *
from initialization_of_db import *

# Connect to datajoint server
dj.conn()

# Define which schema you're using
schema = dj.schema('common_atlas_v3')
schema.spawn_missing_classes()

@schema
class Process(dj.Computed):
    definition="""
    -> Slice
    ---
    size:int #size of raw file
    """
    bucket=os.environ['BUCKET_RAWDATA']
    credFiles='/Users/yoavfreund/VaultBrain/credFiles.yaml'
    client=get_s3_client(credFiles)
    def make(self,key):
        print('populating for',key,end='')
        raw_s3_fp = (Slice & key).fetch1('raw_s3_fp')
        if len(raw_s3_fp)>0:
            #print('raw_s3_fp=',raw_s3_fp,end='')
            report=self.client.stat_object(self.bucket,raw_s3_fp)
            key['size']=int(report.size/1000000)
            #print('size=',key['size'],'MB')
        else:
            key['size']=-1
        print(' inserting',key)
        try:
            self.insert1(key)
        except:
            print('could not insert key=',key)


        
sizes=Process()
#sizes.drop()
(sizes & dict(mouse='MD585')).populate(suppress_errors=True)
