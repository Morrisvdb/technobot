import discord
from discord import guild_only, Option
from discord.ext import commands
from init import db, config_values, bot
from models import Guild


config_command_group = bot.create_group("config", "Configure the bot for your server.", guild_ids=[977513866097479760])

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @config_command_group.command(name="set", description="Set a configuration value.")
    @guild_only()
    @commands.has_permissions(manage_guild=True)
    async def set(ctx: discord.ApplicationContext,
                    key: Option(description="The configuration key you want to set.", required=True, choices=config_values),
                    value: Option(description="The value you want to set the configuration key to.", required=True)):
        """Set a configuration value."""
        try:
            guild = db.query(Guild).filter_by(guild_id=ctx.guild.id).first()
            setattr(guild, key, value)
            db.add(guild)
            db.commit()
            setEmbed = discord.Embed(
                title="Value set!",
                description=f"""The value for {key} has been set to **{value}**.""",
                color=discord.Color.green()
            )
            await ctx.respond(embed=setEmbed, ephemeral=True)
        except ValueError:
            wrongTypeEmbed = discord.Embed(
                title="Wrong value type!",
                description=f"""The value you entered is not the correct datatype.""",
                color=discord.Color.red()
            )
            await ctx.respond(embed=wrongTypeEmbed, ephemeral=True)
                                

    @config_command_group.command(name="get", description="Get a configuration value.")
    @guild_only()
    @commands.has_permissions(manage_guild=True)
    async def get(ctx: discord.ApplicationContext,
                    key: Option(description="The configuration key you want to get.", required=True, choices=config_values)):
        """Get a configuration value."""
        guild = db.query(Guild).filter_by(guild_id=ctx.guild.id).first()

        getEmbed = discord.Embed(
            title="Value get!",
            description=f"""The value for {key} is **{guild.__dict__[key]}**.""",
            color=discord.Color.green()
        )
        await ctx.respond(embed=getEmbed, ephemeral=True)
    

def setup(bot):
    bot.add_cog(Config(bot))
