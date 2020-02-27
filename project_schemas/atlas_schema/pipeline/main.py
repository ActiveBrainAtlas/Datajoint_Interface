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
    #slides_processor.insert_czi_data()
    #slides_processor.process_czi()
    #slides_processor.depth8()
    #slides_processor.rotate_flip()
    slide_processor.test_tables()
  
  
def download():
    download_spreadsheet(prep_id, session, engine)      
    
    
def upload():
    download_spreadsheet(path, session, engine)      
    
if __name__ == '__main__':
    # Parsing argument
    parser = argparse.ArgumentParser(description='Work on Animal')
    parser.add_argument('prep_id', help='Enter the animal prep_id')
    args = parser.parse_args()
    prep_id = args.prep_id
    fetch_and_run(prep_id)