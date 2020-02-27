from sqlalchemy import Column, String, Integer, ForeignKey, Table
from .atlas_model import AtlasModel, Base

injection_virus = Table('injection_virus', Base.metadata,
                        
    Column('injection_id', Integer, ForeignKey('injection.id'), nullable=False),
    Column('virus_id', Integer, ForeignKey('virus.id'), nullable=False),
)