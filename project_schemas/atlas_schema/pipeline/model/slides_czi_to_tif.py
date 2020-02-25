from sqlalchemy import Column, String, Integer, Float, ForeignKey
from .atlas_model import Base, AtlasModel



class SlidesCziTif(Base, AtlasModel):
    __tablename__ = 'slides_czi_to_tif'
    
    slide_id = Column(Integer, ForeignKey('slides.id'), nullable=False)
    scene_number = Column(Integer) 
    channel = Column(Integer) 
    file_name = Column(String)
    file_size = Column(Float)
    comments = Column(String)