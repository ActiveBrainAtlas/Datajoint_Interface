import argparse
import os
import atlas_schema
import pandas as pd
import inspect
from tqdm import tqdm

PATH = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description='Download the tables for the specified animals. Each specified animal will generate one xlsx file. Each table is a seperate sheet in the file')
parser.add_argument('animals', nargs='+', help='The animals to download.')
args = parser.parse_args()
animals = args.animals

def parse_definition(table):
    TRANSFORM_TYPE = {
        'varchar': 'length',
        'enum': 'list'
    }

    xlsx_validate = {}
    columns = [line for line in str(table.heading).split('\n') if ':' in line]

    for column in columns:
        no_comment = column.split('#')[0]
        prefix, suffix = no_comment.split(':')
        column_name = prefix.split('=')[0].strip()
        column_type = suffix.split('(')[0].strip()

        validate = None
        if column_type in TRANSFORM_TYPE:
            validate = {}
            validate['validate'] = TRANSFORM_TYPE[column_type]
            if len(suffix.split('(')) > 1:
                column_value = suffix.split('(')[1].strip()[:-1]

                try:
                    transform_value = int(column_value)
                except ValueError:
                    transform_value = list(column_value.replace("'", "").split(','))

                validate['criteria'] = '<'
                validate['value'] = transform_value
        xlsx_validate[column_name] = validate
        
    return xlsx_validate

for prep_id in animals:
    print(prep_id, end='...')
    writer = pd.ExcelWriter(PATH + '/' + prep_id + '.xlsx', engine='xlsxwriter')

    for table_name, table in tqdm(inspect.getmembers(atlas_schema, inspect.isclass)):
        try:
            rows = pd.DataFrame((table & ('prep_id = ' + f'"{prep_id}"')).fetch())
        except: 
            rows = pd.DataFrame(table.fetch())
        rows.to_excel(writer, sheet_name=table_name)

        worksheet = writer.sheets[table_name]
        for index, (name, validate) in enumerate(parse_definition(table).items()):
            column_letter = chr(ord('B') + index)
            worksheet.set_column(column_letter + ':' + column_letter, len(name) + 2)
            
            if validate != None:
                worksheet.data_validation(column_letter + '1:' + column_letter + '1048576', validate)

    writer.save()
    print('done')