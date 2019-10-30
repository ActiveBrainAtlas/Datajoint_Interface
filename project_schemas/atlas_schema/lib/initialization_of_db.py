# This is code used for the initial population of the database. Is not needed unless recreating the database from scratch.


# Load a dictionary of all brains assiciated with the Active Atlas Project
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


def get_raw_files( s3_client, stack, returntype="string" ):
    # Raw files located: mousebrainatlas-rawdata/CSHL_data/[stack]/
    bucket_name='mousebrainatlas-rawdata'
    if 'UCSD' in stack:
        rel_fp = 'UCSD_data/'+stack+'/'
    else: 
        rel_fp = 'CSHL_data/'+stack+'/'
    # 'Objects' contains information on every item in the specified path
    objects = s3_client.list_objects(bucket_name=bucket_name, prefix=rel_fp)
    
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

def get_processed_files( s3_client, stack, prep_id="2", version="", resol="thumbnail", returntype="string" ):
    # prep_id only used as a string
    prep_id = str(prep_id)
    # add the underscore prefix if does not currently exist
    if version!="" and version[0]!="_":
        version = "_"+version
    
    
    # CHANGE TO ENV VARIABLE * * * * * * * * * * * * 
    bucket_name='mousebrainatlas-data'
    rel_fp = 'CSHL_data_processed/'+stack+'/'+stack+'_prep'+prep_id+'_'+resol+'/'
    # 'Objects' contains information on every item in the specified path
    objects = s3_client.list_objects(bucket_name=bucket_name, prefix=rel_fp)
    
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
        fp_data = get_processed_files( s3_client, stack, prep_id=prep_id, version=version, \
                                      resol="lossless", returntype=returntype )
    
    return fp_data