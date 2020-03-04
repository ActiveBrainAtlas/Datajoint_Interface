import os
import yaml
import datajoint as dj
from controller.preprocessor import DATA_ROOT, TIF, NORMALIZED, SCALED
import cv2 as cv
from skimage import io
import numpy as np

PATH = os.path.dirname(os.path.abspath(__file__))
with open(PATH + '/parameters.dj.yaml') as file:
    credential = yaml.load(file, Loader=yaml.FullLoader)
    
# Connect to the datajoint database
dj.config['database.user'] = credential['user']
dj.config['database.password'] = credential['password']
dj.config['database.host'] = credential['host']
dj.conn()

# Get the specified schema reference
schema = dj.schema(credential['schema'])


# Below are the table definitions
@schema
class Animal(dj.Manual):
    definition = """
    prep_id                   : varchar(20) # Name for lab mouse/rat, max 20 chars, primary key
    ---    
    performance_center = NULL : enum("CSHL", "Salk", "UCSD", "HHMI", "Duke")
    date_of_birth = NULL      : date # the mouse's date of birth
    species = NULL            : enum("mouse", "rat")
    strain = NULL             : varchar(50)
    sex = NULL                : enum("M", "F") # (M/F) either 'M' for male, 'F' for female
    genotype = NULL           : varchar(100) # transgenic description, usually "C57"; We will need a genotype table 
    breeder_line = NULL       : varchar(100) # We will need a local breeding table 
    vender = NULL             : enum ("Jackson", "Charles River", "Harlan", "NIH", "Taconic") 
    stock_number = NULL       : varchar(100) # if not from a performance center
    tissue_source = NULL      : enum("animal", "brain", "slides")
    ship_date = NULL          : date
    shipper = NULL            : enum("FedEx", "UPS")
    tracking_number = NULL    : varchar(100)
    aliases_1 = NULL          : varchar(100) # names given by others 
    aliases_2 = NULL          : varchar(100) 
    aliases_3 = NULL          : varchar(100)
    aliases_4 = NULL          : varchar(100)
    aliases_5 = NULL          : varchar(100)
    comments = NULL           : varchar(2001) # assessment
    """

@schema 
class ScanRun(dj.Manual):
    definition = """
    id                      : int                            
    -> Animal # currently assumes tissue from a single animals on each slide
    ---
    performance_center = NULL    : enum("CSHL", "Salk", "UCSD", "HHMI") # default population is from Histology
    machine = NULL               : enum("Zeiss", "Axioscan", "Nanozoomer","Olympus VA")
    objective = NULL             : enum("60X", "40X", "20X", "10X")
    resolution = 0               : float # (µm) lateral resolution if available
    number_of_slides = 0         : int
    scan_date = NULL             : date
    file_type = NULL             : enum("CZI", "JPEG2000", "NDPI", "NGR")
    scenes_per_slide = NULL      : enum("1", "2", "3", "4", "5", "6")
    section_schema = NULL        : enum("L to R", "R to L") # agreement is one row
    channels_per_scene = NULL    : enum("1", "2", "3", "4")
    slide_folder_path = NULL     : varchar(200) # the path to the slides folder on birdstore (files to be converted)
    converted_folder_path = NULL : varchar(200) # the path to the slides folder on birdstore after convertion
    converted_status = NULL      : enum("not started", "converted", "converting", "error")
    ch_1_filter_set = NULL       : enum("68", "47", "38", "46", "63", "64", "50") # This is counterstain Channel
    ch_2_filter_set = NULL       : enum("68", "47", "38", "46", "63", "64", "50")
    ch_3_filter_set = NULL       : enum("68", "47", "38", "46", "63", "64", "50")
    ch_4_filter_set = NULL       : enum("68", "47", "38", "46", "63", "64", "50")
    comments = NULL              : varchar(2001) # assessment
    """

@schema
class Slide(dj.Manual): # prior to segregation of animals and scenes on each slide
    definition = """
    id : int                                               # one per slide
    rescan_number     : enum("", "1", "2", "3")
    -> ScanRun
    ---
    scene_qc_1 = ""   : enum("", "Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue") # Missing are ignored and include folds, dirt over sample 
    scene_qc_2 = ""   : enum("", "Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue")
    scene_qc_3 = ""   : enum("", "Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue") 
    scene_qc_4 = ""   : enum("", "Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue") 
    scene_qc_5 = ""   : enum("", "Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue") 
    scene_qc_6 = ""   : enum("", "Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue") #"Bad tissue" is interpretted as one missing section
    file_name = NULL  : varchar(200)               # folder on Birdstore
    comments = NULL   : varchar(2001) # assessment
    """

@schema
class SlideCziToTif(dj.Manual): # Used to populate sections after Bioconverter; this is the replacement for the "text file"
    definition = """
    id : int
    -> Slide
    ----------------
    slide_number    : int
    scan_date       : date
    scene_number    : tinyint
    channel         : tinyint
    scanner_counter : int
    file_name       : varchar(200)
    comments = NULL : varchar(2000) # assessment
       """


def lognorm(img):
    img = (img/256).astype('uint8')
    lxf = np.log(img + 0.005)
    lxf = np.where(lxf < 0, 0, lxf)
    xmin = min(lxf.flatten()) 
    xmax = max(lxf.flatten())
    return -lxf*255/(xmax-xmin) + xmax*255/(xmax-xmin) #log of data and stretch 0 to 255

def linnorm(img):
    img = (img/256).astype('uint8')
    flat = img.flatten()
    hist,bins = np.histogram(flat,256)
    cdf = hist.cumsum() #cumulative distribution function
    cdf = 255 * cdf / cdf[-1] #normalize
    #use linear interpolation of cdf to find new pixel values
    img_norm = np.interp(flat,bins[:-1],cdf)
    img_norm = np.reshape(img_norm, img.shape)
    img_norm = 255 - img_norm
    return img_norm



def norm_file(prep_id, tif):
    io.use_plugin('tifffile')
    INPUT = os.path.join(DATA_ROOT, prep_id, TIF)
    OUTPUT = os.path.join(DATA_ROOT, prep_id, NORMALIZED)
    input_tif = os.path.join(INPUT, tif)
    output_tif = os.path.join(OUTPUT, tif)

    img = io.imread(input_tif)
    if '_C0_' in input_tif:
        img = linnorm(img)
    else:
        img = lognorm(img)
    io.imsave(output_tif, img.astype('uint8'), check_contrast=False)



def scale(prep_id, tif):
    INPUT = os.path.join(DATA_ROOT, prep_id, NORMALIZED)
    OUTPUT = os.path.join(DATA_ROOT, prep_id, SCALED)
    scale_percent = 1 / float(32) # percent of original size
    input_tif = os.path.join(INPUT, tif)
    output_tif = os.path.join(OUTPUT, tif)
    img = io.imread(input_tif)
    
    
    width = int(img.shape[1] * scale_percent)
    height = int(img.shape[0] * scale_percent)
    dim = (width, height)
    # resize image
    xf = cv.resize(img, dim, interpolation = cv.INTER_AREA)
    #io.imsave(output_tif, xf, check_contrast=False)
    cv.imwrite(output_tif, xf)

       
@schema
class FileOperation(dj.Computed):
    definition = """
    file_operation_id : int
    -> SlideCziToTif
    ---
    file_name :  varchar(200)  # (Voxels) original image width 
    operation :  varchar(50)  # (voxels) original image height
    """
    
    def make(self, key):
        file_name = (SlideCziToTif & key).fetch1('file_name')
        norm_file('DK43', file_name)
        self.insert1(dict(key, file_operation_id=1, file_name=file_name, operation='normalizing'))
        scale('DK43', file_name)
        self.insert1(dict(key, file_operation_id=2, file_name=file_name, operation='scaling'))
# End of table definitions 
