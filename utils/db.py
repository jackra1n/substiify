from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///./data/main.sqlite')
session = sessionmaker(bind=engine)()

Base = declarative_base()

class Daydeal(Base):
    __tablename__ = 'daydeal'

    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer)
    channel_id = Column(Integer)
    role_id = Column(Integer)

    def __init__(self, guild_id, channel_id, role_id):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.role_id = role_id