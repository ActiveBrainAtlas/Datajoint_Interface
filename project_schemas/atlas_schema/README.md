# Datajoint utilities
This folder is for python and BASH scripts for creating, uploading and
downloading data from the database.

# parameters.yaml
This file stores the datajoint credientials. We are no longer keeping
this on Github

# atlas_schema.py
This file contains the code to manipulate the tables in the schema. You can use this file to create/drop/populate the table. 
- Create the table: 
	`python definition.py create`
	> You need to specify the absolute path to the birdstore on this machine. 
	The default is /nfs/birdstore.
	> `python definition.py create --path /nfs/another/birdstore`
- Drop the table: 
	`python definition.py drop`
	> You need to confirm by entering `yes` to actually drop the table. 
- Populate the slides table: 
	`python definition.py populate`
	> Currently it is in the **Test** mode, it will automically create a test `Animal` instance and a test `scanRun` instance, so that `Slides` table can be popluated.

# download_spreadsheets.py
This file can help you to download all the data for the specified animal(s) from the database into a spreadsheet. The spreadsheet will be stored in xlsx format with the name of the animal as the prefix to the filename.  
- To download the slides for animals `DK39`:
	`python download_spreadsheet.py DK39`
	> The spreadsheet will be named as DK39.xlsx in the same directory with this file. 

# upload_slides.py
This file can help you upload the updated slides spreadsheet to the database and update the relevent slides if necessary. The input spreadsheet should have the same column names with spreadsheet generated by `download_slides.py`. This file will also output a spredsheet to describe the difference between the slides in the input spreadsheet and in the database. 

- To upload the spreadsheet named`slides.xlsx`stored in the same directory with the file:
	`python upload_slides.py slides.xlsx`
	> The output spreadsheet will be named as diff.xlsx in the same directory with this file. 