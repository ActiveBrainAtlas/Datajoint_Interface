import argparse
import sys
from model.atlas_schema import FileOperation, Slide, ScanRun, SlideCziToTif
    
def manipulate_images(prep_id):

    scans = (ScanRun & ('prep_id = "{}"'.format(prep_id))).fetch("KEY")
    if not scans:
        print('No scan data for {}'.format(prep_id))
        sys.exit()
    scan_run_ids = [v for sublist in scans for k, v in sublist.items()]
    slides = [(Slide & 'slide_status = "Good"' & 'scan_run_id={}'.format(i)).fetch("KEY") for i in scan_run_ids][0]
    if not slides:
        print('No slide data for {}'.format(prep_id))
        sys.exit()
    slide_ids = [v for sublist in slides for k, v in sublist.items()]
    slide_ids = tuple(slide_ids)
    restriction = 'slide_id IN {}'.format(slide_ids)
    if len(slide_ids) == 1:
        slide_ids = (slide_ids[0])
        restriction = 'slide_id = {}'.format(slide_ids)

    FileOperation.populate([SlideCziToTif & 'active=1' & restriction ], display_progress=True, reserve_jobs=True)
    
    

if __name__ == '__main__':
    # Parsing argument
    parser = argparse.ArgumentParser(description='Work on Animal')
    parser.add_argument('--prep_id', help='Enter the animal prep_id', required=True)
    args = parser.parse_args()
    prep_id = args.prep_id
    manipulate_images(prep_id)
