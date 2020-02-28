import pandas as pd
from sqlalchemy.ext.automap import automap_base
from datetime import date
from tqdm import tqdm 

def get_tables(engine):
    base = automap_base()
    base.prepare(engine, reflect=True)
    name_class = {table_name: table for table_name, table in base.classes.items()}
    name_cols = {table_name: list(table.columns)[:-2] for table_name, table in base.metadata.tables.items()}

    TABLE_NAMES = ['animal', 'organic_label', 'virus', 'histology', 'injection', 'injection_virus', 'scan_run', 'slide', 'slide_czi_to_tif']
    
    return TABLE_NAMES, name_class, name_cols

def download_spreadsheet(prep_id, session, engine):
    TABLE_NAMES, name_class, name_cols = get_tables(engine)
    
    print(f'Downloading the tables for {prep_id}', end='...')

    writer = pd.ExcelWriter('./' + prep_id + '.xlsx', engine='xlsxwriter')
    workbook  = writer.book
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})

    # For each table definition
    for table_name in tqdm(TABLE_NAMES):
        # Write the data in current table to excel
        try:
            query = session.query(name_class[table_name]).filter(name_class[table_name].prep_id == prep_id)
        except AttributeError:
            query = session.query(name_class[table_name])

        rows = pd.read_sql(query.statement, query.session.bind)
        rows = rows.drop(columns=['active', 'created'])

        rows.to_excel(writer, sheet_name=table_name, index=False)

        worksheet = writer.sheets[table_name]
        for index, column in enumerate(name_cols[table_name]):
            # Calculate the letter for current column
            column_letter = chr(ord('A') + index)
            column_range = column_letter + '1:' + column_letter + '1048576'

            # Set the length of the cells 
            worksheet.set_column(column_range, len(column.name) + 2)

            # Add date format
            if str(column.type)[:4] == 'DATE':
                worksheet.conditional_format(column_range, {'type': 'no_errors', 'format': date_format})

            # Add enum validations
            elif str(column.type)[:4] == 'ENUM':
                validate = {
                    'validate': 'list',
                    'value': column.type.enums
                }
                worksheet.data_validation(column_range, validate)

    # Sort the spreadsheet in the provided order
    workbook.worksheets_objs.sort(key=lambda x: TABLE_NAMES.index(x.name))
    writer.save()
        
def upload_spreadsheet(xlsx, session, engine):
    TABLE_NAMES, name_class, name_cols = get_tables(engine)
    
    # For each table in the spreadsheet
    for table_name in tqdm(TABLE_NAMES):
        # Read spreadsheet into dataframes
        spreadsheet = pd.read_excel(xlsx, sheet_name=table_name, dtype=object, parse_dates=True)
        
        # Convert rows in the table to dicts
        dict_rows = spreadsheet.to_dict(orient='records')
        for dict_row in dict_rows:
            # Create sqlalchemy instance and insert/update to the database
            new_row = name_class[table_name]()
            for (key, value), column in zip(dict_row.items(), name_cols[table_name]):
                # Fullfill the nan values in the spreadsheets
                if pd.isnull(value):
                    # If the column has default value, then we do not specify the value
                    if column.server_default is not None or column.autoincrement:
                        continue
                    # If the column is nullable, we put null
                    elif column.nullable:
                        value = None
                    else:
                        print('Error', key, value)
                        return
                        
                # Convert pandas Timestamp to python datetime object
                elif str(column.type)[:4] == 'DATE':
                    value = value.to_pydatetime()
                    
                # Ensure that the enums are string type
                elif str(column.type)[:4] == 'ENUM':
                    if type(value) is float:
                        value = int(value)
                    value = str(value)
                    
                setattr(new_row, key, value)
            session.merge(new_row)
    session.commit()