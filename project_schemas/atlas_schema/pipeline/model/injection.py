from sqlalchemy import Column, String, Date, Enum, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .atlas_model import AtlasModel, Base
from .virus_injection import virus_injection


class Injection(Base, AtlasModel):
    __tablename__ = 'injection'
    
    id =  Column(Integer, primary_key=True, nullable=False)
    prep_id = Column(String, ForeignKey('animal.pre_id'), nullable=False)
    label_id = Column(String, ForeignKey('organic_label.id'))
    performance_center = Column(Enum("CSHL", "Salk", "UCSD", "HHMI", "Duke"))
    anesthesia = Column(Enum("ketamine", "isoflurane"))
    method = Column(Enum("iontophoresis", "pressure", "volume"))
    injection_volume = Column(Float, default=0)
    pipet = Column(Enum("glass", "quartz", "Hamilton", "syringe needle"))
    location = Column(String)
    angle = Column(String)
    brain_location_dv = Column(Float, default=0)
    brain_location_ml = Column(Float, default=0)
    brain_location_ap = Column(Float, default=0)
    injection_date = Column(Date)
    transport_days = Column(Integer, default=0)
    virus_count = Column(Integer, default=0)
    
    viruses = relationship("Virus", secondary=virus_injection)
    
    
    def __repr__(self):
        return "Injection(injection_id='%s', prep_id='%s'" % (self.injection_id, self.prep_id)