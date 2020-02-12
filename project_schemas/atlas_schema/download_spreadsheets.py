import argparse

parser = argparse.ArgumentParser(description='Download the tables for the specified animals. Each specified animal will generate one xlsx file. Each table is a seperate sheet in the file')
parser.add_argument('animals', nargs='+', help='The animals to download.')
args = parser.parse_args()
animals = args.animals

import atlas_schema
import pandas as pd
from datetime import date
from tqdm import tqdm

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
    for column_name, column_default, column_type, column_value in definitions:
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
        
        writer = pd.ExcelWriter('./' + prep_id + '.xlsx', engine='xlsxwriter')
        workbook  = writer.book
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})

        # For each table definition
        for table_name, table_class, table_defs in tqdm(atlas_schema.get_dj_tables()):
            # Write the data in current table to excel
            try:
                rows = pd.DataFrame((table_class & ('prep_id = ' + f'"{prep_id}"')).fetch())
            except: 
                rows = pd.DataFrame(table_class.fetch())
            rows.to_excel(writer, sheet_name=table_name, index=False)

            # Format the current spreadsheet
            worksheet = writer.sheets[table_name]
            validates = get_validates(table_defs)
            for index, ((column_name, _, column_type, _), validate) in enumerate(zip(table_defs, validates)):
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

        # Sort the spreadsheet in the provided order
        workbook.worksheets_objs.sort(key=lambda x: atlas_schema.TABLE_NAMES.index(x.name))
        writer.save()
        print('Done')
        
download_spreadsheet(animals)