import argparse
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from model.animal import Animal
import sys
from controller.process_animal import SlidesProcessor

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
        
    slides_processor = SlidesProcessor(animal, session)
    #slides_processor.insert_czi_data()
    slides_processor.process_czi()
        
    
if __name__ == '__main__':
    # Parsing argument
    parser = argparse.ArgumentParser(description='Work on Animal')
    parser.add_argument('prep_id', help='Enter the animal prep_id')
    args = parser.parse_args()
    prep_id = args.prep_id
    fetch_and_run(prep_id)