import argparse
import os

PATH = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description='Download the tables for the specified animals. Each specified animal will generate one xlsx file. Each table is a seperate sheet in the file')
parser.add_argument('animals', nargs='+', help='The animals to download.')
args = parser.parse_args()
animals = args.animals

import atlas_schema
import pandas as pd
import inspect
from datetime import date
from tqdm import tqdm

def parse_definition(table):
    definitions = []
    
    columns = [line for line in str(table.heading).split('\n') if ':' in line]
    for column in columns:
        definition = column.split('#')[0]
        prefix, suffix = definition.split(':')
        column_name = prefix.split('=')[0].strip()
        
        types = suffix.split('(')
        column_type = types[0].strip()
        if len(types) > 1:
            column_value = types[1].strip()[:-1]
        else:
            column_value = None
        
        definitions.append((column_name, column_type, column_value))
    return definitions

def get_validates(definitions):
    TRANSFORM_TYPE = {
        'int': 'integer',
        'tinyint': 'integer',
        'float': 'decimal',
        'varchar': 'length',
        'enum': 'list',
        'date': 'date'
    }
    TRANSFORM_VALUE = {
        'int': lambda x: 2147483647,
        'tinyint': lambda x: 127,
        'float': lambda x: 99999999999,
        'varchar': lambda x: int(x),
        'enum': lambda x: list(x.replace("'", "").split(',')),
        'date': lambda x: date(9999, 12, 12)
    }
    
    validates = []
    for column_name, column_type, column_value in definitions:
        validate = None
        if column_type in TRANSFORM_TYPE:
            validate = {}
            validate['validate'] = TRANSFORM_TYPE[column_type]
            validate['criteria'] = '<'
            validate['value'] = TRANSFORM_VALUE[column_type](column_value)
        validates.append(validate)
        
    return validates      

def download_spreadsheet(animals):
    for prep_id in animals:
        print(f'Downloading the tables for {prep_id}', end='...')
        
        writer = pd.ExcelWriter(PATH + '/' + prep_id + '.xlsx', engine='xlsxwriter')
        workbook  = writer.book
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})

        # For each table definition
        for table_name, table in tqdm(inspect.getmembers(atlas_schema, inspect.isclass)):
            # Write the data in current table to excel
            try:
                rows = pd.DataFrame((table & ('prep_id = ' + f'"{prep_id}"')).fetch())
            except: 
                rows = pd.DataFrame(table.fetch())
            rows.to_excel(writer, sheet_name=table_name, index=False)

            # Format the current spreadsheet
            worksheet = writer.sheets[table_name]
            definitions = parse_definition(table)
            validates = get_validates(definitions)
            for index, ((column_name, column_type, column_value), validate) in enumerate(zip(definitions, validates)):
                # Calculate the letter for current column
                column_letter = chr(ord('A') + index)
                column_range = column_letter + '1:' + column_letter + '1048576'
                
                # Set the length of the cells 
                worksheet.set_column(column_range, len(column_name) + 2)
                
                # Add date format
                if column_type == 'date':
                    worksheet.conditional_format(column_range, {'type': 'no_errors', 'format': date_format})

                # Add excel validations
                if validate != None:
                    worksheet.data_validation(column_range, validate)

        writer.save()
        print('Done')
        
download_spreadsheet(animals)