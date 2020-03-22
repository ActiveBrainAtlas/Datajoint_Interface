from sqlalchemy import Column, String, Integer, Float, ForeignKey
from .atlas_model import Base, AtlasModel



class SlideCziTif(Base, AtlasModel):
    __tablename__ = 'slide_czi_to_tif'
    
    id =  Column(Integer, primary_key=True, nullable=False)
    slide_id = Column(Integer, ForeignKey('slide.id'), nullable=False)
    section_number = Column(Integer)
    scene_number = Column(Integer) 
    channel = Column(Integer)
    width = Column(Integer)
    height = Column(Integer) 
    file_name = Column(String)
    file_size = Column(Float)
    comments = Column(String)
    channel_index = Column(Integer)
    scene_index = Column(Integer)
    processing_duration = Column(Float, nullable=False)
