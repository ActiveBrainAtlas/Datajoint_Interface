#!/usr/bin/env python

import os
import sys
import subprocess
import time
import json

sys.path.append(os.path.join(os.environ['REPO_DIR'], 'utilities'))
#from utilities2015 import *
from data_manager_v2 import *
#from distributed_utilities import *
from metadata import *


def save_dict_as_ini( input_dict, fp ):
    import configparser
    assert 'DEFAULT' in input_dict.keys()

    config = configparser.ConfigParser()

    for key in input_dict.keys():
        config[key] = input_dict[key]
        
    with open(fp, 'w') as configfile:
        config.write(configfile)

def get_current_step_from_progress_ini( stack ):
    #try:
    if True:
        progress_dict = DataManager.get_brain_info_progress( stack )

        for pipeline_step in ordered_pipeline_steps:
            completed = progress_dict[ pipeline_step ] in ['True','true']
            if not completed:
                return pipeline_step
        return None
    #except Exception as e:
    #    sys.stderr.write( 'Something went wrong loading the progress ini.\n' )
    #    sys.stderr.write( str(e) )
    #    print( str(e) )
    #    return 'setup_metadata'
    
def set_step_completed_in_progress_ini( stack, step ):
    progress_dict = DataManager.get_brain_info_progress( stack )
    progress_dict[step] = True
    
    # Save PROGRESS ini
    progress_ini_to_save = {}
    progress_ini_to_save['DEFAULT'] = progress_dict
    
    # Get filepath and save ini
    fp = DataManager.get_brain_info_progress_fp( stack )
    save_dict_as_ini( progress_ini_to_save, fp )
    
def revert_to_prev_step( stack, target_step ):
    progress_dict = {}
    
    passed_target_step = False
    for step in ordered_pipeline_steps:
        # Set all steps before "target_step" as completed, all after as incomplete
        if passed_target_step:
            progress_dict[step] = False
        else:
            if step==target_step:
                progress_dict[step] = False
                passed_target_step = True
            else:
                progress_dict[step] = True
    
    # Save PROGRESS ini
    progress_ini_to_save = {}
    progress_ini_to_save['DEFAULT'] = progress_dict
    
    # Get filepath and save ini
    fp = DataManager.get_brain_info_progress_fp( stack )
    save_dict_as_ini( progress_ini_to_save, fp )

def create_input_spec_ini( name, image_name_list, stack, prep_id, version, resol  ):
    f = open(name, "w")
    
    f.write('[DEFAULT]\n')
    f.write('image_name_list = '+image_name_list[0]+'\n')
    for i in range ( 1 , len(image_name_list) ):
        f.write('    '+image_name_list[i]+'\n')
    f.write('stack = '+stack+'\n')
    f.write('prep_id = '+prep_id+'\n')
    f.write('version = '+version+'\n')
    f.write('resol = '+resol+'\n')
    
def create_input_spec_ini_all( name, stack, prep_id, version, resol  ):
    f = open(name, "w")
    
    f.write('[DEFAULT]\n')
    f.write('image_name_list = all\n')
    f.write('stack = '+stack+'\n')
    f.write('prep_id = '+prep_id+'\n')
    f.write('version = '+version+'\n')
    f.write('resol = '+resol+'\n')
    
def get_fn_list_from_sorted_filenames( stack ):
    '''
        get_fn_list_from_sorted_filenames( stack ) returns a list of all the valid
        filenames for the current stack.
    '''
    #fp = DataManager.get_images_root_folder(stack)
    #fn = stack+'_sorted_filenames.txt'
    sfns_fp = DataManager.get_sorted_filenames_filename(stack)
    
    try:
        file0 = open( sfns_fp, 'r')
    except:
        print('_________________________________________________________________________________')
        print('_________________________________________________________________________________')
        print('\"'+sfns_fp+'\" not found!')
        print('')
        print('This file must be present for the pipeline to continue. Add the file and rerun the script.')
        print('_________________________________________________________________________________')
        print('_________________________________________________________________________________')
        sys.exit()
        
    section_names = []

    for line in file0: 
        if 'Placeholder' in line:
            #print line
            continue
        else:
            space_index = line.index(" ")
            section_name = line[ 0 : space_index ]
            section_number = line[ space_index+1 : ]
            section_names.append( section_name )
    return section_names

def make_from_x_to_y_ini(stack,x,y,rostral_limit,caudal_limit,dorsal_limit,ventral_limit):
    '''
    Creates operation configuration files that specify the cropping boxes for either the whole brain, or the brainstem.
    '''
    base_prep_id=''
    dest_prep_id=''
    if x=='aligned':
        base_prep_id = 'aligned'
    elif x=='padded':
        base_prep_id = 'alignedPadded'
    if y=='wholeslice':
        dest_prep_id = 'alignedWithMargin'
    elif y=='brainstem':
        dest_prep_id = 'alignedBrainstemCrop'
    
    fn = os.path.join( DataManager.get_images_root_folder(stack), 'operation_configs', 'from_'+x+'_to_'+y+'.ini' )
    f = open(fn, "w")
    f.write('[DEFAULT]\n')
    f.write('type = crop\n\n')
    f.write('base_prep_id = '+base_prep_id+'\n')
    f.write('dest_prep_id = '+dest_prep_id+'\n\n')
    f.write('rostral_limit = '+str(rostral_limit)+'\n')
    f.write('caudal_limit = '+str(caudal_limit)+'\n')
    f.write('dorsal_limit = '+str(dorsal_limit)+'\n')
    f.write('ventral_limit = '+str(ventral_limit)+'\n')
    f.write('resolution = thumbnail')
    f.close()
    
def make_manual_anchor_points( stack, x_12N, y_12N, x_3N, y_3N, z_midline):
    if not os.path.exists( DataManager.get_simple_global_root_folder(stack) ):
        os.mkdir( DataManager.get_simple_global_root_folder(stack) )
    
    fn = os.path.join( DataManager.get_simple_global_root_folder(stack), stack+'_manual_anchor_points.ini' )
    
    f = open(fn, "w")
    f.write('[DEFAULT]\n')
    f.write('x_12N = '+str(x_12N)+'\n')
    f.write('y_12N = '+str(y_12N)+'\n')
    f.write('x_3N = '+str(x_3N)+'\n')
    f.write('y_3N = '+str(y_3N)+'\n')
    f.write('z_midline = '+str(z_midline))
    f.close()
    
def make_rotation_ini(stack, base_prep_id, dest_prep_id, rotation_type):
    '''
    Creates operation configuration files that specify the kind of rotation / flipping to apply to images (Clockwise rotations).
    
    http://www.imagemagick.org/Usage/warping/#flip
    '''
    assert rotation_type in orientation_argparse_str_to_imagemagick_str.keys()
    
    # Defined in metadata
    base_prep_id = prep_id_short_str_to_full[ base_prep_id ]
    dest_prep_id = prep_id_short_str_to_full[ dest_prep_id ]
    
    fn = os.path.join( DataManager.get_images_root_folder(stack), 'operation_configs', 'rotate_transverse.ini' )
    f = open(fn, "w")
    f.write('[DEFAULT]\n')
    f.write('type = rotate\n')
    f.write('how = '+rotation_type+'\n\n')
    f.write('base_prep_id = '+base_prep_id+'\n')
    f.write('dest_prep_id = '+dest_prep_id+'\n\n')
    f.close()
    
def make_structure_fixed_and_moving_brain_specs( stack, id_detector, structure):
    '''
    Creates the input specification file for the registration script.
    '''
    if type(structure)==list:
        fixed_brain_spec_data = {"name":stack,
                            "vol_type": "score", 
                            "resolution":"10.0um",
                            "detector_id":id_detector,
                            "structure":structure
                            }
        moving_brain_spec_data = {"name":"atlasV7",
                            "vol_type": "score", 
                            "resolution":"10.0um",
                            "structure":structure
                            }
    elif type(structure)==str:
        fixed_brain_spec_data = {"name":stack,
                                "vol_type": "score", 
                                "resolution":"10.0um",
                                "detector_id":id_detector,
                                "structure":[structure]
                                }
        moving_brain_spec_data = {"name":"atlasV7",
                                "vol_type": "score", 
                                "resolution":"10.0um",
                                "structure":[structure]
                                }

    fn_fixed = stack+'_fixed_brain_spec.json'
    fn_moving = stack+'_moving_brain_spec.json'
    
    fp = os.path.join( os.environ['REPO_DIR'], '..', 'demo/')

    with open(fp+fn_fixed, 'w') as outfile:
        json.dump(fixed_brain_spec_data, outfile)
    with open(fp+fn_moving, 'w') as outfile:
        json.dump(moving_brain_spec_data, outfile)
        
    return fp+fn_fixed, fp+fn_moving

def make_registration_visualization_input_specs( stack, id_detector, structure):
    '''
    Creates the input specification file for the registration visualization script.
    '''
    fp = os.path.join( os.environ['REPO_DIR'], '..', 'demo/')
    
    fn_global = stack+'_visualization_global_alignment_spec.json'
    data = {}
    data["stack_m"] ={
            "name":"atlasV7",
            "vol_type": "score",
            "resolution":"10.0um"
            }
    data["stack_f"] ={
        "name":stack, 
        "vol_type": "score", 
        "resolution":"10.0um",
        "detector_id":id_detector
        }
    data["warp_setting"] = 0

    with open(fp+fn_global, 'w') as outfile:
        json.dump(data, outfile)
        
    fn_structures = stack+'_visualization_per_structure_alignment_spec.json'
    data = {}        
    data[structure] ={
        "stack_m": 
            {
            "name":"atlasV7", 
            "vol_type": "score", 
            "structure": [structure],
            "resolution":"10.0um"
            },
        "stack_f":
            {
                    "name":stack,
                    "vol_type": "score",
                    "structure":[structure],
                    "resolution":"10.0um",
                    "detector_id":id_detector
                    },
        "warp_setting": 7
        }
    with open(fp+fn_structures, 'w') as outfile:
        json.dump(data, outfile)
        
    return fn_structures, fn_global

def create_prep2_section_limits( stack, lower_lim, upper_lim):
    fn = os.path.join( DataManager.get_images_root_folder(stack), stack+'_prep2_sectionLimits.ini' )
    f = open(fn, "w")
    f.write('[DEFAULT]\n')
    f.write('left_section_limit = '+str(lower_lim)+'\n')
    f.write('right_section_limit = '+str(upper_lim)+'\n')
    f.close()
    
def get_prep5_limits_from_prep1_thumbnail_masks( stack, max_distance_to_scan_from_midpoint=25,
                                               plot_progression=False):
    prep_id = 1
    version = 'mask'
    resol = 'thumbnail'

    sec_to_fn_dict = DataManager.load_sorted_filenames(stack=stack)[1]

    midpoint = int( np.mean( DataManager.load_sorted_filenames(stack=stack)[1].keys() ) )
    max_distance = max_distance_to_scan_from_midpoint

    # Only keeps sections within a max_distance of the midpoint
    for i in sec_to_fn_dict.keys():
        try:
            if i not in range( midpoint-max_distance, midpoint+max_distance):
                del sec_to_fn_dict[i]
            if sec_to_fn_dict[i] == 'Placeholder':
                del sec_to_fn_dict[i]
        except KeyError:
            pass
        
    
    # Get dimensions of the first image in the list (will be the same for all)
    img_fp = DataManager.get_image_filepath_v2(stack=stack, prep_id=prep_id, 
                                            resol=resol, version=version, 
                                            fn=sec_to_fn_dict[sec_to_fn_dict.keys()[0]])
    height, width, channels = cv2.imread( img_fp ).shape
    height_d16 = height/16
    width_d16 = width/16

    curr_rostral_lim_d16 = width_d16
    curr_caudal_lim_d16 = 0
    curr_dorsal_lim_d16 = height_d16
    curr_ventral_lim_d16 = 0
    
    
    for img_name in sec_to_fn_dict.values():
        # Get the image filepath and then load the image, downsampling
        # an additional 16x for speed
        img_fp = DataManager.get_image_filepath_v2(stack=stack, 
                                                   prep_id=prep_id, 
                                                   resol=resol,
                                                   version=version, 
                                                   fn=img_name)
        img_thumbnail_mask_down16 = cv2.imread( img_fp )[::16,::16]

        # update rostral lim
        for col_i in range( curr_rostral_lim_d16 ):
            col = img_thumbnail_mask_down16[ :, col_i]

            contains_tissue = np.array( col ).any()

            if contains_tissue:
                curr_rostral_lim_d16 = min( curr_rostral_lim_d16, col_i )
                break

        # update caudal lim
        caudal_range = range( curr_caudal_lim_d16, width_d16) 
        caudal_range.reverse() # Goes from right of image to left
        for col_i in caudal_range:
            col = img_thumbnail_mask_down16[ :, col_i]

            contains_tissue = np.array( col ).any()

            if contains_tissue:
                curr_caudal_lim_d16 = max( curr_caudal_lim_d16, col_i )
                break

        # update dorsal lim
        for row_i in range( curr_dorsal_lim_d16 ):
            row = img_thumbnail_mask_down16[ row_i, :]

            contains_tissue = np.array( row ).any()

            if contains_tissue:
                curr_dorsal_lim_d16 = min( curr_dorsal_lim_d16, row_i )
                break

        # update ventral lim
        ventral_range = range( curr_ventral_lim_d16, height_d16) 
        ventral_range.reverse() # Goes from right of image to left
        for row_i in ventral_range:
            row = img_thumbnail_mask_down16[ row_i, :]

            contains_tissue = np.array( row ).any()

            if contains_tissue:
                curr_ventral_lim_d16 = max( curr_ventral_lim_d16, row_i )
                break
                
        if plot_progression:
            plt.imshow( img_thumbnail_mask_down16 )
            plt.scatter( [curr_rostral_lim_d16, curr_rostral_lim_d16, curr_caudal_lim_d16, curr_caudal_lim_d16],
               [curr_dorsal_lim_d16, curr_ventral_lim_d16, curr_dorsal_lim_d16, curr_ventral_lim_d16],
               c='r')
            plt.show()

    # Make the boundary slightly larger
    final_rostral_lim = (curr_rostral_lim_d16-1.5)*16
    final_caudal_lim = (curr_caudal_lim_d16+1.5)*16
    final_dorsal_lim = (curr_dorsal_lim_d16-1.5)*16
    final_ventral_lim = (curr_ventral_lim_d16+1.5)*16
    # If boundary goes past the image, reset to the min/max value
    final_rostral_lim = max( final_rostral_lim, 0 )
    final_caudal_lim = min( final_caudal_lim, width )
    final_dorsal_lim = max( final_dorsal_lim, 0 )
    final_ventral_lim = min( final_ventral_lim, height )
 
    print('rostral:',final_rostral_lim)
    print('caudal:',final_caudal_lim)
    print('dorsal:',final_dorsal_lim)
    print('ventral:',final_ventral_lim)
    
    return final_rostral_lim, final_caudal_lim, final_dorsal_lim, final_ventral_lim

def close_main_gui_old( ex, reopen=True ):
    ex.hide()
    # We manually kill this operation by getting a list of p_ids running this process 
    #  (in case there are multiple hanging instances)
    ps = subprocess.Popen(('ps','aux'), stdout=subprocess.PIPE)
    output = subprocess.check_output(('grep', 'python a_GUI_main.py'), stdin=ps.stdout)
    python_GUI_initial_processes = output.split('\n')
    
    for process_str in python_GUI_initial_processes:
        # We are currently running a grep command that we should not kill
        if 'grep' in process_str or process_str == '':
            continue
        # Get the p-id of every a_GUI_initial.py process and kill it in cold blood
        else:
            p_id = process_str.split()[1]
            subprocess.call(['kill','-9',p_id])
            
    print('\n\n***********************')
    print('\n\nGUI closed down successfully!\n\n')
    print('***********************\n\n')
    
    #sys.exit( app.exec_() )
    #sys.exit()
    
    if reopen:
        subprocess.call(['python', os.path.join(os.environ['REPO_DIR'], '..', 'demo', 'a_GUI_main.py')])
    
def close_main_gui( app, reopen=True ):
    sys.exit( app.exec_() )
    
def call_and_time( command_list, completion_message='' ):
    start_t = time.time()
    subprocess.call( command_list )
    end_t = time.time()
    
    if command_list[0]=='python':
        print('**************************************************************************************************')
        print '\nScript '+command_list[1]+' completed. Took ',round(end_t - start_t,1),' seconds'
        print completion_message +'\n'
        print('**************************************************************************************************')