from sqlalchemy import Column, Integer, Date, ForeignKey, Enum, String, Float
from sqlalchemy.orm import relationship
from .atlas_model import Base, AtlasModel
from .slide import Slide


class ScanRun(Base, AtlasModel):
    __tablename__ = 'scan_run'
    
    id =  Column(Integer, primary_key=True, nullable=False)    
    prep_id = Column(String, ForeignKey('animal.prep_id'), nullable=False)
    performance_center = Column(Enum("CSHL", "Salk", "UCSD", "HHMI"))
    machine = Column(Enum("Zeiss", "Axioscan", "Nanozoomer","Olympus VA"))
    objective = Column(Enum("60X", "40X", "20X", "10X"))
    resolution = Column(Float, default=0)
    number_of_slides = Column(Integer, default=0)
    scan_date = Column(Date)
    file_type = Column(Enum("CZI", "JPEG2000", "NDPI", "NGR"))
    scenes_per_slide = Column(Enum("1", "2", "3", "4", "5", "6"))
    section_schema = Column(Enum("L to R", "R to L"))
    channels_per_scene = Column(Enum("1", "2", "3", "4"))
    slide_folder_path = Column(String)
    converted_folder_path  = Column(String)
    converted_status = Column(Enum("not started", "converted", "converting", "error"))
    ch_1_filter_set = Column(Enum("68", "47", "38", "46", "63", "64", "50"))
    ch_2_filter_set = Column(Enum("68", "47", "38", "46", "63", "64", "50"))
    ch_3_filter_set = Column(Enum("68", "47", "38", "46", "63", "64", "50"))
    ch_4_filter_set = Column(Enum("68", "47", "38", "46", "63", "64", "50"))
    comments = Column(String)

    slides = relationship('Slide', lazy=True)
    
    
    def __repr__(self):
        return "ScanRun(prep_id='%s', scan_id='%s'" % (self.prep_id, self.scan_id)


