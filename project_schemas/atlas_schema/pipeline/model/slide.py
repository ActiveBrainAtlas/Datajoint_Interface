from sqlalchemy import Column, String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from .atlas_model import Base, AtlasModel
from .slide_czi_tif import SlideCziTif


class Slide(Base, AtlasModel):
    __tablename__ = 'slides'
    
    slide_physical_id = Column(Integer)
    file_name = Column(String)
    processed = Column(Boolean(), default = False)
    file_size = Column(Float)
    processing_duration = Column(Float)
    
    scan_run_id = Column(Integer, ForeignKey('scan_run.id'), nullable=False)
    slidesCziTifs = relationship('SlideCziTif', lazy=True)


