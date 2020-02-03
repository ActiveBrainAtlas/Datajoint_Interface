## Listing of steps for the pipeline with datajoint integration


 1. New mouse  
 2. Enter animal, histology, injection and virus data with spreadsheet
 3. Scan slides   
 4. Place czi files in correct folder
 5. Run script that gets czi files into database
 6. Create a spreadsheet where user can add/edit QC information on slides
 5. Run czi to tiff script: main-paralle.py
   a. Script will query database to get list of czi files from Slides table
   b. Script uploads and transforms czi files to tiff files on EC2
   c. Script then populates database table: SlidesCziToTif table
   d. Script downloads tiff files to birdstore
   
 




