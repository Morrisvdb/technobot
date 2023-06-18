import discord
from discord.ext import commands
import sqlalchemy
from discord import guild_only, Option
from init import bot, channelTypes, db, db_error
from models import Channel


features_command_group = bot.create_group("function", "Add a feature to a channel unlocking the commands paired with that feature.")

class Features(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @features_command_group.command(name="add", description="Add a feature to a channel unlocking the commands paired with that feature")
    @guild_only()
    @commands.has_permissions(manage_channels=True)
    async def add_feature(ctx: discord.ApplicationContext,
                  feature: Option(input_type=str,
                                  name="add",
                                  description="The feature you want to add.",
                                  choices=channelTypes,
                                  required=True)
                  ):
        currentChannel = db.query(Channel).filter_by(guild_id=ctx.guild.id, channel_id=ctx.channel.id, channel_type=feature).first()
        if currentChannel is not None:
            embed = discord.Embed(
                title="Feature already added!",
                description=f"""The feature {feature} has already been added to this channel.""",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=embed)
        else:
            try:
                channel = db.query(Channel).filter_by(guild_id=ctx.guild.id, channel_id=ctx.channel.id, channel_type=None).first()
                """Checks if there is already an empty column for this channel."""
                if channel is not None:
                    channel.channel_type = feature
                else:
                    newChannel = Channel(guild_id=ctx.guild.id, channel_id=ctx.channel.id, channel_type=feature)
                    db.add(newChannel)

                embed = discord.Embed(
                    title="Feature added!",
                    description=f"""The feature {feature} has been added to this channel.""",
                    color=discord.Color.green()
                )
                await ctx.respond(embed=embed)
            except sqlalchemy.exc.OperationalError:
                db_error(ctx)
        db.commit()

    @features_command_group.command()
    @guild_only()
    @commands.has_permissions(manage_channels=True)
    async def remove_feature(ctx: discord.ApplicationContext,
                     feature: Option(input_type=str,
                                     description="The feature you want to remove.",
                                     choices=channelTypes,
                                     required=True)):
        currentChannel = db.query(Channel).filter_by(guild_id=ctx.guild.id, channel_id=ctx.channel.id, channel_type=feature).first()
        if currentChannel is None:
            embed = discord.Embed(
                title="Feature not added!",
                description=f"""The feature {feature} has not been added to this channel.""",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=embed)
        else:
            try:
                db.delete(currentChannel)
                embed = discord.Embed(
                    title="Feature removed!",
                    description=f"""The feature {feature} has been removed from this channel.""",
                    color=discord.Color.green()
                )
                await ctx.respond(embed=embed)
            except sqlalchemy.exc.OperationalError:
                db_error(ctx)
        db.commit()
    
    @features_command_group.command()
    @guild_only()
    @commands.has_permissions(manage_channels=True)
    async def info_feature(ctx: discord.ApplicationContext):
        channel = db.query(Channel).filter_by(guild_id=ctx.guild.id, channel_id=ctx.channel.id).first()
        if channel is None:
            try:
                channel = Channel(guild_id=ctx.guild.id, channel_id=ctx.channel.id, channel_type=None)
                db.add(channel)
                db.commit()
            except sqlalchemy.exc.OperationalError:
                db_error(ctx)
        channelTypes = ""
        if len(db.query(Channel).filter_by(guild_id=ctx.guild.id, channel_id=ctx.channel.id).all()) <= 1:
            channelTypes = db.query(Channel).filter_by(guild_id=ctx.guild.id, channel_id=ctx.channel.id).first().channel_type
        else:
            for type in db.query(Channel).filter_by(guild_id=ctx.guild.id, channel_id=ctx.channel.id).all():
                channelTypes += f"{type.channel_type}, "
            
        embed = discord.Embed(
            title="Channel Info!",
            description=f"""
            **Channel ID:** {ctx.channel.id}
            **Guild ID:** {ctx.guild.id}
            **Channel Type:** {channelTypes}
            """,
            color=discord.Color.green()
        )
        await ctx.respond(embed=embed)
        db.commit()
    

def setup(bot):
    bot.add_cog(Features(bot))