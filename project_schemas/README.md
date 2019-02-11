## Project Schemas

Each folder represents a different Datajoint database with an associated schema. Short, high level descriptions of each are below.

Current Schema:
  - atlas_schema_python
    - Kleinfeld Labs schema made by Alex Newberry. First half involves recording mouse metadata, and keeping records of data from injections, perfusions, and histology sections. Second half relies on a computational pipeline for processing histology sections, stores pointers to large image files and relevant metadata.
  - conrad_schema_matlab
    - Kleinfeld Labs schema made by Conrad Foo. Keeps a record of mice and automatically recording data generated in imaging experiments.  
  - U19_schema_python
    - Preliminary schema made as an example to demonstrate the concept of Datajoint to those who don't use it. Built expecting users to interact using Helium.
