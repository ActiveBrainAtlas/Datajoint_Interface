import argparse

# Parsing argument
parser = argparse.ArgumentParser(description='Parse and upload the xlsx file to database. The format of xlsx file should be the same as the one downloaded using "download_spreadsheets" script. This script will update the dataset based on primary keys of each row: Update the row if its primary keys are in the database; otherwise, insert a new row')
parser.add_argument('xlsx', help='The path to the xlsx file to upload.')
args = parser.parse_args()
xlsx = args.xlsx

import atlas_schema
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.automap import automap_base
from datetime import date
from tqdm import tqdm
    
# Connect to sqlalchemy
user = atlas_schema.credential['user']
password = atlas_schema.credential['password']
host = atlas_schema.credential['host']
database = atlas_schema.credential['schema']
connection_string = 'mysql+pymysql://{}:{}@{}/{}'.format(user, password, host, database)
engine = create_engine(connection_string, echo=False)
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Get the table definitions
Base = automap_base()
Base.prepare(engine, reflect=True)
tables = {''.join(word.title() for word in table_name.split('_')): table for table_name, table in Base.classes.items()}
    
def upload_spreadsheet(xlsx):
    # For each table in the spreadsheet
    for table_name, table_class, table_defs in tqdm(atlas_schema.get_dj_tables()):    
        # Read spreadsheet into dataframes
        spreadsheet = pd.read_excel(xlsx, sheet_name=table_name, dtype=object, parse_dates=True)
        
        # Convert rows in the table to dicts
        dict_rows = spreadsheet.to_dict(orient='records')
        
        for dict_row in dict_rows:
            # Create sqlalchemy instance and insert/update to the database
            new_row = tables[table_name]()
            for (key, value), (column_name, column_default, column_type, column_value) in zip(dict_row.items(), table_defs):
                # Fullfill the nan values in the spreadsheets
                if pd.isnull(value):
                    if column_default == 'null' or column_default is None:
                        value = None
                    else:
                        value = column_default
                        
                # Convert pandas Timestamp to python datetime object
                elif column_type == 'date':
                    value = value.to_pydatetime()
                    
                # Ensure that the enums are string type
                elif column_type == 'enum':
                    if type(value) is float:
                        value = int(value)
                    value = str(value)
                    
                setattr(new_row, key, value)
            session.merge(new_row)
    session.commit()

upload_spreadsheet(xlsx)