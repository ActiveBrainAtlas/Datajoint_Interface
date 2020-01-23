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
    prep_id            : varchar(20)    # Name for lab mouse/rat, max 20 chars, primary key
    ---
    performance_center : enum("", "CSHL", "Salk", "UCSD", "HHMI", "Duke")
    date_of_birth      : date           # (date) the mouse's date of birth
    species            : enum("mouse", "rat")
    strain             : varchar(50)
    sex                : enum("M", "F") # (M/F) either 'M' for male, 'F' for female
    genotype           : varchar(100)   # transgenic description, Usually "C57"
    breeder_line       : varchar(100)
    tissue_source      : enum("", "animal", "brain", "slides")
    vender             : varchar(100)   # if not from a performance center
    ship_date          : date
    shipper            : enum("", "FedEx", "UPS")
    tracking_number    : varchar(100)
    aliases_1          : varchar(100)   # names given by others
    aliases_2          : varchar(100)
    aliases_3          : varchar(100)
    aliases_4          : varchar(100)
    aliases_5          : varchar(100)
    comments           : varchar(2001)  # assessment
    """
    
@schema
class Virus(dj.Manual):
    definition = """
    virus_id              : varchar(20)
    ---
    type                  : enum("", "Adenovirus", "AAV", "CAV", "DG rabies", "G-pseudo-Lenti", "Herpes", "Lenti", "N2C rabies", "Sinbis")
    active                : enum("", "no")
    type_details          : varchar(500)
    titer                 : float         # (particles/ml) if applicable
    lot_number            : varchar(20)
    label                 : enum("", "YFP", "GFP", "RFP", "histo-tag") 
    label2                : varchar(200)
    excitation_wavelength : int           # (nm) if applicable 
    excitation_range      : int           # (nm) if applicable
    dichroic_cut          : int           # (nm) if applicable
    source                : enum("", "Adgene", "Salk", "Penn", "UNC")
    source_details        : varchar(100)
    comments              : varchar(2001) # assessment    
    """
    
@schema
class OrganicLabel(dj.Manual):
    definition = """
    label_id              : varchar(20)
    ---
    type                  : enum("", "Cascade Blue", "Chicago Blue", "Alexa405", "Alexa488", "Alexa647", "Cy2", "Cy3", "Cy5", "Cy5.5", "Cy7", "Fluorescein", "Rhodamine B", "Rhodamine 6G", "Texas Red", "TMR")
    type_lot_number       : varchar(20)
    type_tracer           : enum("", "BDA", "Dextran", "FluoroGold", "DiI", "DiO")
    type_details          : varchar(500)
    concentration         : float # (µM) if applicable
    excitation_wavelength : int # (nm)
    excitation_range      : int # (nm)
    dichroic_cut          : int # (nm)
    emission_wavelength   : int # (nm)
    emission_range        : int # (nm)
    source                : enum("",  "Invitrogen", "Sigma", "Thermo-Fisher")
    souce_details         : varchar(100)
    comments              : varchar(2001) # assessment
    """

@schema
class Injection(dj.Manual):
    definition = """
    -> Animal
    ---
    -> Virus 
    -> OrganicLabel
    performance_center  : enum("", "CSHL", "Salk", "UCSD", "HHMI")
    anesthesia          : enum("", "ketamine", "isoflurane")
    method              : enum("", "iontophoresis", "pressure", "volume")
    pipet               : enum("", "glass", "metal")
    location            : varchar(20)   # examples: muscle, brain region
    brain_location_dv   : float         # (mm) dorsal-ventral relative to Bregma
    brain_location_ml   : float         # (mm) medial-lateral relative to Bregma; check if positive
    brain_location_ap   : float         # (mm) anterior-posterior relative to Bregma
    date                : date
    goal                : varchar(2001)
    comments            : varchar(2001) # assessment
    """

@schema
class Histology(dj.Manual):
    definition = """
    -> Animal
    ---
    -> Virus
    -> OrganicLabel
    performance_center      : enum("", "CSHL", "Salk", "UCSD", "HHMI")   # default population is from Injection
    anesthesia              : enum("", "ketamine", "isoflurane", "pentobarbital", "fatal plus")
    perfusion_age_in_days   : tinyint unsigned
    perfusion_date          : date
    exsangination_method    : enum("", "PBS", "aCSF", "Ringers")
    fixative_method         : enum("", "Para", "Glut", "Post fix") 
    special_perfusion_notes : varchar(200)
    post_fixation_period    : tinyint unsigned                                               # (days)
    whole_brain             : enum("Y", "N")
    block                   : varchar(200)                                                   # if applicable
    date_frozen             : date                                                           # if applicable
    date_sectioned          : date
    sectioning_method       : enum("", "cryoJane", "cryostat", "vibratome", "optical")
    section_thickness       : tinyint unsigned
    orientation             : enum("coronal", "horizontal", "sagittal", "oblique")
    oblique_notes           : varchar(200)
    mounting                : enum("every section", "2nd", "3rd", "4th", "5ft", "6th")       # used to automatically populate Placeholder
    counterstain            : enum("", "thionon", "NtB", "NtFR", "DAPI", "Giemsa", "Syto41") # NtB = Neurotrace blue; NtFR = Neurotrace far red
    comments                : varchar(2001)                                                  # assessment
    """

@schema 
class ScanRun(dj.Manual):
    definition = """
    scan_id            : varchar(20)                            
    -> Animal                                                     # currently assumes tissue from a single animals on each slide
    ---
    performance_center : enum("", "CSHL", "Salk", "UCSD", "HHMI") # default population is from Histology
    machine            : enum("", "Zeiss", "Axioscan", "Nanozoomer","Olympus VA")
    objective          : enum("60X", "40X", "20X", "10X")
    resolution         : float                                    # (µm) lateral resolution if available
    number_of_slides   : int
    Scan_date               : date
    file_type          : enum("CZI", "JPEG2000", "NDPI", "NGR")
    scenes_per_slide   : enum("1", "2", "3", "4", "5", "6")
    section_scmema     : enum("L to R", "R to L")                 # agreement is one row
    channels_per_scene : enum("1", "2", "3", "4")
    Slide_folder_path  : varchar(200)                             # the path to the slides folder on birdstore (files to ve uploaded for cenvertion)
    Converted_folder_path  : varchar(200)                             # the path to the slides folder on birdstore (files to ve uploaded for cenvertion)
    # Add identifiers for all 4 channels. 
    # Channel 1 is always counterstain.
    # Channels 2 to 4 are a virus or an organic label that are choosen from our virus/organicLabel tabels.
    comments           : varchar(2001)                            # assessment
    """

@schema
class Slides(dj.Imported): # prior to segregation of animals and scenes on each slide
    definition = """
    slide_physical_id : int                                               # one per slide
    -> ScanRun
    rescan_number     : enum("", "1", "2", "3")
    ---
    scene_qc_1        : enum("", "Missing", "Out-of-focus", "Bad tissue") # Missing / Bad counterstain are ignored and include folds, dirt over sample 
    scene_qc_2        : enum("", "Missing", "Out-of-focus", "Bad tissue")
    scene_qc_3        : enum("", "Missing", "Out-of-focus", "Bad tissue") 
    scene_qc_4        : enum("", "Missing", "Out-of-focus", "Bad tissue") 
    scene_qc_5        : enum("", "Missing", "Out-of-focus", "Bad tissue") 
    scene_qc_6        : enum("", "Missing", "Out-of-focus", "Bad tissue") 
    path              : varchar(200)                                      # example: name1_name2_..._"slide number"_"date".CZI
    comments          : varchar(2001)                                     # assessment
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
class SlidesTIFF(dj.Imported): # Used to populate sections after Bioconverter; this is the replacement for the "text file"
    definition="""
    -> Slides
    -> ScanRun
    -> Animal
    ----------------
    scene_1_ch_1_path : varchar(200) # example: name1_name2_..._"slide number"_"date"_C00_1.tiff; populate from bioformat coverter
    scene_1_ch_2_path : varchar(200)
    scene_1_ch_3_path : varchar(200)
    scene_1_ch_4_path : varchar(200)
    scene_2_ch_1_path : varchar(200)
    scene_2_ch_2_path : varchar(200)
    scene_2_ch_3_path : varchar(200)
    scene_2_ch_4_path : varchar(200)
    scene_3_ch_1_path : varchar(200)
    scene_3_ch_2_path : varchar(200)
    scene_3_ch_3_path : varchar(200)
    scene_3_ch_4_path : varchar(200)
    scene_4_ch_1_path : varchar(200)
    scene_4_ch_2_path : varchar(200)
    scene_4_ch_3_path : varchar(200)
    scene_4_ch_4_path : varchar(200)
    scene_5_ch_1_path : varchar(200)
    scene_5_ch_2_path : varchar(200)
    scene_5_ch_3_path : varchar(200)
    scene_5_ch_4_path : varchar(200)
    scene_6_ch_1_path : varchar(200)
    scene_6_ch_2_path : varchar(200)
    scene_6_ch_3_path : varchar(200)
    scene_6_ch_4_path : varchar(200)
    comments          : varchar(2001) # assessment
    """
    
    def make(self, key):
        print('SlidesTIFF:', key)

@schema
class Section(dj.Imported):
    definition="""
    -> Animal
    section_number : int
    ---
    section_qc     : enum("OK","Missing", "Replace")
    ch_1_path      : varchar(200) # Populate from converted Slides and Slides_TIFF
    ch_2_path      : varchar(200)           
    ch_3_path      : varchar(200) 
    ch_4_path      : varchar(200)
    comments       : varchar(2001)
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
    comments             : varchar(2001) # assessment
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
