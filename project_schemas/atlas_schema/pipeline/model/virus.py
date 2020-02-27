from sqlalchemy import Column, String, Date, Enum, Float, Integer
from sqlalchemy.orm import relationship
from .atlas_model import AtlasModel, Base


class Virus(Base, AtlasModel):    
    __tablename__ = 'virus'
    
    id =  Column(Integer, primary_key=True, nullable=False)
    virus_name = Column(String)
    virus_type = Column(Enum("Adenovirus", "AAV", "CAV", "DG rabies", "G-pseudo-Lenti", "Herpes", "Lenti", "N2C rabies", "Sinbis"))
    active = Column(Enum("yes", "no"))
    type_details = Column(String)
    titer = Column(Float, default=0)
    lot_number = Column(String)
    label = Column(Enum("YFP", "GFP", "RFP", "histo-tag") )
    label2 = Column(String)
    excitation_1p_wavelength = Column(Integer, default=0)
    excitation_1p_range = Column(Integer, default=0)
    excitation_2p_wavelength = Column(Integer, default=0)
    excitation_2p_range = Column(Integer, default=0)
    lp_dichroic_cut = Column(Integer, default=0)
    emission_wavelength = Column(Integer, default=0)
    emission_range = Column(Integer, default=0)
    virus_source = Column(Enum("Adgene", "Salk", "Penn", "UNC"))
    source_details = Column(String)
    comments = Column(String)
        

    def __repr__(self):
        return "Virus(virus_id='%s'" % (self.virus_id)