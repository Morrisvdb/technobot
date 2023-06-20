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
    started_on = Column(DateTime, default=datetime.datetime.now)
    ended_on = Column(DateTime)
    hasEnded = Column(Boolean, default=False)
    thread_id = Column(Integer)
    hasSurrendered = Column(Boolean, default=False)
    winner_id = Column(Integer, default=None)
    loser_id = Column(Integer, default=None)
    isDraw = Column(Boolean)
    last_message_id = Column(Integer, default=None)
    last_message_time = Column(DateTime, default=datetime.datetime.now)
    
class BugReport(Base):
    __tablename__ = "BugReport"
    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer)
    dateTime = Column(DateTime, default=datetime.datetime.now)
    feature = Column(String, default="")
    description = Column(String, default="")
    how = Column(String, default="")
    extra = Column(String, default="")
    isResolved = Column(Boolean, default=False)
    resolvedMessage = Column(Integer, default=None)

Base.metadata.create_all(engine)
