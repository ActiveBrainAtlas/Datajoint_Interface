import datajoint as dj
import numpy as np
from minio import Minio
import json
import yaml
import sys, os

sys.path.append('./lib')
from utilities import *
from initialization_of_db import *

# Fp to file pointers assumes to be 'setup/credFiles.yaml', otherwise pass it directly
# Load AWS Credentials
# `creds` needs the following fields: 'access_key', 'secret_access_key
s3_client = get_s3_client()
# Load Datajoint Credentials
# `dj_creds` needs the following fields: 'user', 'passwd'
dj_creds = get_dj_creds()

# Connect to datajoint server
dj.conn()

# Define which schema you're using
schema = dj.schema('common_atlas_test')
schema.spawn_missing_classes()



@schema
class Animal(dj.Manual):
    definition = """
    animal : char(20)                         # Name for lab mouse/rat, max 20 chars, primary key
    ---------
    Performance_center : enum("", "CSHL", "Salk", "UCSD", "HHMI")
    Date_of_birth      : date                 # (date) the mouse's date of birth
    Species            : enum("mouse", "rat")
    Strain             : varchar(50)
    Sex                : enum("M", "F")       # (M/F) either 'M' for male, 'F' for female
    Genotype           : varchar(100)         # transgenic description, Usually "C57"
    Breeder line       : varchar(100)
    Tissue_source      : enum("", "animal", "brain", "slides")
    Vender             : varchar(100)         # if not from a performance center
    Ship_date          : date
    Shipper            : enum("", "FedEx", "UPS")
    Tracking_number    : varchar(100)
    Aliases 1          : varchar(100)         # names given by others
    Aliases 2          : varchar(100)         # names given by others
    Aliases 3          : varchar(100)         # names given by others
    Comments : varchar(2001)                  # assessment
    """
    
@schema
class Perfusion(dj.Manual): # Everyone should be doing the same type of perfusion
    definition = """
    -> Mouse                        # One injection per mouse
    ----------
    injection_date  : date          # (date) what day was the injection performed

    post_fixation_condition_hours  : int   # (int) How long kept in fix (overnight)
    percent_sucrose_of_fix         : int   # (int) 10 or 20 percent for CSHL stuff

    date_frozen    : date     # (date) The date the brain was frozen
    date_sectioned : date     # (date) The date the brain was sectioned

    injection_type  : varchar(30)   # (Str) what kind of tracer/injection
    perfusion_lab   : varchar(30)   # (Str) Which lab perfused the mouse? This lab also kept the mouse
    
    assessment=''   : varchar(1000) # (Str) optional, qualitative assessment of injection
    """
    
@schema
class Injection(dj.Manual): # Viral injections
    definition = """
    -> Animal
    ----------------
    Performance_center : enum("", "CSHL", "Salk", "UCSD", "HHMI")
    Anesthesia         : enum("", "ketamine", "isoflurane")
    Virus              : varchar(100)       # example 'G-pseudo-typed lenti-cre'; multiple rows for Virus, one for each agent
    Dye                : varchar(100)
    Method             : enum ("", "iontophoresis", "pressure", "volume")
    Pipet              : enum ("", "glass", "metal")
    Concentration (units) : float           # if applicable
    Titer (particles/ml)  : float           # if applicable
    Concentration (mg/ml) : float           # if applicable
    Location              : varchar (20)    # examples: muscle, brain region
    Brain_location_DV (mm): float           # dorsal-ventral relative to Bregma
    Brain_location_ML (mm): float           # medial-lateral relative to Bregma; check if positive
    Brain_location_AP (mm): float           # anterior-posterior relative to Bregma
    Date                  : date
    Goal                  : varchar(2001)
    Comments              : varchar(2001)   # assessment
    """
    
@schema
class Label(dj.Manual):
    definition = """
    -> Label_ID 
    ----------------------
    Type                 : enum("", "counterstain","FP", "antibody", "organic dye")
    Type_of_counterstain : enum("", "thionon", "NtB", "NtFR", "DAPI", "Giemsa", "Syto41") # NtB = Neurotrace blue; NtFR = Neurotrace far red
    Details_of_label     : varchar(200)          # only if not a counterstain
    Tranmission          : enum("yes", "no")
    Tranmission wavelength (nm) : int
    Excitation_wavelength (nm)  : int
    Excitation_range (nm)       : int
    Dichroic_cut (nm)           : int
    Emission_wavelength (nm)    : int
    Emission_range (nm)         : int
    Comments                    : varchar(2001)  # assessment
    """
    
@schema
class Histology(dj.Manual):
    definition = """
    -> Animal
    ----------------
    -> Label
    Performance_center : enum("", "CSHL", "Salk", "UCSD", "HHMI")  # default population is from Injection
    Anesthesia         : enum("", "ketamine", "isoflurane", "pentobarbital", "fatal plus")
    Perfusion age in days : tinyint unsigned
    Perfusion  date    : date
    Perfusion method   : enum("", "standard", "special")           # standard is DK laboratory SOPXX
    Special_perfusion_notes     : varchar(200)
    Post fixation period (days) : tinyint unsigned
    Whole-brain        : enum("Y", "N")
    Block              : varchar(200)    # if applicable
    Date_frozen        : date            # if applicable
    Date_sectioned     : date
    Sectioning_method  : enum ("", "cryoJane", "cryostat', "vibratome", "optical")
    Section_thickness (µm)      :  tinyint unsigned
    Orientation        : enum("coronal", "horizontal", "sagittal", "oblique")
    Oblique_notes      : varchar(200)
    Mounting           : enum("every section", "2nd", "3rd", "4th") # used to automatically populate Placeholder
    Comments           : varchar(2001)    # assessment
    """
# AFTER sectioning, the reporter can either be directly visualized with fuorscence or needs to be 
#  amplified with immunostaining
# Hannah, with Axio Scanner, will manually select level of exposure to reduce saturation but make sure the 
#  the fluorescent molecules are visible
#    - add: CSHL_did_their_own_blackbox_preprocessing : True or False
# Assume calibration

@schema 
class Scan_run(dj.Manual):
    definition = """
    Scan_ID  : charvar(20) # primary key; assigned here; characters and numbers
    ----------------
    Performance_center : enum("", "CSHL", "Salk", "UCSD", "HHMI")  # default population is from Histology
    -> Animal   # multiple rows for Animal IDs, one for each ID
    Machine : enum("", "Zeiss", "Axioscan", "Nanozoomer")
    Objective : enum("60X", "40X", "20X", "10X")
    Resolution (µm): float    # lateral resolution if available
    Number_of_slides : int
    Date: date
    File_type : enum("CZI", "JPEG2000", "NDPI", "NGR")
    Channels_per_slide : enum(1, 2, 3, 4)
    Comments : varchar(2001)  # assessment
    """
    
    
    
@schema 
class Channels(dj.Manual):
    definition = """
    -> Section 
    Channel_number : enum(1, 2, 3, 4) 
    ----------------
    -> Label
    Path : filepath(200)     # proposed "Animal ID"_"Section number"_"channel".tiff) post extraction by preprocessing
    Comments : varchar(2001) # assessment
    """
    
@schema 
class Section(dj.Manual):
    definition = """
    -> Animal
    Section number : int            # This can be reverse ordered for "flipped" directions of cutting. 
    ----------------
    -> Slides
    Scene number : int              #This ordered is manually entered.
    Path : filepath(200)            # example: name1_name2_..._"slide number"_"date"_"scene number"_"section number"tif, "Animal ID"_"ScanID"_"slide number"_"Section number".tif;
    Placeholder : enum("Y", "N")		# used for a missing section
    Comments : varchar(2001)        # assessment
    """

@schema 
class Contours(dj.Manual):
    definition = """
    -> Section
    ------------------
    Snake_contours : filepath(200)    # list of polygons to set-up mask at selected sections. Example filename is "STACK_prep1_thumbnail_initSnakeContours.pkl"
    """

@schema
class Slice(dj.Imported):
    definition = """
    -> Stack
    slice_num       : int           # (int) the unique index of the brain slice. Thickness found in Histology table
    ---
    slice_name      : varchar(100)  # (str) the name of the slice. Naming scheme may vary from lab to lab
    valid           : boolean       # (bool) if false, the slice does not exist
    raw_s3_fp       : varchar(200)  # (str)
    processed_s3_fp : varchar(200)  # (str)
    """
    def make(self, key):
        """
        For every major key in the master table (Stack) the make function will run, once for every unique stack.
        """
        slice_make_function(self, key)
        