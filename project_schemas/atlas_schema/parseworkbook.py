import argparse
import datetime
import xlrd
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from atlas_classes import Animal

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

# Parsing argument
parser = argparse.ArgumentParser(description='Parse workbook')
parser.add_argument('xlsx', help='The path to the spreadsheet to upload.')
args = parser.parse_args()
xlsx = args.xlsx

book = xlrd.open_workbook(xlsx)
#sheet = book.sheet_by_name('Table 9 ')
animal = book.sheet_by_name('Animal')
histology = book.sheet_by_name('Histology')
injection = book.sheet_by_name('Injection')
injection_virus = book.sheet_by_name('InjectionVirus')
organic_label = book.sheet_by_name('OrganicLabel')
scan_run = book.sheet_by_name('ScanRun')
virus = book.sheet_by_name('Virus')

for r in range(1, animal.nrows):
    new_animal = Animal()
    
    new_animal.prep_id = animal.cell(r,0).value
    new_animal.performance_center = animal.cell(r,1).value
    
    dob_as_datetime = datetime.datetime(*xlrd.xldate_as_tuple(animal.cell(r,2).value, book.datemode))
    new_animal.date_of_birth = dob_as_datetime

    new_animal.species = animal.cell(r,3).value
    new_animal.strain =  animal.cell(r,4).value
    new_animal.sex =  animal.cell(r,5).value
    new_animal.genotype =  animal.cell(r,6).value
    new_animal.breeder_line =  animal.cell(r,7).value
    new_animal.vender =  animal.cell(r,8).value
    new_animal.stock_number =  animal.cell(r,8).value
    new_animal.tissue_source =  animal.cell(r,10).value
    shipping_as_datetime = datetime.datetime(*xlrd.xldate_as_tuple(animal.cell(r,11).value, book.datemode))
    new_animal.ship_date = shipping_as_datetime
    new_animal.shipper =  animal.cell(r,12).value
    new_animal.tracking_number =  animal.cell(r,13).value
    new_animal.aliases_1 =  animal.cell(r,14).value
    new_animal.aliases_2 =  animal.cell(r,15).value
    new_animal.aliases_3 =  animal.cell(r,16).value
    new_animal.aliases_4 =  animal.cell(r,17).value
    new_animal.aliases_5 =  animal.cell(r,18).value
    new_animal.comments =  animal.cell(r,19).value
    
    session.merge(new_animal)
    
session.commit()

for animal in session.query(Animal).all():
    print(animal.__dict__)
        
        