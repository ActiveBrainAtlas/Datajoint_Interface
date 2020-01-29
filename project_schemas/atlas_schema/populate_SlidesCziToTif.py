import argparse
from atlas_schema import *

# Parsing argument
parser = argparse.ArgumentParser(description='Create/drop/populate Datajoint Schema')
parser.add_argument('scan_id', type=int, help='The scan run id to populate')
parser.add_argument('--path', default='/nfs/birdstore', help='The absolute path to birdstore on this machine; only valid if the action = create; default is /nfs/birdstore')
args = parser.parse_args()
scan_id = args.scan_id
birdstore_path = args.path

# Populate
scan_runs = (ScanRun & "scan_id = scan_id").fetch(as_dict=True)
for scan_run in scan_runs:
    converted_status = scan_run['converted_status']
    if converted_status != 'not started':
        print(f'Skip {scan_id}: the current converted status for is {converted_status}')
        continue
    
    # Get input and output folder path
    slide_folder_path = scan_run['slide_folder_path']
    converted_folder_path = scan_run['converted_folder_path']
    input_path = birdstore_path + slide_folder_path
    output_path = birdstore_path + converted_folder_path
    
    # Running converter script using input and output paths

    # Read the files in the output folder and populate the table
    for tiff_name in os.listdir(output_path):
        prefix, suffix, _ = tiff_name.split('.')
        prep_id, slide, date_counter = prefix.split('_', 2)
        date, counter = date_counter.rsplit('_', 1)
        _, scene, channel = suffix.split('_')
        
        new_tiff = {} 
        new_tiff['slide_physical_id'] = int(slide[5:])
        new_tiff['prep_id'] = scan_run['prep_id']
        new_tiff['scan_id'] = scan_run['scan_id']
        new_tiff['rescan_number'] = ""
        new_tiff["slide_number"] = int(slide[5:])
        new_tiff["scan_date"] = date.replace('_', '-')
        new_tiff["scene_number"] = scene[1:]
        new_tiff["channel"] = channel[1:]
        new_tiff["scanner_counter"] = int(counter)
        new_tiff["converted_path"] = converted_folder_path + '/' + tiff_name
        Slides_czi_to_tif.insert1(new_tiff, allow_direct_insert=True)