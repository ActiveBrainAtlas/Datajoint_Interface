from sqlalchemy import Column, String, Date, Enum, Float, Integer
from sqlalchemy.orm import relationship
from .atlas_model import AtlasModel, Base


class OrganicLabel(Base, AtlasModel):    
    __tablename__ = 'organic_label'
    
    id =  Column(Integer, primary_key=True, nullable=False)
    label_id = Column(String, nullable=False)
    label_type = Column(Enum("Cascade Blue", "Chicago Blue", "Alexa405", "Alexa488", "Alexa647", "Cy2", "Cy3", "Cy5", "Cy5.5", "Cy7", "Fluorescein", "Rhodamine B", "Rhodamine 6G", "Texas Red", "TMR"))
    type_lot_number = Column(String)
    type_tracer = Column(Enum("BDA", "Dextran", "FluoroGold", "DiI", "DiO"))
    type_details = Column(String)
    concentration = Column(Float, default=0)
    excitation_1p_wavelength = Column(Integer, default=0)
    excitation_1p_range = Column(Integer, default=0)
    excitation_2p_wavelength = Column(Integer, default=0)
    excitation_2p_range = Column(Integer, default=0)
    lp_dichroic_cut = Column(Integer, default=0)
    emission_wavelength = Column(Integer, default=0)
    emission_range = Column(Integer, default=0)
    label_source = Column(Enum("",  "Invitrogen", "Sigma", "Thermo-Fisher"))
    souce_details = Column(String)
    comments = Column(String)
        

    def __repr__(self):
        return "OrganicLabel(label_id='%s'" % (self.label_id)