## Setup

- Fill the following two environmental variables in `./setup/config.sh`
  - `export ENV_DIR="<GIT PROJECT PATH>/Datajoint_Interface/project_schemas/atlas_schema_python_v3"`
    - The absolute path to this directory on your local machine.
  - `export DWNLD_ROOT_DIR=""`
    - This is the local root filepath that images will download onto your computer using the "data_accessor_atlas_v3.ipynb" notebook.
- Run `source setup/config.sh` to set up ENV variables and virtual environment.
- Create `setup/credFiles.yaml` that contains the following fields:
  - aws_fp: <path to aws s3 credentials json file>
  - dj_fp: <path to datajoint credentials json file>
