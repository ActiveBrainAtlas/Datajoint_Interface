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
    slide_folder_path = scan_run['slide_folder_path']

    for slide_name in os.listdir(birdstore_path + slide_folder_path):
        new_slide = {}
        new_slide['slide_physical_id'] = re.findall("\d+", slide_name.split('_')[1])[0]
        new_slide['prep_id'] = scan_run['prep_id']
        new_slide['scan_id'] = scan_run['scan_id']
        new_slide['rescan_number'] = ''
        new_slide['scene_qc_1'] = ''
        new_slide['scene_qc_2'] = ''
        new_slide['scene_qc_3'] = ''
        new_slide['scene_qc_4'] = ''
        new_slide['scene_qc_5'] = ''
        new_slide['scene_qc_6'] = ''
        new_slide['slides_path'] = slide_folder_path + '/' + slide_name
        new_slide['comments'] = ''
        Slides.insert1(new_slide, allow_direct_insert=True)