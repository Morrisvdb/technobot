"""Import other functions"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
# from sqlachemy.orm import relationship
from init import Base, engine
import datetime, discord
from init import db


class User(Base):
    """registers users to keep track of e.g. e-exp"""
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True)
    e_exp = Column(Integer, default=0)

class Guild(Base):
    """registers guilds to keep track of e.g. e-wars"""
    __tablename__ = "Guild"
    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(Integer, unique=True)
    max_ewars_server = Column(Integer, default=100) # Maximum number of e-wars per server
    max_ewars_user = Column(Integer, default=5) # Maximum number of e-wars per user
    ewars_interval = Column(Integer, default=15*60) # Interval between E Messages
    ewars_accept_duration = Column(Integer, default=60*5) # Duration of E-War Accept Message
    ewars_cooldown = Column(Integer, default=60*5) # Cooldown between E-Wars
    ereward_win = Column(Integer, default=3) # E-War Reward for winning
    ereward_loss = Column(Integer, default=-1) # E-War Reward for losing
    ereward_draw = Column(Integer, default=0) # E-War Reward for a draw

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

class AcceptWarView(discord.ui.View):
    def __init__(self, target):
        self.target = target
        super().__init__()

    accepted = None
    interaction = None
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.target.id:
            self.interaction = interaction
            self.accepted = True
            await interaction.response.send_message("You have accepted the war.", ephemeral=True)
            self.disable_all_items()
            self.stop()
        else:
            await interaction.response.send_message("You cannot accept this war.", ephemeral=True)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.target.id:
            self.interaction = interaction
            self.accepted = False
            await interaction.response.send_message("You have declined the war.", ephemeral=True)
            self.disable_all_items()
            self.stop()
            
        else:
            await interaction.response.send_message("You cannot decline this war.", ephemeral=True)

class TruceView(discord.ui.View):
    def __init__(self, target):
        self.target = target
        super().__init__()


    accepted = None
    interaction = None
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.target.id:
            self.interaction = interaction
            self.accepted = True
            await interaction.response.send_message("You have accepted the truce.", ephemeral=True)
            self.stop()
        else:
            await interaction.response.send_message("You cannot accept this truce.", ephemeral=True)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.target.id:
            self.interaction = interaction
            self.accepted = False
            await interaction.response.send_message("You have declined the truce.", ephemeral=True)
            self.stop()
        else:
            await interaction.response.send_message("You cannot decline this truce.", ephemeral=True)

class EWarsHelpView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.string_select(placeholder="Select a page", options=[
        discord.SelectOption(label="Information", description="Information about the ewars system and how it works.", emoji="📚"),
        discord.SelectOption(label="Commands", description="Commands for the ewars system.", emoji="📝"),
        discord.SelectOption(label="Config", description="The current config of the ewars system.", emoji="⚙️")],
        )
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        if select.values[0] == "Information":
            newEmbed = discord.Embed(title="Information", description="""
            E-Wars is a game made up by this discord server based on the iconic **E** spam in Technoblade's chat.
            This started off as a simple E-Chain where people would just post an E every once in a while, but it has evolved into a full war system.
            The E-Wars system is a way for people to fight each other in a fun way, and it is completely optional.

            The general idea is that 2 (Sometimes even more) people would try to keep the last **E** in the E-Chain channel for as long as possible.
            Then who held the E for a certain amount of time would win the war, and be awarded E-Experience.

            The game was already played before this bot came allong, but it is made to make it a lot easier to play.
            """, color=discord.Color.nitro_pink())
        elif select.values[0] == "Commands":
            newEmbed = discord.Embed(title="Commands", description="""
            **/ewars help** - Shows the help menu.
            **/ewars declare [Member]** - Starts a war with the mentioned user.
            **/ewars truce [Member]** - Requests a truce with the mentioned user.
            **/ewars surrender** - Surrenders in the current war. (This awards the other user a win.)
            """,
            color=discord.Color.nitro_pink())
        elif select.values[0] == "Rules":
            ...
        elif select.values[0] == "Config":
            guild = db.query(Guild).filter_by(guild_id=interaction.guild.id).first()
            newEmbed = discord.Embed(title="Config", description=f"""
            **Hold Duration** - The amount of time you have to hold the E to win the war. - {guild.ewars_interval} seconds.
            **Cooldown** - The amount of time you have to wait before you can declare another war. - {guild.ewars_cooldown} seconds.
            **Truce/War accept Duration** - The amount of time you have to accept a truce or a war. - {guild.ewars_accept_duration} seconds.
            **Max EWars per User** - The maximum amount of wars a user can have at the same time. - {guild.max_ewars_user}.
            **Max EWars per Guild** - The maximum amount of wars the guild can have at the same time. - {guild.max_ewars_server}.

            **Rewards**
            **Win** - The amount of E-Experience you get for winning a war. - {guild.ereward_win}.
            **Loss** - The amount of E-Experience you get for losing a war. - {guild.ereward_loss}.
            **Truce/Tie** - The amount of E-Experience you get for accepting a truce. - {guild.ereward_draw}.
            """,
            color=discord.Color.nitro_pink()
            )
        else:
            self.stop()
        await interaction.response.edit_message(embed=newEmbed, view=self)
        
class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
    
    @discord.ui.string_select(placeholder="Select a page", options=[
        discord.SelectOption(label="Information", description="Information about the bot and how it works.", emoji="📚"),
        discord.SelectOption(label="Commands", description="Commands for the bot.", emoji="📝")]
    )
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        if select.values[0] == "Information":
            informationEmbed = discord.Embed(title="Information", description="""
            This is a custom discord bot designed by lagg_mine for the TechnoCult server.
            It is open to suggestions, and any porblems that are found can be reported using the **/bug** command.
            """, color=discord.Color.blue())
            await interaction.response.edit_message(embed=informationEmbed, view=self)
        elif select.values[0] == "Commands":
            admin_commands = ""
            commandsEmbed = discord.Embed(title="Commands", color=discord.Color.blue())
            if interaction.user.guild_permissions.administrator:
                commandsEmbed.add_field(name="Config", value="""
                **/config set [Setting] [Value]** - Sets the value of the specified setting.
                **/config get [Setting]** - Gets the value of the specified setting.
                """, inline=False)
                commandsEmbed.add_field(name="Channel-Features", value="""
                **/feature add [Feature]** - Adds the specified feature to the current channel.
                **/feature remove [Feature]** - Removes the specified feature from the current channel.
                **/feature info** - Gives info about the current channel.
                """, inline=False)
                commandsEmbed.add_field(name="Bugreports", value="""
                **/bug list** - Lists all the bugreports.
                **/bug inspect [ID]** - Gives info about the specified bugreport.
                **/bug resolve [ID]** - Resolves the specified bugreport.
                """, inline=False)
                commandsEmbed.add_field(name="Misc", value="""
                **/say [Message]** - Makes the bot say the given message.
                **/typo remove [Link] <Block>** - Removes the specified typo.
                """, inline=False)
            commandsEmbed.add_field(name="Misc", value="""
            **/help** - Shows this help menu.
            """
            , inline=False)
            commandsEmbed.add_field(name="E-Wars", value="""
            **/ewars help** - Shows the ewars help menu.
            **/ewars declare [Member]** - Starts a war with the mentioned user.
            **/ewars truce [Member]** - Requests a truce with the mentioned user.
            **/ewars surrender [Member]** - Surrenders to the mentioned user. (This awards the other user a win.)
            """, inline=False)
            await interaction.response.edit_message(embed=commandsEmbed, view=self)

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
