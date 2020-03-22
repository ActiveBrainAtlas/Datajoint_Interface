from sqlalchemy import Column, String, Integer, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .atlas_model import Base, AtlasModel
from .slide_czi_to_tif import SlideCziTif


class Slide(Base, AtlasModel):
    __tablename__ = 'slide'
    
    id =  Column(Integer, primary_key=True, nullable=False)
    scan_run_id = Column(Integer, ForeignKey('scan_run.id'))
    slide_physical_id = Column(Integer)
    rescan_number = Column(Enum("1", "2", "3"), default="1", nullable=False)
    slide_status = Column(Enum("Bad", "Good"), nullable=False)
    scene_qc_1 = Column(Enum("Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue"), nullable=True)
    scene_qc_2 = Column(Enum("Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue"), nullable=True)
    scene_qc_3 = Column(Enum("Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue"), nullable=True)
    scene_qc_4 = Column(Enum("Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue"), nullable=True)
    scene_qc_5 = Column(Enum("Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue"), nullable=True)
    scene_qc_6 = Column(Enum("Missing one section", "two", "three", "four", "five", "six","O-o-F", "Bad tissue"), nullable=True)
    processed = Column(Boolean(), default=False)
    file_size = Column(Float, nullable=False)
    file_name = Column(String, nullable=False)
    comments = Column(String)
    
    slide_czi_tifs = relationship('SlideCziTif', lazy=True)
