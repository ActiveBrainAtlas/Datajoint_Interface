# Setup
The setup assumes you are in the `Datajoint_Interface/project_schemas/atlas_schema_python_v3/` folder in the terminal.

1) Run `python setup/define_filepaths.py`
    - The code will ask you to define 2 environment variables manually
      - `ENV_DIR`: The absolute path to this github repo on your machine.
      - `DWNLD_ROOT_DIR`: This is the default local root filepath that images will download onto your computer.

2) Run `source setup/config.sh` to initialize ENV variables and virtual environment.

3) Create `setup/credFiles.yaml` that contains the following fields:
    - `aws_fp: <path to aws s3 credentials json file>`
    - `dj_fp: <path to datajoint credentials json file>`


## Manually making the yaml file

1) If the user prefers, the "step 1)" can be replaced with manually creating the yaml file with the following fields:
    - `ENV_DIR : <path to github repo>`
    - `DWNLD_ROOT_DIR : <path to where S3 files download to>`
    
---

# AWS File Organization
Data for the atlas project is consolidated on AWS S3 on several buckets. Descriptions of the relevant buckets as well as a brief description of the organizational structure for retrievable image files is below.

- `Mousebrainatlas-data`: Contains data created at every step of the image-processing pipeline. Contains several copies of any given brain stack at intermediate stages of the processesing. Current schema allows retrieval of _Processed Images_, which are the fully processed slices cropped to only span the brainstem region ("prep2" appended to filename).
- `Mousebrainatlas-rawdata`: Contains all raw data on every brain used in the atlas pipeline. These are in `.jp2` format and are located in folders matching the stack name. This bucket is purely kept in glacier format, a permanent storage option that requires several days to retrieve data.
- `Mousebrainatlas-rawdata-backup`: An exact copy of `Mousebrainatlas-rawdata` but the data is stored using standard storage, making it freely available.
