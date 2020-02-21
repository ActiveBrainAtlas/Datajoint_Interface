from sqlalchemy import Column, String, Integer, Float, ForeignKey
from .atlas_model import Base, AtlasModel



class SlideCziTif(Base, AtlasModel):
    __tablename__ = 'slides_czi_to_tif'

    scene_number = Column(Integer) 
    channel = Column(Integer) 
    comments = Column(String)     
    file_name = Column(String)
    file_size = Column(Float)
    
    slide_id = Column(Integer, ForeignKey('slides.id'), nullable=False)


