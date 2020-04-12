from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
from .atlas_model import Base, AtlasModel



class Task(Base, AtlasModel):
    __tablename__ = 'task'
    id =  Column(Integer, primary_key=True, nullable=False)

    prep_id = Column(String, ForeignKey('animal.prep_id'), nullable=False)
    lookup_id = Column(Integer, ForeignKey('progress_lookup.id'), nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    start_date = Column(DateTime(), server_default=func.now())
    end_date = Column(DateTime())

    def __init__(self, prep_id, lookup_id, completed):
        now = datetime.now()
        self.prep_id = prep_id
        self.lookup_id = lookup_id
        self.completed = completed
        self.start_date = now
        self.end_date = now
        self.created = now


class ProgressLookup(Base, AtlasModel):
    __tablename__ = 'progress_lookup'
    id =  Column(Integer, primary_key=True, nullable=False)

    ordinal = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    original_step = Column(String, nullable=True)
    lookup_id = Column(String, ForeignKey('animal.prep_id'), nullable=False)
    category = Column(String, nullable=False)
    script = Column(String, nullable=True)


