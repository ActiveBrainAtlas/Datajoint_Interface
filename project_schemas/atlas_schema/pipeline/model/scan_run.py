from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .atlas_model import Base, AtlasModel
from .slide import Slide


class ScanRun(Base, AtlasModel):
    __tablename__ = 'scan_run'
    
    slides = relationship('Slide', lazy=True)

    animal_id = Column(Integer, ForeignKey('animal.id'),
        nullable=False)


