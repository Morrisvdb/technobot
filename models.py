"""Import other functions"""
from sqlalchemy import Column, Integer, String
from init import Base, engine


class User(Base):
    """registers users to keep track of e.g. e-exp"""
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True)
    e_exp = Column(Integer)

class Channel(Base):
    """registers channel features"""
    __tablename__ = "Channel"
    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(Integer)
    channel_id = Column(Integer)
    channel_type = Column(String)
    # Channel Types:
    # See channelTypes in init.py

class Typo(Base):
    """registers typos"""
    __tablename__ = "Typo"
    id = Column(Integer, primary_key=True, index=True)
    message_url = Column(String)
    channel_id = Column(Integer)
    user_id = Column(Integer)
    guild_id = Column(Integer)
    reporter_id = Column(Integer)
    public_msg_id = Column(Integer)
    blocked = Column(Integer)

Base.metadata.create_all(engine)
