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
for scanRun in scanRuns:
    converted_status = scan_runs['converted_status']
    if converted_status != 'not started':
        print(f'Skip {scan_id}: the current converted status for is {converted_status}')
        continue
        
    slide_folder_path = scanRun['slide_folder_path']
    converted_folder_path = scanRun['converted_folder_path']
    
    # Running converter script

    # After the script is done
    for tiff_name in os.listdir(converted_folder_path):
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
        new_tiff["converted_path"]
        Slides_czi_to_tif.insert1(new_slide, allow_direct_insert=True)