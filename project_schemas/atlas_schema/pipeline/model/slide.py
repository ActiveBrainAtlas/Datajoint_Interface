from sqlalchemy import Column, String, Integer, ForeignKey
from .atlas_model import Base, AtlasModel



class Slide(Base, AtlasModel):
    __tablename__ = 'slides'
    
    slide_physical_id = Column(Integer)
    slides_path = Column(String)
    
    scan_run_id = Column(Integer, ForeignKey('scan_run.id'),
        nullable=False)


