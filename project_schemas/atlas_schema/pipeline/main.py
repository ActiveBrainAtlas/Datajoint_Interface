import argparse
from sqlalchemy.orm.exc import NoResultFound
from model.animal import Animal
import sys
from controller.preprocessor import SlideProcessor
from controller.spreadsheet_utilities import upload_spreadsheet, download_spreadsheet
from model.atlas_schema import manipulate_images
from sql_setup import session

def fetch_and_run(prep_id, limit):
    try: 
        animal = session.query(Animal).filter(Animal.prep_id == prep_id).one()
    except (NoResultFound):
        print('No results found for prep_id: {}.'.format(prep_id))
        sys.exit()
        
    slide_processor = SlideProcessor(animal, session)
    #slide_processor.process_czi_dir()
    manipulate_images(prep_id, limit)
    #slide_processor.update_tif_data()
    #slide_processor.test_tables()

def download(prep_id, session, engine):
    download_spreadsheet(prep_id, session, engine)    
    
def upload(xlsx, session, engine):
    upload_spreadsheet(xlsx, session, engine)      
    
if __name__ == '__main__':
    # Parsing argument
    parser = argparse.ArgumentParser(description='Work on Animal')
    parser.add_argument('--prep_id', help='Enter the animal prep_id', required=True)
    parser.add_argument('--xlsx', help='Enter the spreadsheet to upload', required=False)
    parser.add_argument('--limit', help='Enter the number of TIF files to process', required=False)
    args = parser.parse_args()
    prep_id = args.prep_id
    xlsx = args.xlsx
    limit = args.limit or 10000
    limit = int(limit)
    fetch_and_run(prep_id, limit)
    #download(prep_id, session, engine)
