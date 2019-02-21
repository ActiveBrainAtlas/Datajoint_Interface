## Setup

The setup assumes you are in the `Datajoint_Interface/project_schemas/atlas_schema_python_v3/` folder in the terminal.

1) Run `python setup/define_filepaths.py`
    - The code will ask you to define 2 environment variables manually
      - `ENV_DIR`: The absolute path to this github repo on your machine.
    - `export DWNLD_ROOT_DIR=""`
      - `DWNLD_ROOT_DIR`: This is the default local root filepath that images will download onto your computer.
1) If the user prefers, the previous step can be replaced with manually creating the yaml file with the following fields:
    - `ENV_DIR : <>`
    - `DWNLD_ROOT_DIR : <>`
2) Run `source setup/config.sh` to initialize ENV variables and virtual environment.
3) Create `setup/credFiles.yaml` that contains the following fields:
    - aws_fp: <path to aws s3 credentials json file>
    - dj_fp: <path to datajoint credentials json file>
