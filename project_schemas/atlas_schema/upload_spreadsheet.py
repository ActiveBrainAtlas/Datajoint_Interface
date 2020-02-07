import argparse
import yaml
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.automap import automap_base

# Parsing argument
parser = argparse.ArgumentParser(description='Parse workbook')
parser.add_argument('xlsx', help='The path to the spreadsheet to upload.')
args = parser.parse_args()
xlsx = args.xlsx

with open('parameters.yaml') as file:
    parameters = yaml.load(file, Loader=yaml.FullLoader)
    
# Connect to sqlalchemy
user = parameters['user']
password = parameters['password']
host = parameters['host']
database = parameters['schema']
connection_string = 'mysql+pymysql://{}:{}@{}/{}'.format(user, password, host, database)
engine = create_engine(connection_string, echo=False)
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Get the table definitions
Base = automap_base()
Base.prepare(engine, reflect=True)
tables = {table_name.replace('_', ''): table for table_name, table in Base.classes.items()}

def upload_spreadsheet(xlsx):
    # Read spreadsheet into dataframes
    spreadsheets = pd.read_excel(xlsx, sheet_name=None, parse_dates=True)
    
    # For each table in the spreadsheet
    for table_name, spreadsheet in spreadsheets.items():
        # Convert rows in the table to dicts
        ##TODO, you can't fill in values with fillna('')
        ## There is big difference between null values and empty values in sql
        # https://stackoverflow.com/questions/42255474/pandas-dataframe-nan-values-replace-by-no-values
        spreadsheet = spreadsheet.where(pd.notnull(spreadsheet), None)
        #dict_rows = spreadsheet.fillna('').astype(str).to_dict(orient='records')
        dict_rows = spreadsheet.to_dict(orient='records')
        for dict_row in dict_rows:
            # Create sqlalchemy instance and insert/update to the database
            new_row = tables[table_name.lower()]()
            for key, value in dict_row.items():
                setattr(new_row, key, value)
            session.merge(new_row)
        
    session.commit()

upload_spreadsheet(xlsx)