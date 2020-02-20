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
tables = {table_name.replace('_', ''): table for table_name, table in Base.classes.items()}
    
def upload_spreadsheet(xlsx):
    # For each table in the spreadsheet
    for table_name, table_class, table_defs in tqdm(atlas_schema.get_dj_tables()):    
        # Read spreadsheet into dataframes
        spreadsheet = pd.read_excel(xlsx, sheet_name=table_name, dtype=object, parse_dates=True)
        
        for column_name, column_default, column_type, column_value in table_defs:                            
            # Fullfill the nan values in the spreadsheets
            if spreadsheet[column_name].isnull().any():
                if column_default is None:
                    print(f'Error: the column [{column_name}] in table [{table_name}] contains null values')
                    return
                else:
                    if column_default == 'null':
                        column_default = None
                    spreadsheet[column_name] = spreadsheet[column_name].where(pd.notnull(spreadsheet[column_name]), column_default)
                    
        # Convert rows in the table to dicts
        dict_rows = spreadsheet.to_dict(orient='records')
        
        for dict_row in dict_rows:
            # Create sqlalchemy instance and insert/update to the database
            new_row = tables[table_name.lower()]()
            for key, value in dict_row.items():
                # Convert pandas Timestamp to python datetime object
                if type(value) is pd.Timestamp:
                    value = value.to_pydatetime()
                setattr(new_row, key, value)
            session.merge(new_row)
    session.commit()

upload_spreadsheet(xlsx)