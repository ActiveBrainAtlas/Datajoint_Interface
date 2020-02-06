from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, Date, Table, ForeignKey
from sqlalchemy.orm import relationship
Base = declarative_base()


class Animal(Base):
    __tablename__ = 'animal'
    
    prep_id = Column(String, primary_key=True)
    performance_center = Column(String)
    date_of_birth = Column(Date)
    species = Column(String)
    strain = Column(String)
    sex = Column(String)
    genotype = Column(String)
    breeder_line = Column(String)
    vender = Column(String)
    stock_number = Column(String)
    tissue_source = Column(String)
    ship_date = Column(Date)
    shipper = Column(String)
    tracking_number = Column(String)
    aliases_1 = Column(String)
    aliases_2 = Column(String)
    aliases_3 = Column(String)
    aliases_4 = Column(String)
    aliases_5 = Column(String)
    comments = Column(String)

    def __repr__(self):
        return "Animal(prep_id='%s' is a '%s'" % (self.prep_id, self.species)
   
   
   
class OrganicLabel(Base):
    __tablename__ = 'organic_label'
    
    label_id = Column(String, primary_key=True)
    type = Column(String)
    type_lot_number = Column(String)
    type_tracer = Column(String)
    type_details = Column(String)
    concentration = Column(Float, default=0)
    excitation_1p_wavelength = Column(Integer, default=0)
    excitation_1p_range = Column(Integer, default=0)
    excitation_2p_wavelength = Column(Integer, default=0)
    excitation_2p_range = Column(Integer, default=0)
    lp_dichroic_cut = Column(Integer, default=0)
    emission_wavelength = Column(Integer, default=0)
    emission_range = Column(Integer, default=0)
    source = Column(String)
    souce_details = Column(String)
    comments = Column(String)


virus_injection = Table('virus_injection', Base.metadata,
    Column('injection_id', Integer, ForeignKey('injection.injection_id')),
    Column('virus_id', Integer, ForeignKey('virus.virus_id')),
    Column('prep_id', String)
)

class Injection(Base):
    __tablename__ = 'injection'
    
    injection_id = Column(Integer, primary_key=True)
    prep_id = Column(String, ForeignKey('animal.prep_id'), primary_key=True)
    label_id = Column(String, ForeignKey('organic_label.label_id'))
    performance_center = Column(String)
    anesthesia = Column(String)
    method = Column(String)
    injection_volume = Column(Float)
    pipet = Column(String)
    location = Column(String)
    angle = Column(String)
    brain_location_dv = Column(Float)
    brain_location_ml = Column(Float)
    brain_location_ap = Column(Float)
    injection_date = Column(Date)
    transport_days = Column(Integer)
    virus_count = Column(Integer, default=0) # default 0
    viruses = relationship("Virus", secondary=virus_injection)

class Virus(Base):
    __tablename__ = 'virus'
    
    virus_id = Column(Integer, primary_key=True)
    type = Column(String)
    active = Column(String)
    type_details = Column(String)
    titer = Column(Float, default=0)
    lot_number = Column(String)
    label = Column(String)
    label2 = Column(String)
    excitation_1p_wavelength = Column(Integer, default=0)
    excitation_1p_range = Column(Integer, default=0)
    excitation_2p_wavelength = Column(Integer, default=0)
    excitation_2p_range = Column(Integer, default=0)
    lp_dichroic_cut = Column(Integer, default=0)
    emission_wavelength = Column(Integer, default=0)
    emission_range = Column(Integer, default=0)
    source = Column(String)
    source_details = Column(String)
    comments = Column(String)
    
    
class ScanRun(Base):
    __tablename__ = 'scan_run'
    
    scan_id = Column(Integer, primary_key=True)
    prep_id = Column(String, ForeignKey('animal.prep_id'), primary_key=True)
    performance_center = Column(String)
    machine = Column(String)
    objective = Column(String)
    resolution = Column(Float, default=0)
    number_of_slides = Column(Integer)
    scan_date = Column(Date)
    file_type = Column(String)
    scenes_per_slide = Column(String)
    section_schema = Column(String)
    channels_per_scene = Column(String)
    slide_folder_path = Column(String)
    converted_folder_path  = Column(String)
    converted_status = Column(String)
    ch_1_filter_set = Column(String)
    ch_2_filter_set = Column(String)
    ch_3_filter_set = Column(String)
    ch_4_filter_set = Column(String)
    comments = Column(String)

    
class Histology(Base):
    __tablename__ = 'histology'
    
    prep_id= Column(String, ForeignKey('animal.prep_id'), primary_key=True)
    virus_id = Column(String, ForeignKey('virus.virus_id'))
    label_id = Column(String, ForeignKey('virus.label_id'))
    performance_center = Column(String)
    anesthesia = Column(String)
    perfusion_age_in_days = Column(Integer)
    perfusion_date = Column(Date)
    exsangination_method = Column(String)
    fixative_method = Column(String)
    special_perfusion_notes = Column(String)
    post_fixation_period = Column(Integer, default=0)
    whole_brain = Column(String)
    block = Column(String)
    date_sectioned = Column(Date)
    sectioning_method = Column(String)
    section_thickness = Column(Integer, default=20)
    orientation = Column(String)
    oblique_notes = Column(String)
    mounting = Column(String)
    counterstain = Column(String)
    comments = Column(String)
    
    
    
    