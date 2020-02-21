from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from .atlas_model import Base, AtlasModel
from .slide import Slide


class ScanRun(Base, AtlasModel):
    __tablename__ = 'scan_run'

    scan_date = Column(Date, nullable=False)
    animal_id = Column(Integer, ForeignKey('animal.id'), nullable=False)
    slides = relationship('Slide', lazy=True)


