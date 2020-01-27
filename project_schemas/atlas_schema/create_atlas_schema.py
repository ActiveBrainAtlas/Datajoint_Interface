import yaml
import argparse
import os
import re

from atlas_schema import get_schema 

PATH = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description='Create/drop/populate Datajoint Schema')
parser.add_argument('action', choices=['create', 'drop', 'populate'], help='The action on the schema')
parser.add_argument('--path', default='/nfs/birdstore', help='The absolute path to birdstore on this machine; only valid if the action = create; default is /nfs/birdstore')
args = parser.parse_args()
action = args.action
birdstore_path = args.path

with open(PATH + '/parameters.yaml') as file:
    credential = yaml.load(file, Loader=yaml.FullLoader)

schema = get_schema(credential)

if action == 'create':
    print('Schema created')
elif action == 'drop':
    schema.drop()
    print('Schema dropped')
elif action == 'populate':
    print('This is in the Test mode!')
    Animal.insert1(['DK_37', '', '01-01-0001', 'mouse', '', 'M', '', '', '', '', '01-01-0001', '', '', '', '', '', '', '', ''])
    ScanRun.insert1(['TEST', 'DK_37', '', '', '60X', 0, 0, '01-01-0001', 'CZI', 'L to R', '1', '/Hannah_Liechty/DK37_Final', ''])
    Slides.populate()
    print('Schema populated')