import datajoint as dj
import yaml
import argparse
import os
import pandas as pd

PATH = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description='Upload the slides for the specified animals. Generate a report describing the difference between the spreadsheet and the database.')
parser.add_argument('xlsx', help='The path to the spreadsheet to upload.')
args = parser.parse_args()
xlsx = args.xlsx

with open(PATH + '/parameters.yaml') as file:
    parameters = yaml.load(file, Loader=yaml.FullLoader)

dj.config['database.user'] = parameters['user']
dj.config['database.password'] = parameters['password']
dj.config['database.host'] = parameters['host']
dj.conn()
schema = dj.schema(parameters['schema'])
schema.spawn_missing_classes()

def slides_diff(old_slides, new_slides):
    old_slides = old_slides.drop(['path', 'comments'], axis=1)
    new_slides = new_slides.drop(['path', 'comments'], axis=1)
    
    # Get the changes in the new_slides
    new_slides_only = old_slides.merge(new_slides, how='outer', indicator=True).query('_merge=="right_only"').drop(['_merge'], axis=1)
    
    # Merge it to the old_slides to see the difference
    diff_slides = old_slides.merge(new_slides_only, how='right', on=['slide_physical_id', 'scan_id', 'prep_id', 'rescan_number'], suffixes=['_old', '_new'])
    
    return diff_slides

def xlsx_slides(xlsx):
    prep_id_slides = pd.read_excel(xlsx, sheet_name=None, converters={'rescan_number': str})

    writer = pd.ExcelWriter(PATH + '/diff.xlsx', engine='xlsxwriter')
    for prep_id, slides in prep_id_slides.items():
        new_slides = slides.fillna('')
        old_slides = (Slides & ('prep_id = ' + f'"{prep_id}"')).fetch(format="frame")
        
        diff_slides = slides_diff(old_slides, new_slides)
        diff_slides.to_excel(writer, sheet_name=prep_id)    
        
        Slides.insert(new_slides.to_dict('records'), replace=True, allow_direct_insert=True)
    writer.save()

xlsx_slides('slides.xlsx')