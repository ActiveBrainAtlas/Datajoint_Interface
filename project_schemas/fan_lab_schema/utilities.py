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

# Load excel spreadsheet with CSHL metadata
import xlrd 
file_name = 'CSHL_Brain_Metadata.xlsx'

wb = xlrd.open_workbook(file_name) 
sheet = wb.sheet_by_index(1) 
#print( sheet.cell_value(0, 0) )
  
# Extracting number of rows & cols
nrows = sheet.nrows
ncols = sheet.ncols
#print( nrows )
#print( ncols )