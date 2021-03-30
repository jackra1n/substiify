from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

engine = create_engine('sqlite:///./data/main.sqlite')
session = sessionmaker(bind=engine)()

Base = declarative_base()

class Daydeal(Base):
    __tablename__ = 'daydeal'

    id = Column(Integer, primary_key=True)
    server_id = Column(Integer)
    channel_id = Column(Integer)
    role_id = Column(Integer)

    def __init__(self, server_id, channel_id, role_id):
        self.server_id = server_id
        self.channel_id = channel_id
        self.role_id = role_id

class command_history(Base):
    __tablename__ = 'command_history'

    id = Column(Integer, primary_key=True)
    command = Column(String)
    date = Column(DateTime)
    user_id = Column(Integer)
    server_id = Column(Integer)
    channel_id = Column(Integer)
    message_id = Column(Integer)

    def __init__(self, message):
        self.command = message.content
        self.date = datetime.now()
        self.user_id = message.author.id
        self.server_id = message.guild.id
        self.channel_id = message.channel.id
        self.message_id = message.id

# Creates database tables if the don't exist
def create_database():
    if not engine.has_table(Daydeal.__tablename__):
        metadata = MetaData(engine)
        Table(Daydeal.__tablename__, metadata,
            Column('id', Integer, primary_key=True, nullable=False), 
            Column('server_id', Integer),
            Column('channel_id', Integer), 
            Column('role_id', Integer)
            )
        metadata.create_all()
    
    if not engine.has_table(command_history.__tablename__):
        metadata = MetaData(engine)
        Table(command_history.__tablename__, metadata,
            Column('id', Integer, primary_key=True, nullable=False), 
            Column('command', String),
            Column('date', DateTime),
            Column('user_id', Integer),
            Column('server_id', Integer),
            Column('channel_id', Integer), 
            Column('message_id', Integer)
            )
        metadata.create_all()