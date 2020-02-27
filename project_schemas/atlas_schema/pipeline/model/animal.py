from sqlalchemy import Column, String, Date, Enum
from sqlalchemy.orm import relationship
from .atlas_model import AtlasModel, Base
from .scan_run import ScanRun


class Animal(Base, AtlasModel):
    __tablename__ = 'animal'
    
    prep_id = Column(String, nullable=False, primary_key=True)
    performance_center = Column(Enum("CSHL", "Salk", "UCSD", "HHMI", "Duke"))
    date_of_birth = Column(Date)
    species = Column(Enum("mouse", "rat"))
    strain = Column(String)
    sex = Column(Enum("M", "F"))
    genotype = Column(String)
    breeder_line = Column(String)
    vender = Column(String)
    stock_number = Column(String)
    tissue_source = Column(String)
    ship_date = Column(Date)
    shipper = Column(Enum("FedEx", "UPS"))
    tracking_number = Column(String)
    aliases_1 = Column(String)
    aliases_2 = Column(String)
    aliases_3 = Column(String)
    aliases_4 = Column(String)
    aliases_5 = Column(String)
    comments = Column(String)
    
    scan_runs = relationship('ScanRun', lazy=True)
    

    def __repr__(self):
        return "Animal(prep_id='%s' is a species='%s'" % (self.prep_id, self.species)