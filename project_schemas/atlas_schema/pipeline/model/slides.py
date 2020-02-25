from sqlalchemy import Column, String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from atlas_model import Base, AtlasModel
from slide_czi_tif import SlideCziTif


class Slides(Base, AtlasModel):
    __tablename__ = 'slides'
    
    scan_run_id = Column(Integer, ForeignKey('scan_run.id'))
    slide_physical_id = Column(Integer)
    rescan_number = Column(Enum("", "1", "2", "3"))
    scene_qc_1 = Column(Enum("", "Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue"))
    scene_qc_2 = Column(Enum("", "Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue"))
    scene_qc_3 = Column(Enum("", "Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue"))
    scene_qc_4 = Column(Enum("", "Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue"))
    scene_qc_5 = Column(Enum("", "Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue"))
    scene_qc_6 = Column(Enum("", "Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue"))
    processed = Column(Boolean(), default=False)
    processing_duration = Column(Float, nullable=False)
    file_size = Column(Float, nullable=False)
    file_name = Column(String, nullable=False)
    comments = Column(String)
    
    slides_czi_tifs = relationship('SlideCziTif', lazy=True)