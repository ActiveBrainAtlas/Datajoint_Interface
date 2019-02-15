## Alas Schema

This directory contains all necessary files for the integration of Datajoint into the Atlas Project. The active schema is currently on its second version and so all updated files are appended with "v2".

The following are a list of relevant files:

- `creator_atlas.ipynb`
  - Defines the schema tables and populates with information from S3. Changes with every new version.
- `Accessing Atlas Data.ipynb`
  - Demonstration of retrieving data from the associated schema. Changes with every new version to reflect the new tables made in `creator_atlas.ipynb`.
- `db_manager.ipynb`
  - Notebook demonstrates certain mySQL commands through the package pymysql including listing users, permissions, and making queries.
- `config.ipynb`
  - Simply commands that set sets up the Datajoint environment for a particular user.
- 'utilities.py'
  - Contains utility functions including loading json credentials, retrieving files from S3, and loading information about brains in the Active Atlas
