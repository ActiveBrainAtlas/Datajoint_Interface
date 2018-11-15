## Atlas project

The Atlas takes in histology sections as input and constructs a 3D atlas with gnerated probability volumes for certain structures of interest. No actual experimentation, fairly linear pipeline.

## Collection of tables

- __Mouse__
  - [Mouse table](mouse_info.md)
  
- __Raw Stack__
  - Brain Name: the designated name of the mouse brain: `UCSD001`
  - Orientation: saggital, coronal, or horozontal: `saggital`
  - Number of sections: total number of histology sections made: `500`
  - List of unusable sections: Should be a part of "Sorted Filenames"
  - Sorted filenames: a list of the filenames numbered in order: 
  - Extensions: filename extensions: `jp2`
  - Microscope resolution: microns per pixel: `0.46um`
  - Section thickness: The thickness in microns of each slice: `20um`
  - Stain type: Injected compound for neuron visualization: `Ntb`
  - Stack: The stack itself, nearly 1 terrabyte. A series of images about 2GB each.
    - Raw data stored on AWS S3, bucketname "mousebrainatlas-rawdata": [LINK](https://s3.console.aws.amazon.com/s3/buckets/mousebrainatlas-rawdata/?region=us-east-1&tab=overview)
  
- __Preprocessing Stages__
  - Downsampling factor: All thumbnail images will be downsampled by this amount: `32X`
  - *Everything below this point is a stack of images with a certain transformation/normalization/cut applied to them.*
    - All this data can be found on AWS S3, bucketname "mousebrainatlas-data", folder "CSHL_data_processed/": [LINK](https://s3.console.aws.amazon.com/s3/buckets/mousebrainatlas-data/CSHL_data_processed/?region=us-east-1&tab=overview)
  - Thumbnail: 
  - Aligned thumbnails: 
  - Global intensity normalization: 
  - Thumbnail masks: 
  - Lossless Local Adaptive Intensity Normalized Brainstem Crops: 
  
- __Patch Features__
  - Inception-bn-blue: Pretrained neural network used for probabalistic segmentation, needed as input.
  - Feature data for each slice: `SLICENAME_prep2_none_win7_inception-bn-blue_features.bp`
  - Location data for each slice: `SLICENAME_prep2_none_win7_inception-bn-blue_locations.bp`

- __Probability Volumes__
  - Inception-bn-blue: Pretrained neural network used for probabalistic segmentation, needed as input.
  - Classifier settings: region classifier settings encoded as a 3 digit number: `899`
  - Regions: regions of interest that probability volumes are generated for: `3N, 4N, 12N`
  - Volumes: Files with probabalistic score voluems, gradients, and global coordinates
  - Scoremaps: Scoremaps for every ROI
  - Contour images: jpeg files of slices overlain with probability contours
