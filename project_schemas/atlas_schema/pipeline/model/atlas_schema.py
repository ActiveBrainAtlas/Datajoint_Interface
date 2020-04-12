import numpy as np
from datetime import datetime
from controller.preprocessor import make_thumbnail, make_histogram, make_tif
from sql_setup import session, dj, database
import sys
import time

# Get the specified schema reference
schema = dj.schema(database)

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
    comments = NULL              : varchar(2000) # assessment
    active = 1                : tinyint(4) 
    created                   : date    
    """
@schema
class Histology(dj.Manual):
    definition = """
    -> Animal
    ---
    -> [nullable] Virus
    -> [nullable] OrganicLabel
    performance_center = NULL      : enum("CSHL", "Salk", "UCSD", "HHMI") # default population is from Injection
    anesthesia = NULL              : enum("ketamine", "isoflurane", "pentobarbital", "fatal plus")
    perfusion_age_in_days = 0      : tinyint unsigned
    perfusion_date = NULL          : date
    exsangination_method = NULL    : enum("PBS", "aCSF", "Ringers")
    fixative_method = NULL         : enum("Para", "Glut", "Post fix") 
    special_perfusion_notes = NULL : varchar(200)
    post_fixation_period = 0       : tinyint unsigned # (days)
    whole_brain = NULL             : enum("Y", "N")
    block = NULL                   : varchar(200) # if applicable
    date_sectioned = NULL          : date
    sectioning_method = NULL       : enum("cryoJane", "cryostat", "vibratome", "optical", "sliding microtiome")
    section_thickness = 20         : tinyint unsigned # (µm)
    orientation = NULL             : enum("coronal", "horizontal", "sagittal", "oblique")
    oblique_notes = NULL           : varchar(200)
    mounting = NULL                : enum("every section", "2nd", "3rd", "4th", "5ft", "6th") # used to automatically populate Placeholder
    counterstain = NULL            : enum("thionon", "NtB", "NtFR", "DAPI", "Giemsa", "Syto41") # NtB = Neurotrace blue; NtFR = Neurotrace far red
    comments = NULL              : varchar(2000) # assessment
    active = 1                : tinyint(4) 
    created                   : date    
    """


@schema
class Injection(dj.Manual):
    definition = """
    injection_id              : int
    -> Animal
    ---
    -> [nullable] OrganicLabel
    performance_center = NULL : enum("CSHL", "Salk", "UCSD", "HHMI", "Duke")
    anesthesia = NULL         : enum("ketamine", "isoflurane")
    method = NULL             : enum("iontophoresis", "pressure", "volume")
    injection_volume = 0      : float # (nL)
    pipet = NULL              : enum("glass", "quartz", "Hamilton", "syringe needle")
    location = NULL           : varchar(20) # examples: muscle, brain region
    angle = NULL              : varchar(20)
    brain_location_dv = 0     : float # (mm) dorsal-ventral relative to Bregma
    brain_location_ml = 0     : float # (mm) medial-lateral relative to Bregma; check if positive
    brain_location_ap = 0     : float # (mm) anterior-posterior relative to Bregma
    injection_date = NULL     : date
    transport_days = 0        : int
    virus_count = 0           : int
    comments = NULL              : varchar(2000) # assessment
    active = 1                : tinyint(4) 
    created                   : date    
    """


@schema
class InjectionVirus(dj.Manual):
    definition = """
    injection_virus_id : int
    -> Injection
    -> Virus
    ---
    """


@schema
class OrganicLabel(dj.Manual):
    definition = """
    label_id                     : varchar(20)
    ---   
    type = NULL                  : enum("Cascade Blue", "Chicago Blue", "Alexa405", "Alexa488", "Alexa647", "Cy2", "Cy3", "Cy5", "Cy5.5", "Cy7", "Fluorescein", "Rhodamine B", "Rhodamine 6G", "Texas Red", "TMR")
    type_lot_number = NULL       : varchar(20)
    type_tracer = NULL           : enum("BDA", "Dextran", "FluoroGold", "DiI", "DiO")
    type_details = NULL          : varchar(500)
    concentration = 0            : float # (µM) if applicable
    excitation_1p_wavelength = 0 : int # (nm)
    excitation_1p_range = 0      : int # (nm)
    excitation_2p_wavelength = 0 : int # (nm)
    excitation_2p_range = 0      : int # (nm)
    lp_dichroic_cut = 0          : int # (nm)
    emission_wavelength = 0      : int # (nm)
    emission_range = 0           : int # (nm)
    source = NULL                : enum("",  "Invitrogen", "Sigma", "Thermo-Fisher")
    souce_details = NULL         : varchar(100)
    comments = NULL              : varchar(2000) # assessment
    active = 1                : tinyint(4) 
    created                   : date    
    """


@schema
class Virus(dj.Manual):
    definition = """
    virus_id                      : varchar(50)
    ---    
    type = NULL                   : enum("Adenovirus", "AAV", "CAV", "DG rabies", "G-pseudo-Lenti", "Herpes", "Lenti", "N2C rabies", "Sinbis")
    active = NULL                 : enum("yes", "no")
    type_details = NULL           : varchar(500)
    titer = 0                     : float # (particles/ml) if applicable 
    lot_number = NULL             : varchar(20)
    label = NULL                  : enum("YFP", "GFP", "RFP", "histo-tag") 
    label2 = NULL                 : varchar(200)
    excitation_1p_wavelength = 0  : int # (nm) if applicable
    excitation_1p_range = 0       : int # (nm) if applicable
    excitation_2p_wavelength = 0  : int # (nm) if applicable
    excitation_2p_range = 0       : int # (nm) if applicable
    lp_dichroic_cut  = 0          : int # (nm) if applicable
    emission_wavelength = 0       : int # (nm) if applicable
    emission_range  = 0           : int # (nm) if applicable0
    source = NULL                 : enum("Adgene", "Salk", "Penn", "UNC")
    source_details = NULL         : varchar(100)
    comments = NULL              : varchar(2000) # assessment
    active = 1                : tinyint(4) 
    created                   : date    
    """



@schema
class ScanRun(dj.Manual):
    definition = """
    id                      : int auto_increment                            
    -> Animal # currently assumes tissue from a single animals on each slide
    ---
    performance_center = NULL    : enum("CSHL", "Salk", "UCSD", "HHMI") # default population is from Histology
    machine = NULL               : enum("Zeiss", "Axioscan", "Nanozoomer","Olympus VA")
    objective = NULL             : enum("60X", "40X", "20X", "10X")
    resolution = 0               : float # (µm) lateral resolution if available
    number_of_slides = 0         : int
    scan_date = NULL             : date
    file_type = NULL             : enum("CZI", "JPEG2000", "NDPI", "NGR")
    section_schema = NULL        : enum("L to R", "R to L") # agreement is one row
    channels_per_scene = NULL    : enum("1", "2", "3", "4")
    slide_folder_path = NULL     : varchar(200) # the path to the slides folder on birdstore (files to be converted)
    converted_folder_path = NULL : varchar(200) # the path to the slides folder on birdstore after convertion
    converted_status = NULL      : enum("not started", "converted", "converting", "error")
    ch_1_filter_set = NULL       : enum("68", "47", "38", "46", "63", "64", "50") # This is counterstain Channel
    ch_2_filter_set = NULL       : enum("68", "47", "38", "46", "63", "64", "50")
    ch_3_filter_set = NULL       : enum("68", "47", "38", "46", "63", "64", "50")
    ch_4_filter_set = NULL       : enum("68", "47", "38", "46", "63", "64", "50")
    comments = NULL           : varchar(2000) 
    active = 1                : tinyint(4) 
    created                   : date    
    """


@schema
class Slide(dj.Manual):  # prior to segregation of animals and scenes on each slide
    definition = """
    id : int   auto_increment                                             # one per slide
    -> ScanRun
    ---
    slide_status      : enum("Bad", "Good")
    slide_physical_id : int COMMENT 'one per slide',
    scenes = NULL     : int
    rescan_number     : enum("", "1", "2", "3")
    insert_before_one = 0 : tinyint
    scene_qc_1 = NULL   : enum("Out-of-Focus", "Bad tissue") # Missing are ignored and include folds, dirt over sample 
    insert_between_one_two = 0 : tinyint
    scene_qc_2 = NULL   : enum("Out-of-Focus", "Bad tissue")
     insert_between_two_three = 0 : tinyint
    scene_qc_3 = NULL   : enum("Out-of-Focus", "Bad tissue") 
    insert_between_three_four = 0 : tinyint
    scene_qc_4 = NULL   : enum("Out-of-Focus", "Bad tissue") 
    insert_between_four_five = 0 : tinyint
    scene_qc_5 = NULL   : enum("Out-of-Focus", "Bad tissue") 
    insert_between_five_six = 0 : tinyint
    scene_qc_6 = NULL   : enum("Out-of-Focus", "Bad tissue") #"Bad tissue" is interpretted as one missing section
    file_name = NULL  : varchar(200)               # folder on Birdstore
    file_size = 0 : float 
    processing_duration = 0 : float
    processed  = 0: tinyint
    comments = NULL           : varchar(2000) 
    active = 1                : tinyint(4) 
    created                   : date    
    """


@schema
class SlideCziToTif(
    dj.Manual):  # Used to populate sections after Bioconverter; this is the replacement for the "text file"
    definition = """
    id : int auto_increment
    -> Slide
    ----------------
    file_name       : varchar(200)
    section_number int(11) NOT NULL,
    scene_number    : tinyint
    channel         : tinyint
    width = 0       : int 
    height = 0      : int
    scanner_counter : int
    scene_number    :tinyint
    channel         : tinyint 
    file_size = 0   : float 
    processing_duration = 0 : float
    processed  = 0  : tinyint
    comments = NULL : varchar(2000) 
    active = 1      : tinyint 
    created         : date    
       """


@schema
class FileOperation(dj.Computed):
    definition = """
    id : int
    -> SlideCziToTif
    ---
    file_name :  varchar(200) 
    thumbnail: tinyint
    czi_to_tif: tinyint
    histogram: tinyint
    processing_duration: float
    created: datetime
    """

    def make(self, key):
        start = time.time()
        file_id = (SlideCziToTif & key).fetch1('id')
        file_name = (SlideCziToTif & key).fetch1('file_name')
        czi_to_tif = make_tif(session, prep_id, np.asscalar(file_id))
        # histogram = make_histogram(session, prep_id, np.asscalar(file_id))
        # thumbnail = make_thumbnail(prep_id, file_name)
        histogram = 0
        thumbnail = 0
        end = time.time()
        self.insert1(dict(key, file_name=file_name,
                          created=datetime.now(),
                          thumbnail=thumbnail,
                          czi_to_tif=czi_to_tif,
                          processing_duration=end - start,
                          histogram=histogram), skip_duplicates=True)


# End of table definitions


def manipulate_images(id, limit):
    global prep_id
    prep_id = id
    scans = (ScanRun & ('prep_id = "{}"'.format(prep_id))).fetch("KEY")
    if not scans:
        print('No scan data for {}'.format(prep_id))
        sys.exit()
    scan_run_ids = [v for sublist in scans for k, v in sublist.items()]
    slides = [(Slide & 'slide_status = "Good"' & 'scan_run_id={}'.format(i)).fetch("KEY") for i in scan_run_ids][0]
    if not slides:
        print('No slide data for {}'.format(prep_id))
        sys.exit()
    slide_ids = [v for sublist in slides for k, v in sublist.items()]
    slide_ids = tuple(slide_ids)
    restriction = 'slide_id IN {}'.format(slide_ids)
    if len(slide_ids) == 1:
        slide_ids = (slide_ids[0])
        restriction = 'slide_id = {}'.format(slide_ids)
    # print(restriction)
    FileOperation.populate([SlideCziToTif & 'active=1' & restriction], display_progress=True, reserve_jobs=True,
                           limit=limit)
