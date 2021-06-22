from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from utils.store import store
import logging
import discord

logger = logging.getLogger(__name__)

engine = create_engine(f'sqlite:///{store.db_path}')
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
        self.message_id = message.id
        self.server_id = None
        self.channel_id = None
        if isinstance(message.channel, discord.channel.TextChannel):
            self.server_id = message.guild.id
            self.channel_id = message.channel.id

class active_giveaways(Base):
    __tablename__ = 'active_giveaways'

    id = Column(Integer, primary_key=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    prize = Column(String)
    creator_user_id = Column(Integer)
    server_id = Column(Integer)
    channel_id = Column(Integer)
    message_id = Column(Integer)

    def __init__(self, creator, end_date, prize, giveaway_message):
        self.start_date = datetime.now()
        self.end_date = end_date
        self.prize = prize
        self.creator_user_id = creator.id
        self.message_id = giveaway_message.id
        self.server_id = giveaway_message.guild.id
        self.channel_id = giveaway_message.channel.id


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

    if not engine.has_table(active_giveaways.__tablename__):
        metadata = MetaData(engine)
        Table(active_giveaways.__tablename__, metadata,
            Column('id', Integer, primary_key=True, nullable=False), 
            Column('start_date', DateTime),
            Column('end_date', DateTime),
            Column('prize', String),
            Column('creator_user_id', Integer),
            Column('server_id', Integer),
            Column('channel_id', Integer), 
            Column('message_id', Integer)
            )
        metadata.create_all()
