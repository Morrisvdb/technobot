import discord
from discord import Option, guild_only
from discord.ext import commands
import sqlalchemy.exc

"""Import other functions"""
from init import db, db_error, bot
from models import Channel, Typo, User, EWar
import re
import datetime
import asyncio

class Features(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="sing", description="Create a new thread to sing like you are back in the live chat.")
    @guild_only()
    async def sing(self, ctx: discord.ApplicationContext,
    
                    name: Option(description="The song you want to sing.", required=True),
                    duration: Option(input_type=str, description="The duration of the song in minutes. Choose any of: 60, 1440, 4320, 10080.", choices=["60" , "1440", "4320", "10080"], required=True)
                ):
        """Create a new thread to sing like you are back in the live chat."""
        if db.query(Channel).filter_by(guild_id=ctx.guild.id, channel_id=ctx.channel.id, channel_type="singing").first() is None:
            embed = discord.Embed(
                title="Command not allowed!",
                description="""This command is not allowed in this channel.
                Please use it in a channel that is marked as a singing channel.""",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="Thread created!",
                description=f"""Your thread has been created.
                You can now sing {name} for {duration} minutes.""",
                color=discord.Color.green()
            )
            message = await ctx.send(embed=embed)
            await message.create_thread(name=name, auto_archive_duration=int(duration))

    @discord.slash_command(name="typo", description="Tell the bot when someone made a typo and store the message in the typo's channel.")
    @guild_only()
    async def typo(self, ctx: discord.ApplicationContext,
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
                else:
                    try:
                        channel_id = int(link.split("/")[5])
                        message_id = int(link.split("/")[6])
                        message = await bot.get_channel(channel_id).fetch_message(message_id)
                        user_id= await bot.get_channel(channel_id).fetch_message(message_id)
                        newTypo = Typo(message_url=link, channel_id=channel_id, guild_id=ctx.guild.id, reporter_id=ctx.author.id, user_id=user_id.author.id)
                        db.add(newTypo)
                        reportedEmbed = discord.Embed(
                            title=f"Typo By {message.author.display_name}!",
                            description=f"""
                            {message.author.mention}
                            {message.content}
                            """,
                            color=discord.Color.blue()
                            )
                        typoChannel = db.query(Channel).filter_by(guild_id=ctx.guild.id, channel_type="typo").first()
                        sendMessage = await bot.get_channel(typoChannel.channel_id).send(embed=reportedEmbed)
                        newTypo.public_msg_id = sendMessage.id
                        db.add(newTypo)

                        isRecordedEmbed = discord.Embed(
                            title="Typo Registered!",
                            description="Your typo has been registered.",
                            color=discord.Color.green()
                        )
                        await ctx.respond(embed=isRecordedEmbed)
                        db.commit()
                        
                        
                        # print(channel_id)
                        # message = await bot.get_channel(channel_id).fetch_message(message_id)
                        # print(message.channel)
                        # newTypo = Typo(message_url=link, channel_id=ctx.channel.id, guild_id=ctx.guild.id, reporter_id=ctx.author.id)
                        # db.add(newTypo)
                        # db.commit()
                        # typo = db.query(Typo).filter_by(message_url=link).first()
                        # typoMessage = await bot.get_channel(typo.channel_id).fetch_message(int(message_id))

                        # reported = discord.Embed(
                        #     title=f"Funny Typo By {bot.get_user(user_id).display_name}!",
                        #     description=f"""
                        #     {bot.get_user(typo.user_id).mention}
                        #     {typoMessage.content}
                        #     """,
                        #     color=discord.Color.blue()
                        #     )
                        # sendMessage = await bot.get_channel(typoChannel.channel_id).send(f"{typo.message_url}", embed=reported)
                        # typo.public_msg_id = sendMessage.id
                        # db.add(typo)
                        
                        # messageSendEmbed = discord.Embed(
                        #     title="Typo Registered!",
                        #     description="Your typo has been registered.",
                        #     color=discord.Color.green()
                        # )
                        # await ctx.respond(embed=messageSendEmbed)
                        # db.commit()
                    except sqlalchemy.exc.OperationalError:
                        db_error(ctx)
            else:
                embed = discord.Embed(
                    title="Invalid link!",
                    description="The message link you provided is invalid. Please provide a valid link.",
                    colour=discord.Color.orange()
                )
                await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Features(bot))