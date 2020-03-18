import argparse
import sys
import numpy as np
from model.atlas_schema import FileOperation, Animal, Slide, ScanRun, SlideCziToTif

    
def manipulate_images(prep_id):
    scan_run_ids = (ScanRun & ('prep_id = ' + f'"{prep_id}"')).fetch('id')
    scan_run_ids = tuple(scan_run_ids[:])
    if len(scan_run_ids) == 0:
        print('Exiting, no data for that prep_id')
        sys.exit()
        
    if len(scan_run_ids) == 1:
        scan_run_ids = scan_run_ids[0]
        slide_ids = (Slide & ('scan_run_id = ' + str(scan_run_ids) )).fetch('id')
    else:
        slide_ids = (Slide & ('scan_run_id IN ' + str(scan_run_ids)  )).fetch('id')
        
    
    slide_ids = tuple(slide_ids[:])
    if len(slide_ids) == 1:
        slide_ids = slide_ids[0]
        FileOperation.populate([SlideCziToTif & 'slide_id = ' + str(slide_ids) ], display_progress=True)
    else:
        FileOperation.populate([SlideCziToTif & 'slide_id IN ' + str(slide_ids) ], display_progress=True)
        
    
    

    
if __name__ == '__main__':
    # Parsing argument
    parser = argparse.ArgumentParser(description='Work on Animal')
    parser.add_argument('--prep_id', help='Enter the animal prep_id', required=True)
    args = parser.parse_args()
    prep_id = args.prep_id
    manipulate_images(prep_id)
