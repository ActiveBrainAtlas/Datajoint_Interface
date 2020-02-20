import subprocess
import os, sys
import cv2
#sys.path.append(os.path.join(os.environ['REPO_DIR'], 'utilities'))
#from data_manager_v2 import DataManager


def get_czi_metadata( czi_fp, get_full_metadata=False ):
    command = ['/usr/local/share/bftools/showinf', '-nopix', czi_fp ]
    print(czi_fp)
    # "showinf -nopix" will return the metadata of a CZI file
    czi_metadata_full = subprocess.check_output( command )
    czi_metadata_full = czi_metadata_full.decode("utf-8") 
    
    if get_full_metadata:
        return czi_metadata_full
    
    # I seperate the metadata into 3 seperate sections
    czi_metadata_header = czi_metadata_full[0:czi_metadata_full.index('\nSeries #0')]
    czi_metadata_series = czi_metadata_full[0:czi_metadata_full.index('\nReading global metadata')]
    czi_metadata_global = czi_metadata_full[czi_metadata_full.index('\nReading global metadata'):]

    # This extracts the 'series' count.
    # Each series is a tissue sample at a certain resolution
    #  or an erroneous thingy
    series_count = int( czi_metadata_header[
        czi_metadata_header.index('Series count = ')+15:] )

    # Series #0 should be the first tissue sample at full resolution.
    # Series #1 tends to be this same tissue sample at half the resolution.
    # This continues halving resolution 5-6 times in succession. We only
    # want the full resolution tissue series so we ignore those with dimensions
    # that are much smaller than expected.
    expected_min_width = 9000
    expected_min_height = 9000

    metadata_dict = {}

    for series_i in range(series_count):
        search_str = 'Series #'

        # If the last series, extract to end of file
        if series_i == series_count-1:
            czi_metadata_series_i = czi_metadata_series[
                czi_metadata_series.index('Series #'+str(series_i)) : ]
        # Otherwise extract metadata from Series(#) to Series(#+1)
        else:
            czi_metadata_series_i = czi_metadata_series[
                czi_metadata_series.index('Series #'+str(series_i)) : 
                czi_metadata_series.index('Series #'+str(series_i+1))]

        # Extract width and height
        width_height_data = czi_metadata_series_i[ czi_metadata_series_i.index('Width'):
                                                   czi_metadata_series_i.index('\n\tSizeZ')]
        width, height = width_height_data.replace('Width = ','').replace('Height = ','').split('\n\t')

        metadata_dict[series_i] = {}
        metadata_dict[series_i]['width'] = width
        metadata_dict[series_i]['height'] = height
        
        # Extract number of channels
        channel_count_index = czi_metadata_series_i.index('SizeC = ')+8
        channel_count = int( czi_metadata_series_i[ channel_count_index: channel_count_index+1] )
        
        metadata_dict[series_i]['channels'] = channel_count
       
    for channel_i in range( metadata_dict[0]['channels'] ):
        # Extract channel names
        str_to_search = 'Information|Image|Channel|Name #'+str(channel_i+1)+': '
        str_index = czi_metadata_global.index(str_to_search)
        channel_name = czi_metadata_global[str_index+len(str_to_search):
                                           czi_metadata_global.find('\n', str_index)]
        metadata_dict['channel_'+str(channel_i)+'_name'] = channel_name
        
    return metadata_dict

def get_fullres_series_indices( metadata_dict ):
    fullres_series_indices = []
    
    series = []
    for key in metadata_dict.keys():
        try:
            int(key)
            series.append(int(key))
        except:
            #del metadata_dict[key]
            continue
    #last_series_i = max(metadata_dict.keys())
    last_series_i = max(series)
    metadata_dict = {k: metadata_dict[k] for k in series}
    
    series_0_width = int( metadata_dict[0]['width'] )
    series_0_height = int( metadata_dict[0]['height'] )
    
    for series_curr in metadata_dict.keys():
        #try:
        #    int(series_curr)
        #xcept:
        #    # Skip keys that are not integers
        #    continue
        
        # Series 0 is currently assumed to be real, fullres tissue
        if series_curr != 0:
            series_curr_width = int( metadata_dict[series_curr]['width'] )
            series_prev_width = int( metadata_dict[series_curr-1]['width'] )
            
            series_prev_width_halved = series_prev_width/2
            
            # If the curr series is about half the size of the previous series
            # this indicates that it is not a new tissue sample, just a 
            # downsampled version of the previous series.
            if abs( series_curr_width-series_prev_width_halved ) < 5:
                continue
            # If this series is suspisciously small, it is not likely to be fullres
            # Currently this assumed that series#0 is fullres 
            if series_curr_width < series_0_width*0.5:
                continue
                
        # We ignore the last two series.
        # 2nd last should be "label image"
        # last should be "macro image"
        if series_curr >= last_series_i-2:
            continue
                
        fullres_series_indices.append( series_curr )
        
    return fullres_series_indices

def get_list_of_czis_in_folder( folder ):
    command = ['ls', folder]

    possible_czi_files = subprocess.check_output( command ).split( '\n' )
    possible_czi_files.remove('')
    
    czi_files = []

    for file_to_check in czi_files:
        if '.czi' not in file_to_check:
            continue
            #czi_files.remove(file_to_check)
        else:
            czi_files.append(file_to_check)
            
    czi_files = []
    
    for possible_czi in os.listdir( folder ):
        if '.czi' in possible_czi:
            czi_files.append(possible_czi)
            
    return czi_files

def get_tiff_fp_from_matching_str( folder, str_to_match ):
    command = ['ls', folder]

    possible_tif_files = subprocess.check_output( command ).split( '\n' )
    possible_tif_files.remove('')
    
    tif_files = []

    for file_to_check in possible_tif_files:
        if '.tif' not in file_to_check:
            continue
        else:
            tif_files.append(file_to_check)
            
    
    for tif_file in tif_files:
        if str_to_match in tif_file:
            #print(str_to_match)
            #print(tif_file)
            return tif_file
    return None
    
def copy_extracted_tiffs_to_proper_locations( stack, tiff_target_folder, main_channel):
    # "Ancillary Channel list contains all possible channel numbers except for the main channel
    ancillary_channel_list = []
    for i in range(0,4):
        if i == main_channel:
            continue
        else:
            ancillary_channel_list.append(i)
    
    for fn in os.listdir(tiff_target_folder):
        full_fn = os.path.join(tiff_target_folder, fn)
        
        for ancillary_channel in ancillary_channel_list:
            # e.g.'C2' will appear in images of the third channel, use this to tell which channel each image is
            
            # If this image is a secondary/ancillary channel
            if 'C'+str(ancillary_channel) in fn:
                destination_fp = os.path.join( DataManager.get_images_root_folder(stack), 
                                              stack+'_raw_C'+str(ancillary_channel_list.index(ancillary_channel)), 
                                              fn[0:fn.index('.tif')]+'_raw.tif')
                # Create directory if it doesn't exist
                try:
                    os.makedirs( os.path.split(destination_fp)[0] )
                except:
                    pass
                command = ['cp', full_fn, destination_fp]
                subprocess.call( command )
                
            # If this image is the main channel, copy to the main folder
            elif 'C'+str(main_channel) in fn:
                destination_fp = os.path.join( DataManager.get_images_root_folder(stack), 
                                              stack+'_raw', fn[0:fn.index('.tif')]+'_raw.tif')
                # Create directory if it doesn't exist
                try:
                    os.makedirs( os.path.split(destination_fp)[0] )
                except:
                    pass
                command = ['cp', full_fn, destination_fp]
                subprocess.call( command )

def extract_tiff_from_czi_all_channels( fn_czi, tiff_target_folder, series_i ):
    # The name of the tiff file
    # %t is time, %z is z height, %s is series #, %c is channel #
    #target_tiff_fn = os.path.join( tiff_target_folder, '%n_C%c_W%w.tif' )
    target_tiff_fn = os.path.join( tiff_target_folder, '%n_C%c_W%w.tif' )
    
    command = ['bfconvert', '-bigtiff', '-compression', 'LZW', '-separate', 
               '-series', str(series_i), fn_czi, target_tiff_fn]
    
    subprocess.call( command )


def extract_tiff_from_czi( fn_czi, tiff_target_folder, series_i, channel, fullres_series_indices=-1, auto_rename=False ):
    # The name of the tiff file
    # %t is time, %z is z height, %s is series #, %c is channel #
    #target_tiff_fn = os.path.join( tiff_target_folder, '%n_S%s_C%c_%w.tif' )
    #target_tiff_fn = os.path.join( tiff_target_folder, '%n_C%c_%w.tif' )
    target_tiff_fn = os.path.join( tiff_target_folder, '%n_C%c_%w.tif' )
    
    command = ['bfconvert', '-bigtiff', '-compression', 'LZW', '-separate', 
               '-series', str(series_i), '-channel', str(channel), fn_czi, target_tiff_fn]
    print('        Command: `'+' '.join(command)+'`\n')
    subprocess.call( command )
    
    #print(fullres_series_indices)
    
    if auto_rename and fullres_series_indices>=0:
        # We will search for a tiff file that contains partial_target_tiff_fn in its name
        partial_target_tiff_fn = os.path.basename(target_tiff_fn)
        #partial_target_tiff_fn = partial_target_tiff_fn.replace('%n', os.path.basename(fn_czi)+' #'+str(series_i+1).zfill(2))
        partial_target_tiff_fn = partial_target_tiff_fn.replace('%n', os.path.basename(fn_czi)+' #'+str(series_i+1) )
        partial_target_tiff_fn = partial_target_tiff_fn.replace('%c', str(channel)).replace('%w.tif', '')
        section_num_padded_zeros = False
        
        # The name of the corresponding tiff file
        curr_tiff_filename = get_tiff_fp_from_matching_str( tiff_target_folder, str_to_match=partial_target_tiff_fn )
        
        if curr_tiff_filename==None:
            # Same operation as above on failure, except we pad the section number ( using zfill(2) )
            # We will search for a tiff file that contains partial_target_tiff_fn in its name
            partial_target_tiff_fn = os.path.basename(target_tiff_fn)
            partial_target_tiff_fn = partial_target_tiff_fn.replace('%n', os.path.basename(fn_czi)+' #'+str(series_i+1).zfill(2))
            partial_target_tiff_fn = partial_target_tiff_fn.replace('%c', str(channel)).replace('%w.tif', '')
            # The name of the corresponding tiff file
            curr_tiff_filename = get_tiff_fp_from_matching_str( tiff_target_folder, str_to_match=partial_target_tiff_fn )
            section_num_padded_zeros = True
            
        print(curr_tiff_filename)
        old_tif_fp = os.path.join( tiff_target_folder, curr_tiff_filename)
        print(old_tif_fp)
        if section_num_padded_zeros:
            new_tif_fp = old_tif_fp.replace( '.czi #'+str(series_i+1).zfill(2), \
                                            '_S'+str(fullres_series_indices.index(series_i)+1).zfill(2) )
        if not section_num_padded_zeros:
            new_tif_fp = old_tif_fp.replace( '.czi #'+str(series_i+1), \
                                            '_S'+str(fullres_series_indices.index(series_i)+1).zfill(2) )
        print( 'Converting '+old_tif_fp+' to '+new_tif_fp )
        
        # Read the image we just extracted
        #img = cv2.imread( old_tif_fp )
        #from skimage.io import imread
        #img = cv2.imread( old_tif_fp )
        
        from skimage.io import imread
        try:
            print('- Loading image using skimage.io.imread -')
            img = imread( old_tif_fp )
        except Exception as e:
            print(str(e))
            try:
                print('- Loading image using cv2.imread -')
                img = cv2.imread( old_tif_fp )
            except Exception as e:
                print(str(e))
                print('Aborting the loading/renaming process')
                return
        
        # If image is shaped properly
        if len(img.shape)==3:
            try:
                # Save the image as a gray image, takes less space
                cv2.imwrite( new_tif_fp, img[:,:,0] )
                del img
                os.remove( old_tif_fp )
            except Exception as e:
                print(old_fn)
                print(str(e))
        
        # If image is shaped oddly (i.e. (1,1,1,Y,X) ) run this instead
        elif len(img.shape)==5:
            try:
                # If Image shape is (1,1,1,Y,X) (UNKNOWN AS TO WHY IT IS THIS SHAPE)
                if img.shape[0]==img.shape[1] and img.shape[0]==img.shape[2] and img.shape[0]==1:
                    img = img[0,0,0,:,:]
                    cv2.imwrite( new_tif_fp, img )
                    del img
                    os.remove( old_tif_fp )
                    return
            except Exception as e:
                print(str(e))
                
    #clean_up_tiff_directory( tiff_target_folder )
    
def clean_up_tiff_directory( tiff_target_folder ):
    # Create path if it doesn't exist
    if not os.path.exists(tiff_target_folder):
        os.makedirs(tiff_target_folder)
    
    for tiff_fn in os.listdir(tiff_target_folder):
        # Do nothing if expected patterns don't show up in the file
        if (not '.czi' in tiff_fn and not '.ndpi' in tiff_fn) or not '.tif' in tiff_fn:
            continue
            
        old_fn = os.path.join(tiff_target_folder, tiff_fn)
        # Remove unwanted symbols and whatnot
        new_fn = old_fn.replace('.czi #','_S')
        # Read the image we just extracted
        img = cv2.imread( old_fn )
        try:
            # Save the image in its proper format
            cv2.imwrite(new_fn, img[:,:,0] )
            del img
            os.remove( old_fn )
        except Exception as e:
            print(old_fn)
            print(e)