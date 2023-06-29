import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from discord.ext import commands
import discord

DATABASE_URL = "sqlite:///database.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}, echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()
Base = declarative_base()

# TOKEN = os.environ["DISCORD_TOKEN"]
bot = commands.Bot(intents=discord.Intents.all(), command_prefix="!")

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

channelTypes = ["singing", "e-wars", "typo", "bugs"]

config_values = ["max_ewars_server", "max_ewars_user", "ewars_interval", "ewars_accept_duration", "ereward_win", "ereward_loss", "ereward_surrender", "ereward_draw"]

"""The amount of time in seconds between each global check."""
updateCycle = 1


async def db_error(ctx):
    """Sends an embed to the user when there is an error with the database."""
    embed = discord.Embed(
        title="Database Error!",
        description="""There was an error with the database.
        Try again, or contact the bot owner to resolve this issue.""",
        color=discord.Color.red()
    )
    db.rollback()
    await ctx.send(embed=embed)