import argparse
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from model.animal import Animal
import sys
from controller.preprocessor import SlideProcessor
from controller.spreadsheet_utilities import upload_spreadsheet, download_spreadsheet

with open('parameters.yaml') as file:
    parameters = yaml.load(file, Loader=yaml.FullLoader)

user = parameters['user']
password = parameters['password']
host = parameters['host']
database = parameters['schema']
connection_string = 'mysql+pymysql://{}:{}@{}/{}'.format(user, password, host, database)
engine = create_engine(connection_string, echo=False)
DBSession = sessionmaker(bind=engine)
session = DBSession()

def fetch_and_run(prep_id):
    try: 
        animal = session.query(Animal).filter(Animal.prep_id == prep_id).one()
    except (NoResultFound):
        print('No results found for prep_id: {}.'.format(prep_id))
        sys.exit()
        
    slide_processor = SlideProcessor(animal, session)
    slide_processor.process_czi_dir()
#     slide_processor.process_czi()
    slide_processor.update_tif_data()
    slide_processor.test_tables()

def download(prep_id, session, engine):
    download_spreadsheet(prep_id, session, engine)    
    
def upload(xlsx, session, engine):
    upload_spreadsheet(xlsx, session, engine)      
    
if __name__ == '__main__':
    # Parsing argument
    print(parameters)
    parser = argparse.ArgumentParser(description='Work on Animal')
    parser.add_argument('--prep_id', help='Enter the animal prep_id')
    parser.add_argument('--xlsx', help='Enter the spreadsheet to upload')
    args = parser.parse_args()
    prep_id = args.prep_id
    xlsx = args.xlsx
    fetch_and_run(prep_id)
    #download(prep_id, session, engine)