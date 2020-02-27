from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Date, Boolean, TIMESTAMP
Base = declarative_base()

class AtlasModel(object):
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
                    
    __table_args__ = {'mysql_engine': 'InnoDB'}
    __mapper_args__= {'always_refresh': True}
                            
    created = Column(TIMESTAMP)
    active = Column(Boolean, default=True, nullable=False)