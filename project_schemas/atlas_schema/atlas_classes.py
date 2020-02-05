from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
Base = declarative_base()


class Animal(Base):
    __tablename__ = 'animal'
    
    prep_id = Column(String, primary_key=True)
    performance_center = Column(String)
    date_of_birth = Column(Date)
    species = Column(String)
    strain = Column(String)
    sex = Column(String)
    genotype = Column(String)
    breeder_line = Column(String)
    vender = Column(String)
    stock_number = Column(String)
    tissue_source = Column(String)
    ship_date = Column(Date)
    shipper = Column(String)
    tracking_number = Column(String)
    aliases_1 = Column(String)
    aliases_2 = Column(String)
    aliases_3 = Column(String)
    aliases_4 = Column(String)
    aliases_5 = Column(String)
    comments = Column(String)

    def __repr__(self):
        return "Animal(pre_id='%s' is a species='%s'" % (self.prep_id, self.species)
    
    

virus_injection = Table('virus_injection', Base.metadata,
    Column('injection_id', Integer, ForeignKey('injection.injection_id')),
    Column('virus_id', Integer, ForeignKey('virus.virus_id'))
)

class Injection(Base):
    __tablename__ = 'injection'
    injection_id = Column(Integer, primary_key=True)
    viruses = relationship("Virus", secondary=virus_injection)

class Virus(Base):
    __tablename__ = 'virus'
    virus_id = Column(Integer, primary_key=True)