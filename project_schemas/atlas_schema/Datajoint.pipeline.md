## Listing of steps for the pipeline with datajoint integration

1. New mouse  
1. Enter animal, histology, injection and virus data with spreadsheet
1. Scan slides   
1. Place czi files in correct folder
1. Run script that gets czi files into database
1. Create a spreadsheet where user can add/edit QC information on slides. The script is: download_spreadsheets.py
1. Run czi to tiff script: main-paralle.py
 * Script will query database to get list of czi files from Slides table
 * Script uploads and transforms czi files to tiff files on EC2
 * Script then populates database table: SlidesCziToTif table
 * Script downloads tiff files to birdstore
1. Run existing pipeline. Existing GUI program gets changed to query database animal table for dropdown.
1. Run Neuroglancer alignment setps
   
 




