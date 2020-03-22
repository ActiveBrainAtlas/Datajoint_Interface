Pipeline (existing process with manual and automatic steps)

    Manual: Hannah scans the slides and places the czi files in birdstore at: /net/birdstore/Active_Atlas_Data/data_root/pipeline_data/DK43/czi/
    Manual: Hannah contacts Ed, Ed scans CZI directory and metadata is extracted and entered into the database.
    Manual: Ed contacts Hannah to enter QC info into admin interface: https://activebrainatlas.ucsd.edu/activebrainatlas/admin/
    Manual: Hannah contacts Ed and informs QC is finished. Ed can then run script to extract good czi files into tif files.
    Automatic: Thumbnails are created and links are set up in the admin interface.
    Manual: Users can go into the admin interface and create the sections and export into a list of files.
    Manual: Ed informs users that tifs are ready for the pipeline
    Manual: User (Beth, Hannah, Ed) determines a "root filepath" and starts the docker
        Manual (Existing pipeline): User enters in relevant metadata (slice thickness, resolution, stain)
        Manual (new pipeline): User selects animal from drop down and metadata is automatically filled in.
    Tiff extraction
        Automatic (existing pipeline): Extract Tiffs from CZI, create viewable thumbnails for each image
        Automatic (new pipeline): Tiffs and thumbnails are created in previous step
    Selection of sorted section filenames
        Manual (existing pipeline): User creates the sorted_filenames.txt file with built in GUI. (OR pipeline prompts user to find an existing one)
        Manual (new pipeline): Sections of sorted filenames with appropriate placeholders are created by the user in the admin interface
    Manual(existing pipeline): User scrolls through thumbnails, can rotate by 90 degree increments (batch or individual) (want rostral=left caudal=right) [10 minutes]
    Automatic (existing pipeline): linear 8-bit stretch normalization on NTB images. section-to-section alignment script
    Manual (existing pipeline): User corrects erroneous section-to-section alignments [20 minutes to 1 hour]
    Manual (existing pipeline): User creates initial masks via interactive GUI. Involves drawing large, blocky polygons around the tissue every 50 sections or so. This provides a starting point for the automatic mask generation (the polygons can only shrink) [15 minutes]
    Automatic (existing pipeline): Generate masks automatically using the initial masks made by the user [>12 hours]
    Manual (existing pipeline): User correct erroneous masks by creating/deleting/moving vertices that make up the mask polygon. [severa hours for thionin, 30 minutes for NTB]
    Automatic (existing pipeline): Create "full brain crop" spanning only the tissue covered by masks, dot product images with masks. All images cropped to the same size. NTB images go through the adaptive intensity normalization now that masks are finished.
    Manual (existing pipeline): User create the "brainstem crop" by adjusting 3D bounding box. Uses custom GUI. [5 minutes]
    Automatic (existing pipeline): Generate images using this crop. Images reduced in size.
    Manual (existing pipeline): User specifies center points of the structures "3N_R" and "12N" as anchor points for a rough, global atlas fit.
    Automatic (existing pipeline): Run classifiers on the images. User can specify various parameters.
    Manual (existing pipeline): Run precompute script for Neuroglancer.

