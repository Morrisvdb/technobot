"""Import other functions"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
# from sqlachemy.orm import relationship
from init import Base, engine
import datetime


class User(Base):
    """registers users to keep track of e.g. e-exp"""
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True)
    e_exp = Column(Integer, default=0)

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

class EWar(Base):
    __tablename__ = "EWar"
    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(Integer)
    first_user_id = Column(Integer, ForeignKey("User.id"))
    second_user_id = Column(Integer, ForeignKey("User.id"))
    started_on = Column(DateTime)
    declared_on = Column(DateTime)
    ended_on = Column(DateTime)
    thread_id = Column(Integer)
    surrenderer_id = Column(Integer, default=None)
    winner_id = Column(Integer, default=None)
    isDraw = Column(Boolean)
    wants_peace_id = Column(Integer, default=None)
    declared_peace_on = Column(DateTime, default=None)
    hasStarted = Column(Boolean, default=False)
    last_message_id = Column(Integer)
    hasEnded = Column(Boolean, default=False)

Base.metadata.create_all(engine)
