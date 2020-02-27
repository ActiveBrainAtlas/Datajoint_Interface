from sqlalchemy import Column, String, Date, Enum, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .atlas_model import AtlasModel, Base


class Histology(Base, AtlasModel):
    __tablename__ = 'histology'
    
    id =  Column(Integer, primary_key=True, nullable=False)
    prep_id = Column(String, ForeignKey('animal.prep_id'), nullable=False)
    virus_id = Column(Integer, ForeignKey('virus.id'))
    label_id = Column(String, ForeignKey('organic_label.id'))
    performance_center = Column(Enum("CSHL", "Salk", "UCSD", "HHMI"))
    anesthesia = Column(Enum("ketamine", "isoflurane", "pentobarbital", "fatal plus"))
    perfusion_age_in_days = Column(Integer, nullable=False)
    perfusion_date = Column(Date)
    exsangination_method = Column(Enum("PBS", "aCSF", "Ringers"))
    fixative_method = Column(Enum("Para", "Glut", "Post fix") )
    special_perfusion_notes = Column(String)
    post_fixation_period = Column(Integer, default=0, nullable=False)
    whole_brain = Column(Enum("Y", "N"))
    block = Column(String)
    date_sectioned = Column(Date)
    sectioning_method = Column(Enum("cryoJane", "cryostat", "vibratome", "optical", "sliding microtiome"))
    section_thickness = Column(Integer, default=20, nullable=False)
    orientation = Column(Enum("coronal", "horizontal", "sagittal", "oblique"))
    oblique_notes = Column(String)
    mounting = Column(Enum("every section", "2nd", "3rd", "4th", "5ft", "6th"))
    counterstain = Column(Enum("thionon", "NtB", "NtFR", "DAPI", "Giemsa", "Syto41"))
    comments = Column(String)

    def __repr__(self):
        return "Histology(prep_id='%s')" % (self.prep_id)