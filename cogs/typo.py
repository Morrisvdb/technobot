import discord
from discord import guild_only, Option
from discord.ext import commands
import sqlalchemy
import re
"""Modular imports"""
from init import db, db_error, bot
from models import Channel, UserTypo

typo_command_group = bot.create_group("typo", "Report and resolve typos.")

class Typo(discord.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @typo_command_group.command(name="test", description="Block a typo from being reported.")
    @guild_only()
    async def test(ctx: discord.ApplicationContext):
        print(db.query(UserTypo).filter_by(guild_id=ctx.guild.id).first())

    @typo_command_group.command(name="add", description="Add a typo to the typo channel.")
    @guild_only()
    async def add(ctx: discord.ApplicationContext,
                  link: Option(description="The message that contains the typo.", required=True)
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
                typo = db.query(UserTypo).filter_by(guild_id=ctx.guild.id, message_url=link).first()
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
                        newTypo = UserTypo(message_url=link, channel_id=channel_id, guild_id=ctx.guild.id, reporter_id=ctx.author.id, user_id=user_id.author.id)
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
                    except sqlalchemy.exc.OperationalError:
                        db_error(ctx)
            else:
                embed = discord.Embed(
                    title="Invalid link!",
                    description="The message link you provided is invalid. Please provide a valid link.",
                    colour=discord.Color.orange()
                )
                await ctx.respond(embed=embed)
    
    @typo_command_group.command(name="remove", description="Remove a typo from the typo channel.")
    @guild_only()
    @commands.has_permissions(manage_messages=True)
    async def remove(ctx: discord.ApplicationContext,
                        link: Option(str, description="The message that contains the typo.", required=True),
                        block: Option(str, description="Whether or not to block this typo form being registered again.", required=False, choices=["yes", "no"])):
        """
        Remove a typo from the typo channel.
        Uses the message link to find the typo.
        Uses the "typo" subcommand class.
        """
        typoChannel = db.query(Channel).filter_by(
            guild_id=ctx.guild.id, channel_type="typo").first()
        if typoChannel is None:
            doesNotExistEmbed = discord.Embed(
                title="Command is disabled in this server!",
                description="""This command has been disabled in this server because there is no channel marked as a typo channel. \n Consult an admin if you think this is a mistake.""",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=doesNotExistEmbed)
        else:
            typo = db.query(Typo).filter_by(message_url=link).first()
            if typo is None:
                doesNotExistEmbed = discord.Embed(
                    title="Typo not found!",
                    description="""The typo you are trying to remove was not registered in the database.""",
                    color=discord.Color.orange()
                )
                await ctx.respond(embed=doesNotExistEmbed)
            else:
                if block == "yes":
                    typo.blocked = True
                    db.add(typo)
                else:
                    db.delete(typo)
                db.commit()
                typoPublicMessage = await bot.get_channel(typoChannel.channel_id).fetch_message(typo.public_msg_id)
                deletedEmbed = discord.Embed(
                    title="Typo removed!",
                    description="""This typo has been removed by and admin.""",
                    color=discord.Color.orange()
                )
                await typoPublicMessage.edit(embed=deletedEmbed)
                removedEmbed = discord.Embed(
                    title="Typo removed!",
                    description="""The typo has been removed from the typo channel.""",
                    color=discord.Color.green()
                )
                await ctx.respond(embed=removedEmbed)


def setup(bot):
    bot.add_cog(Typo(bot))