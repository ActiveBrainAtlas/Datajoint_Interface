import datajoint as dj
import yaml
import argparse
import os
import pandas as pd

PATH = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description='Download the slides for the specified animals. The donwloaded slides will be stored in xlsx format.')
parser.add_argument('animals', nargs='+', help='The animals to download.')
args = parser.parse_args()
animals = args.animals

with open(PATH + '/parameters.yaml') as file:
    parameters = yaml.load(file, Loader=yaml.FullLoader)

dj.config['database.user'] = parameters['user']
dj.config['database.password'] = parameters['password']
dj.config['database.host'] = parameters['host']
dj.conn()
schema = dj.schema(parameters['schema'])
schema.spawn_missing_classes()

def slides_xlsx(animals):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(PATH + '/slides.xlsx', engine='xlsxwriter')
    
    for prep_id in animals:
        slides = (Slides & ('prep_id = ' + f'"{prep_id}"')).fetch(format="frame")
        
        if slides.shape[0] == 0:
            print(prep_id, 'does not have any slides')
            continue

        slides.to_excel(writer, sheet_name=prep_id)    
        worksheet = writer.sheets[prep_id]
        
        rescan_ranges = "D2:D" + str(slides.shape[0] + 1)
        worksheet.data_validation(rescan_ranges, {'validate': 'list', 'source': ["", "1", "2", "3"]})
        
        scene_ranges = "E2:J" + str(slides.shape[0] + 1)
        worksheet.data_validation(scene_ranges, {'validate': 'list', 'source': ["", "Missing/Bad", "Out-of-focus", "Bad tissue"]})
    
    writer.save()

print('Downloading slides for animals:', ', '.join(animals))
slides_xlsx(animals)
print('slides.xlsx is generated')