import discord
from discord.ext import commands
import sqlalchemy
from discord import guild_only, Option
from init import bot, channelTypes, db, db_error
from models import Channel

<<<<<<< Updated upstream
=======
"""Import other functions"""
from init import db, db_error, bot
from models import Channel, Typo, User, EWar, BugReport
import re
import datetime
import asyncio
from bot import bug_command_group, typo_command_group
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
            try:
                channel = db.query(Channel).filter_by(guild_id=ctx.guild.id, channel_id=ctx.channel.id, channel_type=None).first()
                """Checks if there is already an empty column for this channel."""
                if channel is not None:
                    channel.channel_type = feature
=======
            embed = discord.Embed(
                title="Thread created!",
                description=f"""Your thread has been created.
                You can now sing {name} for {duration} minutes.""",
                color=discord.Color.green()
            )
            message = await ctx.send(embed=embed)
            await message.create_thread(name=name, auto_archive_duration=int(duration))

    @commands.typo_command_group.command(name="add", description="Add a typo to the typo channel.")
    @guild_only()
    async def add(self, ctx: discord.ApplicationContext,
                  link: Option(input_type=str, description="The message that contains the typo.", required=True)
                ):
        typoChannel = db.query(Channel).filter_by(guild_id=ctx.guild.id, channel_type="typo").first()
        if typoChannel is None:
            embed = discord.Embed(
                title="Command is disabled!",
                description="""This command has been disabled in this server.
                This is because there is no channel marked as a typo channel.""",
                color=discord.Color.orange())
            await ctx.respond(embed=embed)
        else:
            validLink = re.search("^https://discord.com/channels/([0-9])+/([0-9])+/([0-9])+", link)
            if validLink:
                typo = db.query(Typo).filter_by(message_url=link).first()
                if typo is not None:
                    if typo.blocked:
                        isBlockedEmbed = discord.Embed(
                            title="Typo blocked!",
                            description="This typo has been blocked by an admin.",
                            color=discord.Color.orange()
                        )
                        await ctx.respond(embed=isBlockedEmbed)
                    else:
                        alreadyReportedEmbed = discord.Embed(
                            title="Typo already reported!",
                            description=f"This typo has already been reported by another user. \n User: {bot.get_user(typo.reporter_id)}",
                            color=discord.Color.orange()
                        )
                        await ctx.respond(embed=alreadyReportedEmbed)
>>>>>>> Stashed changes
                else:
                    newChannel = Channel(guild_id=ctx.guild.id, channel_id=ctx.channel.id, channel_type=feature)
                    db.add(newChannel)

                embed = discord.Embed(
                    title="Feature added!",
                    description=f"""The feature {feature} has been added to this channel.""",
                    color=discord.Color.green()
                )
                await ctx.respond(embed=embed)
<<<<<<< Updated upstream
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
    
=======

    # @discord.slash_command(name="typo", description="Tell the bot when someone made a typo and store the message in the typo's channel.")
    # @guild_only()
    # async def typo(self, ctx: discord.ApplicationContext,
    #                link: Option(input_type=str, description="The message that contains the typo.", required=True)
    #                ):
        # typoChannel = db.query(Channel).filter_by(guild_id=ctx.guild.id, channel_type="typo").first()
        # if typoChannel is None:
        #     embed = discord.Embed(
        #         title="Command is disabled!",
        #         description="""This command has been disabled in this server.
        #         This is because there is no channel marked as a typo channel.""",
        #         color=discord.Color.orange())
        #     await ctx.respond(embed=embed)
        # else:
        #     validLink = re.search("^https://discord.com/channels/([0-9])+/([0-9])+/([0-9])+", link)
        #     if validLink:
        #         typo = db.query(Typo).filter_by(message_url=link).first()
        #         if typo is not None:
        #             if typo.blocked:
        #                 isBlockedEmbed = discord.Embed(
        #                     title="Typo blocked!",
        #                     description="This typo has been blocked by an admin.",
        #                     color=discord.Color.orange()
        #                 )
        #                 await ctx.respond(embed=isBlockedEmbed)
        #             else:
        #                 alreadyReportedEmbed = discord.Embed(
        #                     title="Typo already reported!",
        #                     description=f"This typo has already been reported by another user. \n User: {bot.get_user(typo.reporter_id)}",
        #                     color=discord.Color.orange()
        #                 )
        #                 await ctx.respond(embed=alreadyReportedEmbed)
        #         else:
        #             try:
        #                 channel_id = int(link.split("/")[5])
        #                 message_id = int(link.split("/")[6])
        #                 message = await bot.get_channel(channel_id).fetch_message(message_id)
        #                 user_id= await bot.get_channel(channel_id).fetch_message(message_id)
        #                 newTypo = Typo(message_url=link, channel_id=channel_id, guild_id=ctx.guild.id, reporter_id=ctx.author.id, user_id=user_id.author.id)
        #                 db.add(newTypo)
        #                 reportedEmbed = discord.Embed(
        #                     title=f"Typo By {message.author.display_name}!",
        #                     description=f"""
        #                     {message.author.mention}
        #                     {message.content}
        #                     """,
        #                     color=discord.Color.blue()
        #                     )
        #                 typoChannel = db.query(Channel).filter_by(guild_id=ctx.guild.id, channel_type="typo").first()
        #                 sendMessage = await bot.get_channel(typoChannel.channel_id).send(embed=reportedEmbed)
        #                 newTypo.public_msg_id = sendMessage.id
        #                 db.add(newTypo)

        #                 isRecordedEmbed = discord.Embed(
        #                     title="Typo Registered!",
        #                     description="Your typo has been registered.",
        #                     color=discord.Color.green()
        #                 )
        #                 await ctx.respond(embed=isRecordedEmbed)
        #                 db.commit()
        #             except sqlalchemy.exc.OperationalError:
        #                 db_error(ctx)
        #     else:
        #         embed = discord.Embed(
        #             title="Invalid link!",
        #             description="The message link you provided is invalid. Please provide a valid link.",
        #             colour=discord.Color.orange()
        #         )
        #         await ctx.respond(embed=embed)
    
    @bug_command_group.command(name="report", description="Block a bug report from being seen by the bot admins.")
    async def report(self, ctx: discord.ApplicationContext,
                    feature: Option(input_type=str, description="The feature that has the bug.", required=True),
                    description: Option(input_type=str, description="The description of the bug.", required=True),
                    how: Option(input_type=str, description="How to reproduce the bug.", required=True),
                    extra: Option(input_type=str, description="Extra information about the bug.", required=False)
                    ):
        """Report a bug to the bot developers."""
        newBugReport = BugReport(reporter_id=ctx.author.id, feature=feature, description=description, how=how, extra=extra)
        try:
            db.add(newBugReport)
            db.commit()
            reportedEmbed = discord.Embed(
                title="Bug reported!",
                description="Your bug has been reported to the bot developers. \n Thank you for your contribution!",
                color=discord.Color.green()
            )
            await ctx.respond(embed=reportedEmbed)
        except sqlalchemy.exc.OperationalError:
            db.rollback()
            await db_error(ctx)
    
    
    # @commands.slash_command(name="bugreport", description="Report a bug to the bot developers.")
    # async def bugreport(self, ctx: discord.ApplicationContext,
    #                     feature: Option(input_type=str, description="The feature that has the bug.", required=True),
    #                     description: Option(input_type=str, description="The description of the bug.", required=True),
    #                     how: Option(input_type=str, description="How to reproduce the bug.", required=True),
    #                     extra: Option(input_type=str, description="Extra information about the bug.", required=False)
    #                     ):
    #     """Report a bug to the bot developers."""
    #     newBugReport = BugReport(reporter_id=ctx.author.id, feature=feature, description=description, how=how, extra=extra)
    #     try:
    #         db.add(newBugReport)
    #         db.commit()
    #         reportedEmbed = discord.Embed(
    #             title="Bug reported!",
    #             description="Your bug has been reported to the bot developers. \n Thank you for your contribution!",
    #             color=discord.Color.green()
    #         )
    #         await ctx.respond(embed=reportedEmbed)
    #     except sqlalchemy.exc.OperationalError:
    #         db.rollback()
    #         await db_error(ctx)
>>>>>>> Stashed changes

def setup(bot):
    bot.add_cog(Features(bot))