"""
This module stores static meta information.
"""
import os, sys
import numpy as np
import subprocess

import json

########### Data Directories #############

hostname = str(subprocess.check_output("hostname", shell=True).strip())
username = str(subprocess.check_output("whoami", shell=True).strip())

if 'ENABLE_UPLOAD_S3' in os.environ:
    ENABLE_UPLOAD_S3 = bool(int(os.environ['ENABLE_UPLOAD_S3']))
    #sys.stderr.write("ENABLE_UPLOAD_S3 set to %s\n" % ENABLE_UPLOAD_S3)
else:
    ENABLE_UPLOAD_S3 = False
    #sys.stderr.write("ENABLE_UPLOAD_S3 is not set, default to False.\n")

if 'ENABLE_DOWNLOAD_S3' in os.environ:
    ENABLE_DOWNLOAD_S3 = bool(int(os.environ['ENABLE_DOWNLOAD_S3']))
    #sys.stderr.write("ENABLE_DOWNLOAD_S3 set to %s\n" % ENABLE_DOWNLOAD_S3)
else:
    ENABLE_DOWNLOAD_S3 = False
    #sys.stderr.write("ENABLE_DOWNLOAD_S3 is not set, default to False.\n")

ON_DOCKER = False
if hostname == 'atlasDocker':
    print('Setting environment for the Docker Container')
    ON_DOCKER = True
    
    try:
        #ROOT_DIR = os.environ['ROOT_DIR']
        #DATA_ROOTDIR = os.environ['ROOT_DIR']
        #THUMBNAIL_DATA_ROOTDIR = os.environ['ROOT_DIR']
        ROOT_DIR = '/net/birdstore/Active_Atlas_Data/data_root/pipeline_data'
        DATA_ROOTDIR = ROOT_DIR
        THUMBNAIL_DATA_ROOTDIR = ROOT_DIR
    except KeyError:
        print("Please ensure you are inside the virtual environment.")
        print("Run `source ./app`")
        sys.exit(0)
        

    ON_AWS = False
    S3_DATA_BUCKET = 'mousebrainatlas-data'
    S3_RAWDATA_BUCKET = 'mousebrainatlas-rawdata'
    
    RAW_DATA_DIR = os.path.join(DATA_ROOTDIR, 'CSHL_data')
    DATA_DIR = os.path.join(DATA_ROOTDIR, 'CSHL_data_processed')
    THUMBNAIL_DATA_DIR = os.path.join(THUMBNAIL_DATA_ROOTDIR, 'CSHL_data_processed')
    VOLUME_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_volumes')
    MESH_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_meshes')

    # annotation_rootdir =  os.path.join(ROOT_DIR, 'CSHL_data_labelings_losslessAlignCropped')
#     annotation_midbrainIncluded_v2_rootdir = '/home/yuncong/CSHL_labelings_v3/'
    PATCH_FEATURES_ROOTDIR = os.path.join(DATA_ROOTDIR, 'CSHL_patch_features')
    PATCH_LOCATIONS_ROOTDIR = os.path.join(DATA_ROOTDIR, 'CSHL_patch_locations')

    SCOREMAP_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_scoremaps')
    SCOREMAP_VIZ_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_scoremap_viz')
    SPARSE_SCORES_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_patch_scores')

    ANNOTATION_ROOTDIR =  os.path.join(ROOT_DIR, 'CSHL_labelings_v3')
    ANNOTATION_THALAMUS_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_labelings_thalamus')
    CLF_ROOTDIR =  os.path.join(DATA_ROOTDIR, 'classifiers')

    REGISTRATION_PARAMETERS_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_registration_parameters')
    REGISTRATION_VIZ_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_registration_visualization')

    KDU_EXPAND_BIN = '/app/KDU7A2_Demo_Apps_for_Ubuntu-x86-64_170827/kdu_expand'

    CLASSIFIER_SETTINGS_CSV = os.path.join(REPO_DIR, 'learning', 'classifier_settings.csv')
    DATASET_SETTINGS_CSV = os.path.join(REPO_DIR, 'learning', 'dataset_settings.csv')
    REGISTRATION_SETTINGS_CSV = os.path.join(REPO_DIR, 'registration', 'registration_settings.csv')
    PREPROCESS_SETTINGS_CSV = os.path.join(REPO_DIR, 'preprocess', 'preprocess_settings.csv')
    DETECTOR_SETTINGS_CSV = os.path.join(REPO_DIR, 'learning', 'detector_settings.csv')

    MXNET_MODEL_ROOTDIR = os.path.join(ROOT_DIR, 'mxnet_models')

    ELASTIX_BIN = 'elastix'

elif hostname == 'ratto.dk.ucsd.edu' and username == 'adnewber':
    print('Setting environment for Precision WorkStation for Alex Newberry')
    HOST_ID = 'workstation'

    if 'ROOT_DIR' in os.environ:
        ROOT_DIR = os.environ['ROOT_DIR']
    else:
        ROOT_DIR = '/home/alexn/'

    if 'DATA_ROOTDIR' in os.environ:
        DATA_ROOTDIR = os.environ['DATA_ROOTDIR']
    else:
        DATA_ROOTDIR = '/home/alexn/data'

    if 'THUMBNAIL_DATA_ROOTDIR' in os.environ:
        THUMBNAIL_DATA_ROOTDIR = os.environ['THUMBNAIL_DATA_ROOTDIR']
    else:
        THUMBNAIL_DATA_ROOTDIR = '/home/alexn/data'

    RAW_DATA_DIR = os.path.join(DATA_ROOTDIR, 'CSHL_data')

    ON_AWS = False
    S3_DATA_BUCKET = 'mousebrainatlas-data'
    S3_RAWDATA_BUCKET = 'mousebrainatlas-rawdata'

    REPO_DIR = os.environ['REPO_DIR']

    DATA_DIR = os.path.join(DATA_ROOTDIR, 'CSHL_data_processed')

    THUMBNAIL_DATA_DIR = os.path.join(THUMBNAIL_DATA_ROOTDIR, 'CSHL_data_processed')
    VOLUME_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_volumes')
    # MESH_ROOTDIR =  '/home/alexn/CSHL_meshes'
    MESH_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_meshes')

    # annotation_rootdir =  os.path.join(ROOT_DIR, 'CSHL_data_labelings_losslessAlignCropped')
#     annotation_midbrainIncluded_v2_rootdir = '/home/yuncong/CSHL_labelings_v3/'
    PATCH_FEATURES_ROOTDIR = os.path.join(DATA_ROOTDIR, 'CSHL_patch_features')
    PATCH_LOCATIONS_ROOTDIR = os.path.join(DATA_ROOTDIR, 'CSHL_patch_locations')

    SCOREMAP_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_scoremaps')
    SCOREMAP_VIZ_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_scoremap_viz')
    SPARSE_SCORES_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_patch_scores')

    ANNOTATION_ROOTDIR =  os.path.join(ROOT_DIR, 'CSHL_labelings_v3')
    ANNOTATION_THALAMUS_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_labelings_thalamus')
    CLF_ROOTDIR =  os.path.join(DATA_ROOTDIR, 'CSHL_classifiers')

    REGISTRATION_PARAMETERS_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_registration_parameters')
    REGISTRATION_VIZ_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_registration_visualization')

    KDU_EXPAND_BIN = '/home/yuncong/KDU7A2_Demo_Apps_for_Centos7-x86-64_170827/kdu_expand'

    CLASSIFIER_SETTINGS_CSV = os.path.join(REPO_DIR, 'learning', 'classifier_settings.csv')
    DATASET_SETTINGS_CSV = os.path.join(REPO_DIR, 'learning', 'dataset_settings.csv')
    REGISTRATION_SETTINGS_CSV = os.path.join(REPO_DIR, 'registration', 'registration_settings.csv')
    PREPROCESS_SETTINGS_CSV = os.path.join(REPO_DIR, 'preprocess', 'preprocess_settings.csv')
    DETECTOR_SETTINGS_CSV = os.path.join(REPO_DIR, 'learning', 'detector_settings.csv')

    MXNET_MODEL_ROOTDIR = os.path.join(ROOT_DIR, 'mxnet_models')

    ELASTIX_BIN = 'elastix'


elif hostname.startswith('ip'):
    print('Setting environment for AWS compute node')
    HOST_ID = 'ec2'

    if 'ROOT_DIR' in os.environ:
        ROOT_DIR = os.environ['ROOT_DIR']
    else:
        ROOT_DIR = '/shared'

    if 'DATA_ROOTDIR' in os.environ:
        DATA_ROOTDIR = os.environ['DATA_ROOTDIR']
    else:
        DATA_ROOTDIR = '/shared'

    if 'THUMBNAIL_DATA_ROOTDIR' in os.environ:
        THUMBNAIL_DATA_ROOTDIR = os.environ['THUMBNAIL_DATA_ROOTDIR']
    else:
        THUMBNAIL_DATA_ROOTDIR = '/shared'

    ON_AWS = True
    S3_DATA_BUCKET = 'mousebrainatlas-data'
    S3_RAWDATA_BUCKET = 'mousebrainatlas-rawdata'
    S3_DATA_DIR = 'CSHL_data_processed'
    REPO_DIR = os.environ['REPO_DIR']
    RAW_DATA_DIR = os.path.join(ROOT_DIR, 'CSHL_data')
    DATA_DIR = os.path.join(DATA_ROOTDIR, 'CSHL_data_processed')
    THUMBNAIL_DATA_DIR = os.path.join(THUMBNAIL_DATA_ROOTDIR, 'CSHL_data_processed')
    VOLUME_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_volumes')

    MESH_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_meshes')

    # SCOREMAP_VIZ_ROOTDIR = '/shared/CSHL_scoremap_viz_Sat16ClassFinetuned_v2'
    ANNOTATION_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_labelings_v3')
    ANNOTATION_THALAMUS_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_labelings_thalamus')
    ANNOTATION_VIZ_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_annotation_viz')
    # SVM_ROOTDIR = '/shared/CSHL_patch_features_Sat16ClassFinetuned_v2_classifiers/'
    # SVM_NTBLUE_ROOTDIR = '/shared/CSHL_patch_features_Sat16ClassFinetuned_v2_classifiers_neurotraceBlue/'
    PATCH_FEATURES_ROOTDIR = os.path.join(DATA_ROOTDIR, 'CSHL_patch_features')
    PATCH_LOCATIONS_ROOTDIR = os.path.join(DATA_ROOTDIR, 'CSHL_patch_locations')
    SCOREMAP_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_scoremaps')
    SCOREMAP_VIZ_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_scoremap_viz')
    SPARSE_SCORES_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_patch_scores')
    REGISTRATION_PARAMETERS_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_registration_parameters')
    REGISTRATION_VIZ_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_registration_visualization')
    # SPARSE_SCORES_ROOTDIR = '/shared/CSHL_patch_Sat16ClassFinetuned_v2_predictions'
    # SCOREMAPS_ROOTDIR = '/shared/CSHL_lossless_scoremaps_Sat16ClassFinetuned_v2'
    # HESSIAN_ROOTDIR = '/shared/CSHL_hessians/'
    ELASTIX_BIN = 'elastix'
    KDU_EXPAND_BIN = '/home/ubuntu/KDU79_Demo_Apps_for_Linux-x86-64_170108/kdu_expand'
    CELLPROFILER_EXEC = 'python /shared/CellProfiler/CellProfiler.py' # /usr/local/bin/cellprofiler
    CELLPROFILER_PIPELINE_FP = '/shared/CSHL_cells_v2/SegmentCells.cppipe'

    if 'CELLS_ROOTDIR' in os.environ:
        CELLS_ROOTDIR = os.environ['CELLS_ROOTDIR']
    else:
        CELLS_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_cells_v2')

    DETECTED_CELLS_ROOTDIR = os.path.join(CELLS_ROOTDIR, 'detected_cells')
    CELL_EMBEDDING_ROOTDIR = os.path.join(CELLS_ROOTDIR, 'embedding')
    D3JS_ROOTDIR = os.path.join(CELLS_ROOTDIR, 'd3js')
    CELL_FEATURES_CLF_ROOTDIR = os.path.join(CELLS_ROOTDIR, 'classifiers')

    CLF_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_classifiers')

    CLASSIFIER_SETTINGS_CSV = os.path.join(REPO_DIR, 'learning', 'classifier_settings.csv')
    DATASET_SETTINGS_CSV = os.path.join(REPO_DIR, 'learning', 'dataset_settings.csv')
    REGISTRATION_SETTINGS_CSV = os.path.join(REPO_DIR, 'registration', 'registration_settings.csv')
    PREPROCESS_SETTINGS_CSV = os.path.join(REPO_DIR, 'preprocess', 'preprocess_settings.csv')
    DETECTOR_SETTINGS_CSV = os.path.join(REPO_DIR, 'learning', 'detector_settings.csv')

    MXNET_MODEL_ROOTDIR = os.path.join(ROOT_DIR, 'mxnet_models')

    LABELED_NEURONS_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_labeled_neurons')

    CSHL_SPM_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_SPM')

else:

    print('Setting environment for an unknown machine. Global root paths must be set as env variables.')

    assert 'ROOT_DIR' in os.environ, "Must set ROOT_DIR env variable"
    ROOT_DIR = os.environ['ROOT_DIR']

    assert 'DATA_ROOTDIR' in os.environ, "Must set DATA_ROOTDIR env variable"
    DATA_ROOTDIR = os.environ['DATA_ROOTDIR']

    assert 'THUMBNAIL_DATA_ROOTDIR' in os.environ, "Must set THUMBNAIL_DATA_ROOTDIR env variable"
    THUMBNAIL_DATA_ROOTDIR = os.environ['THUMBNAIL_DATA_ROOTDIR']

    # ON_AWS = False
    S3_DATA_BUCKET = 'mousebrainatlas-data'
    S3_RAWDATA_BUCKET = 'mousebrainatlas-rawdata'
    S3_DATA_DIR = 'CSHL_data_processed'
    REPO_DIR = os.environ['REPO_DIR']
    RAW_DATA_DIR = os.path.join(ROOT_DIR, 'CSHL_data')
    DATA_DIR = os.path.join(DATA_ROOTDIR, 'CSHL_data_processed')
    THUMBNAIL_DATA_DIR = os.path.join(THUMBNAIL_DATA_ROOTDIR, 'CSHL_data_processed')
    VOLUME_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_volumes')

    MESH_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_meshes')

    ANNOTATION_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_labelings_v3')
    ANNOTATION_THALAMUS_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_labelings_thalamus')
    ANNOTATION_VIZ_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_annotation_viz')
    PATCH_FEATURES_ROOTDIR = os.path.join(DATA_ROOTDIR, 'CSHL_patch_features')
    PATCH_LOCATIONS_ROOTDIR = os.path.join(DATA_ROOTDIR, 'CSHL_patch_locations')
    SCOREMAP_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_scoremaps')
    SCOREMAP_VIZ_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_scoremap_viz')
    SPARSE_SCORES_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_patch_scores')
    REGISTRATION_PARAMETERS_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_registration_parameters')
    REGISTRATION_VIZ_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_registration_visualization')
    ELASTIX_BIN = 'elastix'
    #KDU_EXPAND_BIN = '/home/ubuntu/KDU79_Demo_Apps_for_Linux-x86-64_170108/kdu_expand'

    if 'CELLS_ROOTDIR' in os.environ:
        CELLS_ROOTDIR = os.environ['CELLS_ROOTDIR']
    else:
        CELLS_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_cells_v2')

    DETECTED_CELLS_ROOTDIR = os.path.join(CELLS_ROOTDIR, 'detected_cells')
    CELL_EMBEDDING_ROOTDIR = os.path.join(CELLS_ROOTDIR, 'embedding')
    D3JS_ROOTDIR = os.path.join(CELLS_ROOTDIR, 'd3js')
    CELL_FEATURES_CLF_ROOTDIR = os.path.join(CELLS_ROOTDIR, 'classifiers')

    CLF_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_classifiers')

    CLASSIFIER_SETTINGS_CSV = os.path.join(REPO_DIR, 'learning', 'classifier_settings.csv')
    DATASET_SETTINGS_CSV = os.path.join(REPO_DIR, 'learning', 'dataset_settings.csv')
    REGISTRATION_SETTINGS_CSV = os.path.join(REPO_DIR, 'registration', 'registration_settings.csv')
    PREPROCESS_SETTINGS_CSV = os.path.join(REPO_DIR, 'preprocess', 'preprocess_settings.csv')
    DETECTOR_SETTINGS_CSV = os.path.join(REPO_DIR, 'learning', 'detector_settings.csv')

    MXNET_MODEL_ROOTDIR = os.path.join(ROOT_DIR, 'mxnet_models')

    LABELED_NEURONS_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_labeled_neurons')

    CSHL_SPM_ROOTDIR = os.path.join(ROOT_DIR, 'CSHL_SPM')



#################### Resolution conversions ############

def convert_resolution_string_to_um(resolution, stack=None):
    return convert_resolution_string_to_voxel_size(resolution, stack=stack)

def convert_resolution_string_to_voxel_size(resolution, stack=None):
    """
    Args:
        resolution (str):
    Returns:
        voxel/pixel size in microns.
    """

    assert resolution is not None, 'Resolution argument cannot be None.'

    if resolution in ['down32', 'thumbnail']:
        assert stack is not None
        return planar_resolution[stack] * 32.
    elif resolution == 'lossless' or resolution == 'down1' or resolution == 'raw':
        assert stack is not None
        return planar_resolution[stack]
    elif resolution.startswith('down'):
        assert stack is not None
        return planar_resolution[stack] * int(resolution[4:])
    elif resolution == 'um':
        return 1.
    elif resolution.endswith('um'):
        return float(resolution[:-2])
    else:
        print(resolution)
        raise Exception("Unknown resolution string %s" % resolution)

#################### Name conversions ##################

def parse_label(label, singular_as_s=False):
    """
    Args:
        singular_as_s (bool): If true, singular structures have side = 'S', otherwise side = None.

    Returns:
        (structure name, side, surround margin, surround structure name)
    """
    import re
    try:
        m = re.match("([0-9a-zA-Z]*)(_(L|R))?(_surround_(.+)_([0-9a-zA-Z]*))?", label)
    except:
        raise Exception("Parse label error: %s" % label)
    g = m.groups()
    structure_name = g[0]
    side = g[2]
    if side is None:
        if singular_as_s:
            side = 'S'
    surround_margin = g[4]
    surround_structure_name = g[5]

    return structure_name, side, surround_margin, surround_structure_name

is_sided_label = lambda label: parse_label(label)[1] is not None
# is_surround_label = lambda label: parse_label(label)[2] is not None
is_surround_label = lambda label: 'surround' in label
get_side_from_label = lambda label: parse_label(label)[1]
get_margin_from_label = lambda label: parse_label(label)[2]

def compose_label(structure_name, side=None, surround_margin=None, surround_structure_name=None, singular_as_s=False):
    label = structure_name
    if side is not None:
        if not singular_as_s and side == 'S':
            pass
        else:
            label += '_' + side
    if surround_margin is not None:
        label += '_surround_' + surround_margin
    if surround_structure_name is not None:
        label += '_' + surround_structure_name
    return label

def convert_to_unsided_label(label):
    structure_name, side, surround_margin, surround_structure_name = parse_label(label)
    return compose_label(structure_name, side=None, surround_margin=surround_margin, surround_structure_name=surround_structure_name)

def convert_to_nonsurround_label(name):
    return convert_to_nonsurround_name(name)

    # return convert_name_to_unsided(name)

# def convert_name_to_unsided(name):
#     if '_' not in name:
#         return name
#     else:
#         return convert_to_original_name(name)

def convert_to_left_name(name):
    if name in singular_structures:
        # sys.stderr.write("Asked for left name for singular structure %s, returning itself.\n" % name)
        return name
    else:
        return convert_to_unsided_label(name) + '_L'

def convert_to_right_name(name):
    if name in singular_structures:
        # sys.stderr.write("Asked for right name for singular structure %s, returning itself.\n" % name)
        return name
    else:
        return convert_to_unsided_label(name) + '_R'

def convert_to_original_name(name):
    return name.split('_')[0]

def convert_to_nonsurround_name(name):
    if is_surround_label(name):
        import re
        m = re.match('(.*?)_surround_.*', name)
        return m.groups()[0]
    else:
        return name

def convert_to_surround_name(name, margin=None, suffix=None):
    """
    Args:
        margin (str):
    """

    elements = name.split('_')
    if margin is None:
        if len(elements) > 1 and elements[1] == 'surround':
            if suffix is not None:
                return elements[0] + '_surround_' + suffix
            else:
                return elements[0] + '_surround'
        else:
            if suffix is not None:
                return name + '_surround_' + suffix
            else:
                return name + '_surround'
    else:
        if len(elements) > 1 and elements[1] == 'surround':
            if suffix is not None:
                return elements[0] + '_surround_' + str(margin) + '_' + suffix
            else:
                return elements[0] + '_surround_' + str(margin)
        else:
            if suffix is not None:
                return name + '_surround_' + str(margin) + '_' + suffix
            else:
                return name + '_surround_' + str(margin)


#######################################

from pandas import read_csv
dataset_settings = read_csv(DATASET_SETTINGS_CSV, header=0, index_col=0)
classifier_settings = read_csv(CLASSIFIER_SETTINGS_CSV, header=0, index_col=0)
registration_settings = read_csv(REGISTRATION_SETTINGS_CSV, header=0, index_col=0)
preprocess_settings = read_csv(PREPROCESS_SETTINGS_CSV, header=0, index_col=0)
detector_settings = read_csv(DETECTOR_SETTINGS_CSV, header=0, index_col=0)
windowing_settings = {1: {"patch_size": 224, "spacing": 56},
                      2: {'patch_size':224, 'spacing':56, 'comment':'larger margin'},
                     3: {'patch_size':224, 'spacing':32, 'comment':'smaller spacing'},
                     4: {'patch_size':224, 'spacing':128, 'comment':'smaller spacing'},
                     5: {'patch_size':224, 'spacing':64, 'comment':'smaller spacing'},
                     6: {'patch_size': 448, 'spacing':64, 'comment': 'twice as large patch'},
                     7: {'patch_size_um':103.04, 'spacing_um':30, 'comment':'specify size/spacing in terms of microns rather than pixels'},
                     8: {'patch_size_um':206.08, 'spacing_um':30, 'comment':'larger patch'},
                     9: {'patch_size_um':412.16, 'spacing_um':30, 'comment':'larger patch'},
                    10: {'patch_size_um':824.32, 'spacing_um':30, 'comment':'larger patch'},
                    11: {'patch_size_um':51.52, 'spacing_um':30, 'comment':'larger patch'},
                    12: {'patch_size_um':25.76, 'spacing_um':30, 'comment':'larger patch'},
                     }

############ Class Labels #############

paired_structures = ['5N', '6N', '7N', '7n', 'Amb', 'LC', 'LRt', 'Pn', 'Tz', 'VLL', 'RMC', 'SNC', 'SNR', '3N', '4N',
                    'Sp5I', 'Sp5O', 'Sp5C', 'PBG', '10N', 'VCA', 'VCP', 'DC']
# singular_structures = ['AP', '12N', 'RtTg', 'sp5', 'outerContour', 'SC', 'IC']
singular_structures = ['AP', '12N', 'RtTg', 'SC', 'IC']
singular_structures_with_side_suffix = ['AP_S', '12N_S', 'RtTg_S', 'SC_S', 'IC_S']
all_known_structures = paired_structures + singular_structures
all_known_structures_sided = sum([[n] if n in singular_structures
                        else [convert_to_left_name(n), convert_to_right_name(n)]
                        for n in all_known_structures], [])
all_known_structures_sided_singular_as_s = sum([[n] if n in singular_structures_with_side_suffix
                        else [convert_to_left_name(n), convert_to_right_name(n)]
                        for n in all_known_structures], [])
#all_known_structures_sided_surround_only = [convert_to_surround_name(s, margin='x1.5') for s in all_known_structures_sided]
all_known_structures_sided_surround_200um = [convert_to_surround_name(s, margin='200um') for s in all_known_structures_sided]
all_known_structures_sided_including_surround_200um = sorted(all_known_structures_sided + all_known_structures_sided_surround_200um)
all_known_structures_unsided_including_surround_200um = all_known_structures + [convert_to_surround_name(u, margin='200um') for u in all_known_structures]

all_structures_with_classifiers = sorted([l for l in all_known_structures if l not in {'outerContour', 'sp5'}])

motor_nuclei = ['3N', '4N', '5N','6N', '7N', 'Amb', '12N', '10N']

motor_nuclei_sided_sorted_by_rostral_caudal_position = \
['3N_R', '3N_L', '4N_R', '4N_L', '5N_R', '5N_L', '6N_R', '6N_L', '7N_R', '7N_L', 'Amb_R', 'Amb_L', '12N', '10N_R', '10N_L']

structures_sided_sorted_by_size = ['4N_L', '4N_R', '6N_L', '6N_R', 'Amb_L', 'Amb_R', 'PBG_L', 'PBG_R', '10N_L', '10N_R', 'AP', '3N_L', '3N_R', 'LC_L', 'LC_R', 'SNC_L', 'SNC_R', 'Tz_L', 'Tz_R', '7n_L', '7n_R', 'RMC_L', 'RMC_R', '5N_L', '5N_R', 'VCP_L', 'VCP_R', '12N', 'LRt_L', 'LRt_R', '7N_L', '7N_R', 'VCA_L', 'VCA_R', 'VLL_L', 'VLL_R', 'DC_L', 'DC_R', 'Sp5O_L', 'Sp5O_R', 'Sp5I_L', 'Sp5I_R', 'Pn_L', 'Pn_R', 'RtTg', 'SNR_L', 'SNR_R', 'Sp5C_L', 'Sp5C_R', 'IC', 'SC']
structures_sided_sorted_by_rostral_caudal_position = ['SNC_R', 'SNC_L', 'SC', 'SNR_R', 'SNR_L', 'RMC_R', 'RMC_L', '3N_R', '3N_L', 'PBG_R', 'PBG_L', '4N_R', '4N_L', 'Pn_R', 'Pn_L', 'VLL_R', 'VLL_L', 'RtTg', '5N_R', '5N_L', 'LC_R', 'LC_L', 'Tz_R', 'Tz_L', 'VCA_R', 'VCA_L', '7n_R', '7n_L', '6N_R', '6N_L', 'DC_R', 'DC_L','VCP_R', 'VCP_L', '7N_R', '7N_L', 'Sp5O_R', 'Sp5O_L', 'Amb_R', 'Amb_L', 'Sp5I_R', 'Sp5I_L', 'AP', '12N', '10N_R', '10N_L', 'LRt_R', 'LRt_L', 'Sp5C_R', 'Sp5C_L']
structures_unsided_sorted_by_rostral_caudal_position = ['SNC', 'SC', 'IC', 'SNR', 'RMC', '3N', 'PBG','4N', 'Pn','VLL','RtTg', '5N', 'LC', 'Tz', 'VCA', '7n', '6N', 'DC', 'VCP', '7N', 'Sp5O', 'Amb', 'Sp5I', 'AP', '12N', '10N', 'LRt', 'Sp5C']

#linear_landmark_names_unsided = ['outerContour']
linear_landmark_names_unsided = []
volumetric_landmark_names_unsided = list(set(paired_structures + singular_structures) - set(linear_landmark_names_unsided))
all_landmark_names_unsided = volumetric_landmark_names_unsided + linear_landmark_names_unsided

labels_unsided = volumetric_landmark_names_unsided + linear_landmark_names_unsided
labels_unsided_indices = dict((j, i+1) for i, j in enumerate(labels_unsided))  # BackG always 0

labelMap_unsidedToSided = dict([(name, [name+'_L', name+'_R']) for name in paired_structures] + \
                            [(name, [name]) for name in singular_structures])

labelMap_sidedToUnsided = {n: nu for nu, ns in labelMap_unsidedToSided.iteritems() for n in ns}

from itertools import chain
labels_sided = list(chain(*(labelMap_unsidedToSided[name_u] for name_u in labels_unsided)))
labels_sided_indices = dict((j, i+1) for i, j in enumerate(labels_sided)) # BackG always 0

############ Physical Dimension #############

# section_thickness = 20 # in um
SECTION_THICKNESS = 20. # in um
# xy_pixel_distance_lossless = 0.46
XY_PIXEL_DISTANCE_LOSSLESS = 0.46 # This is the spec for Nanozoomer
XY_PIXEL_DISTANCE_TB = XY_PIXEL_DISTANCE_LOSSLESS * 32 # in um, thumbnail

# This is the spec for Axioscan (our data)
XY_PIXEL_DISTANCE_LOSSLESS_AXIOSCAN = 0.325 # unit is micron
XY_PIXEL_DISTANCE_TB_AXIOSCAN = XY_PIXEL_DISTANCE_LOSSLESS_AXIOSCAN * 32

#######################################

#all_nissl_stacks = ['MD585', 'MD589', 'MD590', 'MD591', 'MD592', 'MD593', 'MD594', 'MD595', 'MD598', 'MD599', 'MD602', 'MD603']
#all_ntb_stacks = ['MD635']
#all_dk_ntb_stacks = ['CHATM2', 'CHATM3', 'UCSD001']
#all_alt_nissl_ntb_stacks = ['MD653', 'MD652', 'MD642']
#all_alt_nissl_tracing_stacks = ['MD657', 'MD658', 'MD661', 'MD662']
# all_stacks = all_nissl_stacks + all_ntb_stacks
#all_stacks = all_nissl_stacks + all_ntb_stacks + all_alt_nissl_ntb_stacks + all_alt_nissl_tracing_stacks + all_dk_ntb_stacks \
#                + ['DEMO999', 'MD998']
#all_annotated_nissl_stacks = ['MD585', 'MD589', 'MD594']
#all_annotated_ntb_stacks = ['MD635']
#all_annotated_stacks = all_annotated_nissl_stacks + all_annotated_ntb_stacks

#all_nissl_stacks = ['MD585', 'MD594', 'MD589']
#all_nissl_stacks = ['MD585']
#all_ntb_stacks = ['UCSD001','DK1-2']
#all_stacks = all_nissl_stacks + all_ntb_stacks


all_stacks = []
all_ntb_stacks = []
all_nissl_stacks = []
if False:
    with open(os.environ['REPO_DIR']+'utilities/registered_brains.json', 'r') as json_file:
        contents = json.load( json_file )

    # Load Nissl and Ntb stacks
    all_nissl_stacks = contents['all_thionin_stacks']
    all_ntb_stacks = contents['all_ntb_stacks']
    #all_stacks = all_nissl_stacks + all_ntb_stacks

    # Load annotated stacks
    all_annotated_ntb_stacks = contents['all_annotated_ntb_stacks']
    all_annotated_nissl_stacks = contents['all_annotated_thionin_stacks']
    all_annotated_stacks = all_annotated_nissl_stacks + all_annotated_ntb_stacks

    all_dk_ntb_stacks = contents['all_dk_ntb_stacks']
    all_alt_nissl_ntb_stacks = contents['all_alt_thionin_ntb_stacks']
    all_alt_nissl_tracing_stacks = contents['all_alt_thionin_tracing_stacks']
    all_stacks = all_nissl_stacks + all_ntb_stacks + all_alt_nissl_ntb_stacks + all_alt_nissl_tracing_stacks + all_dk_ntb_stacks
    #all_stacks = ['MD603','MD635','MD585']


BRAINS_INFO_DIR = os.path.join(DATA_ROOTDIR, 'brains_info')

# from utilities2015 import load_ini

def load_ini(fp, split_newline=True, convert_none_str=True, section='DEFAULT'):
    """
    Value of string None will be converted to Python None.
    """
    import ConfigParser
    config = ConfigParser.ConfigParser()
    if not os.path.exists(fp):
        raise Exception("ini file %s does not exist." % fp)
    config.read(fp)
    input_spec = dict(config.items(section))
    input_spec = {k: v.split('\n') if '\n' in v else v for k, v in input_spec.iteritems()}
    for k, v in input_spec.iteritems():
        if not isinstance(v, list):
            if '.' not in v and v.isdigit():
                input_spec[k] = int(v)
            elif v.replace('.','',1).isdigit():
                input_spec[k] = float(v)
        elif v == 'None':
            if convert_none_str:
                input_spec[k] = None
    assert len(input_spec) > 0, "Failed to read data from ini file."
    return input_spec

planar_resolution = {}
stack_metadata = {}
if os.path.exists( BRAINS_INFO_DIR ):
    for brain_ini in os.listdir( BRAINS_INFO_DIR ):
        # Two kinds of brain_ini files: 'progress' and 'metadata'
        if 'progress' in brain_ini:
            continue
        
        brain_name = os.path.splitext(brain_ini)[0]
        brain_name = brain_name.replace('_metadata', '')
        
        brain_info = load_ini(os.path.join(BRAINS_INFO_DIR, brain_ini))
        planar_resolution[brain_name] = float(brain_info['planar_resolution_um'])
        stain = brain_info['stain']
        cutting_plane = brain_info['cutting_plane']
        cutting_plane = brain_info['cutting_plane']
        section_thickness = brain_info['section_thickness_um']
        
        all_stacks.append( brain_name )
        if stain == "NTB":
            all_ntb_stacks.append( brain_name )
        elif stain == "Thionin":
            all_nissl_stacks.append( brain_name )
        # Fill in stack_metadata:
        stack_metadata[brain_name] = {'stain': stain,
                                      'cutting_plane': cutting_plane,
                                      'resolution': float(brain_info['planar_resolution_um']),
                                      'section_thickness': section_thickness}
            

#print planar_resolution
stain_to_metainfo = {'ntb': {'detector_id': 799, 'img_version_1': 'NtbNormalized', 
                             'img_version_2': 'NtbNormalizedAdaptiveInvertedGamma'},
                    'thionin': {'detector_id': 19, 'img_version_1': 'gray', 'img_version_2': 'gray'}}

########################################

# prep_id_to_str_2d = {0: 'raw', 1: 'alignedPadded', 2: 'alignedCroppedBrainstem', 3: 'alignedCroppedThalamus', 4: 'alignedNoMargin', 5: 'alignedWithMargin', 6: 'rawCropped'}
prep_id_to_str_2d = {0: 'raw', 1: 'alignedPadded', 2: 'alignedBrainstemCrop', 3: 'alignedThalamusCrop', 4: 'alignedNoMargin', 5: 'alignedWithMargin', 6: 'rawCropped', 7: 'rawBeforeRotation'}
prep_str_to_id_2d = {s: i for i, s in prep_id_to_str_2d.iteritems()}

#######################################

import multiprocessing
NUM_CORES = multiprocessing.cpu_count()

############## Colors ##############

boynton_colors = dict(blue=(0,0,255),
    red=(255,0,0),
    green=(0,255,0),
    yellow=(255,255,0),
    magenta=(255,0,255),
    pink=(255,128,128),
    gray=(128,128,128),
    brown=(128,0,0),
    orange=(255,128,0))

kelly_colors = dict(vivid_yellow=(255, 179, 0),
                    strong_purple=(128, 62, 117),
                    vivid_orange=(255, 104, 0),
                    very_light_blue=(166, 189, 215),
                    vivid_red=(193, 0, 32),
                    grayish_yellow=(206, 162, 98),
                    medium_gray=(129, 112, 102),

                    # these aren't good for people with defective color vision:
                    vivid_green=(0, 125, 52),
                    strong_purplish_pink=(246, 118, 142),
                    strong_blue=(0, 83, 138),
                    strong_yellowish_pink=(255, 122, 92),
                    strong_violet=(83, 55, 122),
                    vivid_orange_yellow=(255, 142, 0),
                    strong_purplish_red=(179, 40, 81),
                    vivid_greenish_yellow=(244, 200, 0),
                    strong_reddish_brown=(127, 24, 13),
                    vivid_yellowish_green=(147, 170, 0),
                    deep_yellowish_brown=(89, 51, 21),
                    vivid_reddish_orange=(241, 58, 19),
                    dark_olive_green=(35, 44, 22))

high_contrast_colors = boynton_colors.values() + kelly_colors.values()

hc_perm = [ 0,  5, 28, 26, 12, 11,  4,  8, 25, 22,  3,  1, 20, 19, 27, 13, 24,
       17, 16, 15,  7, 14, 21, 18, 23,  2, 10,  9,  6]
high_contrast_colors = [high_contrast_colors[i] for i in hc_perm]
name_sided_to_color = {s: high_contrast_colors[i%len(high_contrast_colors)]
                     for i, s in enumerate(all_known_structures_sided) }
name_sided_to_color_float = {s: np.array(c)/255. for s, c in name_sided_to_color.iteritems()}

name_unsided_to_color = {s: high_contrast_colors[i%len(high_contrast_colors)]
                     for i, s in enumerate(all_known_structures) }
name_unsided_to_color_float = {s: np.array(c)/255. for s, c in name_unsided_to_color.iteritems()}

stack_to_color = {n: high_contrast_colors[i%len(high_contrast_colors)] for i, n in enumerate(all_stacks)}
stack_to_color_float = {s: np.array(c)/255. for s, c in stack_to_color.iteritems()}

# Colors for the iso-contours or iso-surfaces of different probabilities.
LEVEL_TO_COLOR_LINE = {0.1: (125,0,125), 0.25: (0,255,0), 0.5: (255,0,0), 0.75: (0,125,0), 0.99: (0,0,255)}
LEVEL_TO_COLOR_VERTEX = {0.1: (0,0,255), 0.25: (125,0,125), 0.5: (0,255,0), 0.75: (255,0,0), 0.99: (0,125,0)}
LEVEL_TO_COLOR_LINE2 = {0.1: (0,125,0), 0.25: (0,0,255), 0.5: (125,0,125), 0.75: (0,255,0), 0.99: (255,0,0)}
LEVEL_TO_COLOR_VERTEX2 = {0.1: (0,125,0), 0.25: (0,0,255), 0.5: (125,0,125), 0.75: (0,255,0), 0.99: (255,0,0)}

####################################

orientation_argparse_str_to_imagemagick_str = \
{'transpose': '-transpose',
 'transverse': '-transverse',
 'rotate90': '-rotate 90',
 'rotate180': '-rotate 180',
 'rotate270': '-rotate 270',
 'rotate45': '-rotate 45',
 'rotate135': '-rotate 135',
 'rotate225': '-rotate 225',
 'rotate315': '-rotate 315',
 'flip': '-flip',
 'flop': '-flop'
}

prep_id_short_str_to_full = {
    'None': 'None',
    'aligned': 'aligned',
    'padded': 'alignedPadded',
    'brainstem': 'alignedBrainstemCrop',
    'wholeslice': 'alignedWithMargin'}

prep_id_num_to_str = {
    0:'raw',
    1:'alignedPadded',
    2:'alignedBrainstemCrop',
    3:'alignedThalamusCrop',
    4:'alignedNoMargin',
    5:'alignedWithMargin',
    6:'rawCropped',
    7:'rawBeforeRotation'}

prep_id_str_to_num = dict(map(reversed, prep_id_num_to_str.items()))

#ordered_pipeline_steps = ['1_setup_metadata', '1_setup_images', '1_setup_sorted_filenames', '1_setup_scripts',
#                     '2_align', '3_mask', '4_crop', '5_fit_atlas_global', '6_fit_atlas_local']

ordered_pipeline_steps = ['1-1_setup_metadata', 
                          '1-2_setup_images', 
                          '1-3_setup_thumbnails',
                          '1-4_setup_sorted_filenames', 
                          '1-5_setup_orientations',
                          '1-6_setup_scripts',
                          '2_align', 
                          '3-1_mask_initial_contours', 
                          '3-2_mask_scripts_1', 
                          '3-3_mask_correct_contours', 
                          '3-4_mask_scripts_2', 
                          '4_crop', 
                          '5_fit_atlas_global', 
                          '6_fit_atlas_local']
