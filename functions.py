from init import db
from models import EWar, User, Guild
from init import config_values


def identifyUserInWar(user1, user2, guild_id):
        war1 = db.query(EWar).filter_by(guild_id=guild_id, first_user_id=user1, second_user_id=user2).first()
        if war1 is not None:
            return war1
        war2 = db.query(EWar).filter_by(guild_id=guild_id, first_user_id=user2, second_user_id=user1).first()
        if war2 is not None:
            return war2
        else:
            return None
        

def areAtWar(user1, user2, guild_id):
    war1 = db.query(EWar).filter_by(guild_id=guild_id, first_user_id=user1, second_user_id=user2, hasEnded=False).first()
    war2 = db.query(EWar).filter_by(guild_id=guild_id, first_user_id=user2, second_user_id=user1, hasEnded=False).first()
    if war1 or war2 is not None:
        return True
    else:
        return False
    
def createUser(user_id):
    exists = db.query(User).filter_by(user_id=user_id).first()
    if exists is None:
        user = User(user_id=user_id)
        db.add(user)
        db.commit()

def createGuild(guild_id):
    exists = db.query(Guild).filter_by(guild_id=guild_id).first()
    # for value in config_values:
    #     setattr
    if exists is None:
        guild = Guild(guild_id=guild_id)
        db.add(guild)
        db.commit()

def getWarUser(war_id, user_id):
    war = db.query(EWar).filter_by(id=war_id).first()
    if war.first_user_id == user_id:
        return 1
    elif war.second_user_id == user_id:
        return 2
    else:
        return None