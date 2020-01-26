import datajoint as dj

def get_schema(credential):
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
        prep_id            : varchar(20) # Name for lab mouse/rat, max 20 chars, primary key
        ---
        performance_center : enum("", "CSHL", "Salk", "UCSD", "HHMI", "Duke")
        date_of_birth      : date # (date) the mouse's date of birth
        species            : enum("mouse", "rat")
        strain             : varchar(50) # (= NULL)
        sex                : enum("M", "F") # (M/F) either 'M' for male, 'F' for female
        genotype           : varchar(100) # transgenic description, usually "C57"; We will need a genotype table (= NULL)
        breeder_line       : varchar(100) # We will need a local breeding table (= NULL)
        vender             : enum ("", "Jackson", "Charles River", "Harlan", "NIH", "Taconic") 
        stock_number       : varchar(100) # if not from a performance center (= NULL)
        tissue_source      : enum("", "animal", "brain", "slides")
        ship_date          : date
        shipper            : enum("", "FedEx", "UPS")
        tracking_number    : varchar(100) # (= NULL)
        aliases_1          : varchar(100) # names given by others (= NULL)
        aliases_2          : varchar(100) # (= NULL) 
        aliases_3          : varchar(100) # (= NULL)
        aliases_4          : varchar(100) # (= NULL)
        aliases_5          : varchar(100) # (= NULL)
        comments           : varchar(2001) # assessment
        """
         
    @schema
    class Virus(dj.Manual):
        definition = """
        virus_id  : varchar(20)
        ---
        type                  : enum("", "Adenovirus", "AAV", "CAV", "DG rabies", "G-pseudo-Lenti", "Herpes", "Lenti", "N2C rabies", "Sinbis")
        active                : enum("", "no") # (= NULL)
        type_details          : varchar(500) # (= NULL)
        titer                 : float # (particles/ml) if applicable (= 0)
        lot_number            : varchar(20)
        label                 : enum("", "YFP", "GFP", "RFP", "histo-tag") 
        label2                : varchar(200)
        excitation_wavelength : int # (nm) if applicable (= 0)
        excitation_range      : int # (nm) if applicable (= 0)
        dichroic_cut          : int # (nm) if applicable (= 0)
        emission_wavelength   : int # (nm) if applicable (= 0)
        emission_range        : int # (nm) if applicable (= 0)
        source                : enum("", "Adgene", "Salk", "Penn", "UNC")
        source_details        : varchar(100)
        comments              : varchar(2000) # assessment # (= NULL)
        """
        
    @schema
    class OrganicLabel(dj.Manual):
        definition = """
        label_id                  : varchar(20)
        ---
        type                      : enum("", "Cascade Blue", "Chicago Blue", "Alexa405", "Alexa488", "Alexa647", "Cy2", "Cy3", "Cy5", "Cy5.5", "Cy7", "Fluorescein", "Rhodamine B", "Rhodamine 6G", "Texas Red", "TMR")
        type_lot_number           : varchar(20) # (= NULL)
        type_tracer               : enum("", "BDA", "Dextran", "FluoroGold", "DiI", "DiO")
        type_details              : varchar(500) # (= NULL)
        concentration             : float # (µM) if applicable (= 0)
        excitation_wavelength     : int # (nm) (= 0)
        excitation_range          : int # (nm) (= 0)
        dichroic_cut              : int # (nm) (= 0)
        emission_wavelength       : int # (nm) (= 0)
        emission_range            : int # (nm) (= 0)
        source                    : enum("",  "Invitrogen", "Sigma", "Thermo-Fisher")
        souce_details             : varchar(100) # (= NULL)
        comments                  : varchar(2000) # assessment (= NULL)
        """
    
    @schema
    class Injection(dj.Manual):
        definition = """
        -> Animal
        ---
        -> Virus 
        -> OrganicLabel
        performance_center : enum("", "CSHL", "Salk", "UCSD", "HHMI")
        anesthesia         : enum("", "ketamine", "isoflurane")
        method             : enum("", "iontophoresis", "pressure", "volume")
        injection_volume   : float # (nL) (= 0)
        pipet              : enum("", "glass", "quartz", "Hamilton", "syringe needle")
        location           : varchar(20) # examples: muscle, brain region (= NULL)
        brain_location_dv  : float # (mm) dorsal-ventral relative to Bregma (= 0)
        brain_location_ml  : float # (mm) medial-lateral relative to Bregma; check if positive (= 0)
        brain_location_ap  : float # (mm) anterior-posterior relative to Bregma (= 0)
        date               : date
        comments           : varchar(2001) # assessment (= NULL)
        """
    
    @schema
    class Histology(dj.Manual):
        definition = """
        -> Animal
        ---
        -> Virus # (= null)
        -> OrganicLabel # (= null)
        performance_center      : enum("", "CSHL", "Salk", "UCSD", "HHMI")   # default population is from Injection
        anesthesia              : enum("", "ketamine", "isoflurane", "pentobarbital", "fatal plus")
        perfusion_age_in_days   : tinyint unsigned
        perfusion_date          : date
        exsangination_method    : enum("", "PBS", "aCSF", "Ringers")
        fixative_method         : enum("", "Para", "Glut", "Post fix") 
        special_perfusion_notes : varchar(200) # (= NULL)
        post_fixation_period    : tinyint unsigned # (days) (= 0)
        whole_brain             : enum("Y", "N")
        block                   : varchar(200) # if applicable (= NULL)
        date_sectioned          : date
        sectioning_method       : enum("", "cryoJane", "cryostat", "vibratome", "optical", "sliding microtiome")
        section_thickness       : tinyint unsigned # (µm) (= 20)
        orientation             : enum("coronal", "horizontal", "sagittal", "oblique")
        oblique_notes           : varchar(200) # (= NULL)
        mounting                : enum("every section", "2nd", "3rd", "4th", "5ft", "6th") # used to automatically populate Placeholder
        counterstain            : enum("", "thionon", "NtB", "NtFR", "DAPI", "Giemsa", "Syto41") # NtB = Neurotrace blue; NtFR = Neurotrace far red
        comments                : varchar(2001) # assessment
        """
    
    @schema 
    class ScanRun(dj.Manual):
        definition = """
        scan_id                : int                            
        -> Animal # currently assumes tissue from a single animals on each slide
        ---
        performance_center     : enum("", "CSHL", "Salk", "UCSD", "HHMI") # default population is from Histology
        machine                : enum("", "Zeiss", "Axioscan", "Nanozoomer","Olympus VA")
        objective              : enum("60X", "40X", "20X", "10X")
        resolution             : float # (µm) lateral resolution if available (= 0)
        number_of_slides       : int
        scan_date              : date
        file_type              : enum("CZI", "JPEG2000", "NDPI", "NGR")
        scenes_per_slide       : enum("1", "2", "3", "4", "5", "6")
        section_scmema         : enum("L to R", "R to L") # agreement is one row
        channels_per_scene     : enum("1", "2", "3", "4")
        slide_folder_path      : varchar(200) # the path to the slides folder on birdstore (files to be converted)
        converted_folder_path  : varchar(200) # the path to the slides folder on birdstore after convertion
        ch_1_filter_set        : enum("", "68", "47", "38", "46", "63", "64", "50") # This is counterstain Channel
        ch_2_filter_set        : enum("", "68", "47", "38", "46", "63", "64", "50")
        ch_3_filter_set        : enum("", "68", "47", "38", "46", "63", "64", "50")
        ch_4_filter_set        : enum("", "68", "47", "38", "46", "63", "64", "50")
        comments               : varchar(2001) # assessment (= NULL)
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
        scene_qc_6        : enum("", "Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue") #"Bad tissue" is interpretted as one missing section
        path              : varchar(200) # example: name1_name2_..._"slide number"_"date".CZI (= NULL)
        comments          : varchar(2001) # assessment (= NULL)
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
        slide_number    : int
        scan_date       : date
        scene_number    : tinyint
        channel         : tinyint
        scanner_counter : int
        comments        : varchar(2000) # assessment (= NULL)
        converted_path  : varchar(200) # example: DK39_slide067_2020_01_02_8271.CZI_S10_C01.tif from bioformat coverter
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
        comments        : varchar(2000) # assessment (= NULL)
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
        comments             : varchar(2000) # assessment (= NULL)
        """
        
    return schema