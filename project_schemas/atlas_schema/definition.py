import datajoint as dj
import yaml
import argparse
import os
import re

PATH = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description='Create/drop/populate Datajoint Schema')
parser.add_argument('action', choices=['create', 'drop', 'populate'], help='The action on the schema')
parser.add_argument('--path', default='/nfs/birdstore', help='The absolute path to birdstore on this machine; only valid if the action = create; default is /nfs/birdstore')
args = parser.parse_args()
action = args.action
birdstore_path = args.path

with open(PATH + '/parameters.yaml') as file:
    parameters = yaml.load(file, Loader=yaml.FullLoader)

dj.config['database.user'] = parameters['user']
dj.config['database.password'] = parameters['password']
dj.config['database.host'] = parameters['host']
dj.conn()
schema = dj.schema(parameters['schema'])

@schema
class Animal(dj.Manual):
    definition = """
    prep_id             : varchar(20)    # Name for lab mouse/rat, max 20 chars, primary key
    ---
    performance_center  : enum("", "CSHL", "Salk", "UCSD", "HHMI", "Duke")
    date_of_birth       : date           # (date) the mouse's date of birth
    species             : enum("mouse", "rat")
    strain = NULL       : varchar(50)
    sex                 : enum("M", "F") # (M/F) either 'M' for male, 'F' for female
    genotype = NULL     : varchar(100)   # transgenic description, usually "C57"; We will need a genotype table
    breeder_line = NULL : varchar(100)                                           # We will need a local breeding table
    vender              : enum ("", "Jackson", "Charles River", "Harlan", "NIH", "Taconic") 
    stock_number = NULL : varchar(100)   # if not from a performance center
    tissue_source       : enum("", "animal", "brain", "slides")
    ship_date           : date
    shipper             : enum("", "FedEx", "UPS")
    tracking_number = NULL : varchar(100)
    aliases_1 = NULL    : varchar(100)   # names given by others
    aliases_2 = NULL    : varchar(100)
    aliases_3 = NULL    : varchar(100)
    aliases_4 = NULL    : varchar(100)
    aliases_5 = NULL    : varchar(100)
    comments            : varchar(2001)  # assessment
    """
     
@schema
class Virus(dj.Manual):
    definition = """
    virus_id              : varchar(20)
    ---
    type                  : enum("", "Adenovirus", "AAV", "CAV", "DG rabies", "G-pseudo-Lenti", "Herpes", "Lenti", "N2C rabies", "Sinbis")
    active = NULL         : enum("", "no")
    type_details  =NULL   : varchar(500)
    titer = 0             : float         # (particles/ml) if applicable
    lot_number            : varchar(20)
    label                 : enum("", "YFP", "GFP", "RFP", "histo-tag") 
    label2                : varchar(200)
    1P_excitation_wavelength = 0  : int           # (nm) if applicable
    1P_excitation_range = 0       : int           # (nm) if applicable
    2P_excitation_wavelength = 0  : int           # (nm) if applicable
    2P_excitation_range = 0       : int           # (nm) if applicable
    LP_dichroic_cut  = 0          : int           # (nm) if applicable
    emission_wavelength = 0    : int           # (nm) if applicable
    emission_range  = 0        : int           # (nm) if applicable0
    source                : enum("", "Adgene", "Salk", "Penn", "UNC")
    source_details        : varchar(100)
    comments = NULL       : varchar(2000) # assessment    
    """
    
@schema
class OrganicLabel(dj.Manual):
    definition = """
    label_id                  : varchar(20)
    ---
    type                      : enum("", "Cascade Blue", "Chicago Blue", "Alexa405", "Alexa488", "Alexa647", "Cy2", "Cy3", "Cy5", "Cy5.5", "Cy7", "Fluorescein", "Rhodamine B", "Rhodamine 6G", "Texas Red", "TMR")
    type_lot_number = NULL    : varchar(20)
    type_tracer               : enum("", "BDA", "Dextran", "FluoroGold", "DiI", "DiO")
    type_details = NULL       : varchar(500)
    concentration (µM) = 0    : float # if applicable
    1P_excitation_wavelength = 0 : int # (nm)
    1P_excitation_range = 0      : int # (nm)
    2P_excitation_wavelength = 0 : int # (nm)
    2P_excitation_range = 0      : int # (nm)
    LP_dichroic_cut = 0          : int # (nm)
    emission_wavelength = 0   : int # (nm)
    emission_range = 0        : int # (nm)
    source                    : enum("",  "Invitrogen", "Sigma", "Thermo-Fisher")
    souce_details = NULL      : varchar(100)
    comments = NULL           : varchar(2000) # assessment
    """

@schema
class Injection(dj.Manual):
    definition = """
    -> Animal
    ---
    -> Virus 
    -> OrganicLabel
    performance_center      : enum("", "CSHL", "Salk", "UCSD", "HHMI")
    anesthesia              : enum("", "ketamine", "isoflurane")
    method                  : enum("", "iontophoresis", "pressure", "volume")
    injection_volume (nL) = 0   : float 
    pipet                   : enum("", "glass", "quartz", "Hamilton", "syringe needle")
    location  = NULL        : varchar(20)   # examples: muscle, brain region
    brain_location_dv = 0    : float         # (mm) dorsal-ventral relative to Bregma
    brain_location_ml = 0    : float         # (mm) medial-lateral relative to Bregma; check if positive
    brain_location_ap = 0    : float         # (mm) anterior-posterior relative to Bregma
    date                     : date
    comments = NULL          : varchar(2001) # assessment
    """

@schema
class Histology(dj.Manual):
    definition = """
    -> Animal
    ---
    -> Virus # default is null
    -> OrganicLabel # default is null
    performance_center          : enum("", "CSHL", "Salk", "UCSD", "HHMI")   # default population is from Injection
    anesthesia                  : enum("", "ketamine", "isoflurane", "pentobarbital", "fatal plus")
    perfusion_age_in_days        : tinyint unsigned
    perfusion_date          : date
    exsangination_method         : enum("", "PBS", "aCSF", "Ringers")
    fixative_method               : enum("", "Para", "Glut", "Post fix") 
    special_perfusion_notes = NULL : varchar(200)
    post_fixation_period = 0   : tinyint unsigned                                               # (days)
    whole_brain                  : enum("Y", "N")
    block = NULL                 : varchar(200)                                                   # if applicable
   date_sectioned                : date
    sectioning_method             : enum("", "cryoJane", "cryostat", "vibratome", "optical", "sliding microtiome")
    section_thickness (µm) = 20   : tinyint unsigned
    orientation                   : enum("coronal", "horizontal", "sagittal", "oblique")
    oblique_notes = NULL          : varchar(200)
    mounting                      : enum("every section", "2nd", "3rd", "4th", "5ft", "6th")       # used to automatically populate Placeholder
    counterstain                  : enum("", "thionon", "NtB", "NtFR", "DAPI", "Giemsa", "Syto41") # NtB = Neurotrace blue; NtFR = Neurotrace far red
    comments                      : varchar(2001)                                                  # assessment
    """

@schema 
class ScanRun(dj.Manual):
    definition = """
    scan_id            : int                            
    -> Animal                                                     # currently assumes tissue from a single animals on each slide
    ---
    performance_center     : enum("", "CSHL", "Salk", "UCSD", "HHMI") # default population is from Histology
    machine                : enum("", "Zeiss", "Axioscan", "Nanozoomer","Olympus VA")
    objective              : enum("60X", "40X", "20X", "10X")
    resolution = 0         : float                                    # (µm) lateral resolution if available
    number_of_slides       : int
    Scan_date              : date
    file_type              : enum("CZI", "JPEG2000", "NDPI", "NGR")
    scenes_per_slide       : enum("1", "2", "3", "4", "5", "6")
    section_scmema         : enum("L to R", "R to L")                 # agreement is one row
    channels_per_scene     : enum("1", "2", "3", "4")
    Slide_folder_path      : varchar(200)                             # the path to the slides folder on birdstore (files to be converted)
    Converted_folder_path  : varchar(200)                         # the path to the slides folder on birdstore after convertion
    Ch_1_filter_set        :enum("", "68", "47", "38", "46", "63", "64", "50")   # This is counterstain Channel
    Ch_2_filter_set        :enum("", "68", "47", "38", "46", "63", "64", "50")
    Ch_3_filter_set        :enum("", "68", "47", "38", "46", "63", "64", "50")
    Ch_4_filter_set        :enum("", "68", "47", "38", "46", "63", "64", "50")
    comments = NULL        : varchar(2001) # assessment
    """

@schema
class Slides(dj.Imported): # prior to segregation of animals and scenes on each slide
    definition = """
    slide_physical_id : int                                               # one per slide
    -> ScanRun
    rescan_number     : enum("", "1", "2", "3")
    ---
    scene_qc_1        : enum("", "Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue") # Missing are ignored and include folds, dirt over sample 
    scene_qc_2        : enum("", "Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue")
    scene_qc_3        : enum("", "Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue") 
    scene_qc_4        : enum("", "Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue") 
    scene_qc_5        : enum("", "Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue") 
    scene_qc_6        : enum("", "Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue") 
        #"Bad tissue" is interpretted as one missing section
    path = NULL        : varchar(200)                                      # example: name1_name2_..._"slide number"_"date".CZI
    comments = NULL    : varchar(2001)                                     # assessment
    """
    
    def make(self, key):
        scan_run = (ScanRun & key).fetch(as_dict=True)[0]
        folder_path = scan_run['folder_path']
        
        for slide_name in os.listdir(birdstore_path + folder_path):
            new_key = key.copy()
            new_key['prep_id'] = key['prep_id']
            new_key['scan_id'] = key['scan_id']
            new_key['slide_physical_id'] = re.findall("\d+", slide_name.split('_')[1])[0]
            new_key['rescan_number'] = ''
            new_key['scene_qc_1'] = ''
            new_key['scene_qc_2'] = ''
            new_key['scene_qc_3'] = ''
            new_key['scene_qc_4'] = ''
            new_key['scene_qc_5'] = ''
            new_key['scene_qc_6'] = ''
            new_key['path'] = birdstore_path + folder_path + '/' + slide_name
            new_key['comments'] = ''
            self.insert1(new_key)
        
@schema
class Slides_CZI_to_TIF(dj.Imported): # Used to populate sections after Bioconverter; this is the replacement for the "text file"
    definition="""
    -> Slides
    -> ScanRun
    -> Animal
    ----------------
    Slide_number    : int
    Scan_Date       : date
    Scene_number    : tinyint
    Channel         : tinyint
    Scanner_counter : int
    Comments = NULL  : varchar(2000) # assessment
    Converted_path  : varchar(200) # example: DK39_slide067_2020_01_02_8271.CZI_S10_C01.tif from bioformat coverter
       # DK39 is the animal name (added by renaming file)
       # slide067 refers to physical slide 67 (added by renaming file)
       # 2020_01_02 is the scan date (imposed by scanner)
       # 8271 is the counter (imposed by scanner)
       # CZI is the file type (imposed by machine)
       # S10 is the scene number (imposed by BioFormats converter; monotonically increasing by not contiguous number)
       # C01 is the channel number (imposed by BioFormats converter)
       """
    
    def make(self, key):
        print('SlidesTIFF:', key)

@schema
class Section(dj.Imported):
    definition="""
    -> Animal
    section_number : int
    ---
    section_qc      : enum("OK","Missing", "Replace")
    ch_1_path       : varchar(200) # Populate from converted Slides and Slides_TIFF
    ch_2_path       : varchar(200)           
    ch_3_path       : varchar(200) 
    ch_4_path       : varchar(200)
    Comments = NULL : varchar(2000) # assessment
    """

@schema
class Processed_section(dj.Imported): #these hold uncropped Tiffs after Section-to-Section alignment ready to be converted for Neuroglancer (Steps 1-5 of current Preprocessing steps)
    definition="""
    -> Section
    ---
    mask_path            : varchar(200)          
    ch_1_normalized_path : varchar(200)  # populate after making histogram normalized and inverted NeuroTrace data
    ch_1_afine_path      : varchar(200)  # Populate from converted Slides and Slides_TIFF after inversion, orientation and translation
    ch_2_afine_path      : varchar(200)           
    ch_3_afine_path      : varchar(200) 
    ch_4_afine_path      : varchar(200)
    Comments = NULL : varchar(2000) # assessment
    """

if action == 'create':
    print('Schema created')
elif action == 'drop':
    schema.drop()
    print('Schema dropped')
elif action == 'populate':
    print('This is in the Test mode!')
    Animal.insert1(['DK_37', '', '01-01-0001', 'mouse', '', 'M', '', '', '', '', '01-01-0001', '', '', '', '', '', '', '', ''])
    ScanRun.insert1(['TEST', 'DK_37', '', '', '60X', 0, 0, '01-01-0001', 'CZI', 'L to R', '1', '/Hannah_Liechty/DK37_Final', ''])
    Slides.populate()
    print('Schema populated')

