import discord
from discord import guild_only, Option
from discord.ext import commands, tasks
import asyncio
import datetime
import sqlalchemy
"""Modular imports"""
from models import Channel, EWar, User
from init import db, bot, eRewards, db_error, updateCycle
from functions import identifyUserInWar, areAtWar, getWarUser, createUser
from UIComponents import AcceptWarView, TruceView

ewars_command_group = bot.create_group("ewars", "E-Wars commands.")


async def endWar(war):
    if war.last_message_id is None:
        war.winner_id = war.first_user_id
        war.loser_id = war.second_user_id
    createUser(war.winner_id)
    createUser(war.loser_id)
    if war.isDraw == True:
        user1 = db.query(User).filter_by(user_id=war.first_user_id).first()
        user2 = db.query(User).filter_by(user_id=war.second_user_id).first()
        user1.e_exp += eRewards["draw"]
        user2.e_exp += eRewards["draw"]
        db.add(user1, user2)
    else:
        winner_id = war.winner_id
        loser_id = war.loser_id
        winner = db.query(User).filter_by(user_id=winner_id).first()
        loser = db.query(User).filter_by(user_id=loser_id).first()
        if war.hasSurrendered:
            winner.e_exp += eRewards["win"]
            loser.e_exp += eRewards["surrender"]
        else:
            winner.e_exp += eRewards["win"]
            loser.e_exp += eRewards["loss"]
        war.hasEnded = True
        war.ended_on = datetime.datetime.now()
        db.add(winner)
        db.add(loser)
        db.add(war)
    thread = await bot.get_guild(war.guild_id).fetch_channel(war.thread_id)
    
    await thread.archive(locked=True)
    db.commit()

async def createWar(ctx, first_user, second_user, guild):
    eWarChannel = db.query(Channel).filter_by(guild_id=guild.id, channel_type="e-wars").first()
    startedEmbed = discord.Embed(
        title="War started!",
        description=f"""{first_user.mention} and {second_user.mention} have started a war!""",
        color=discord.Color.nitro_pink()
    )
    channel = bot.get_channel(eWarChannel.channel_id)
    msg = await channel.send(f"{first_user.mention} vs {second_user.mention}", embed=startedEmbed)
    thread = await msg.create_thread(name=f"{first_user.display_name} vs {second_user.display_name}", auto_archive_duration=60)
    newWar = EWar(guild_id=guild.id, first_user_id=first_user.id, second_user_id=second_user.id, thread_id=thread.id)
    db.add(newWar)
    db.commit()
    await ctx.send(f"{first_user.mention} vs {second_user.mention} \n Check it out here: {thread.mention}")
    await thread.send("Ready?")
    await asyncio.sleep(3)
    await thread.send("3")
    await asyncio.sleep(1)
    await thread.send("2")
    await asyncio.sleep(1)
    await thread.send("1")
    await asyncio.sleep(1)
    await thread.send("E")


class EWars(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ewars_command_group.command(name="declare", description="Declare war on a member.")
    @guild_only()
    async def declare_ewar(ctx: discord.ApplicationContext,
                            member: Option(discord.Member, description="The member you want to declare war on.", required=True)
                            ):
        if member == ctx.author:
            cannotDeclareEmbed = discord.Embed(
                title="Cannot declare!",
                description="You cannot declare war on yourself.",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=cannotDeclareEmbed)
        else:
            # TODO: Cap Maximum Amount of running wars per guild
            eWarsChannel = db.query(Channel).filter_by(guild_id=ctx.guild.id, channel_type="e-wars").first()
            if eWarsChannel is None:
                commandDisabledEmbed = discord.Embed(
                    title="Command disabled!",
                    description="""This command has been disabled in this server.
                    This is because there is no channel marked as a E-Wars channel.""",
                    color=discord.Color.orange()
                )
                await ctx.respond(embed=commandDisabledEmbed)
            else:
                declaring = db.query(EWar).filter_by(first_user_id=member.id, second_user_id=ctx.author.id, hasEnded=False).first()
                if declaring is not None:
                    await createWar(ctx, ctx.author, member, ctx.guild)
                else:
                    war = db.query(EWar).filter_by(guild_id=ctx.guild.id, first_user_id=ctx.author.id, hasEnded=False).first()
                    if war is not None:
                        alreadyDeclaredEmbed = discord.Embed(
                            title="Already declared!",
                            description=f"""You have already declared war on {member.mention}.""",
                            color=discord.Color.orange()
                        )
                        await ctx.respond(embed=alreadyDeclaredEmbed)
                    else:
                        declareEmbed = discord.Embed(
                            title="War Declared!",
                            description=f"""{ctx.author.mention} has declared war on {member.mention}.
                            They have 3 minutes to accept this war.""",
                            color=discord.Color.nitro_pink()
                        )
                        uiview = AcceptWarView(target=member)
                        await ctx.respond(f"{member.mention}", embed=declareEmbed, view=uiview)

                        await uiview.wait()
                        if uiview.accepted is None:
                            timedOutEmbed = discord.Embed(
                                title="Timed out!",
                                description=f"""{member.mention} did not respond in time.""",
                                color=discord.Color.orange()
                            )
                            await ctx.edit(embed=timedOutEmbed)
                        elif not uiview.accepted:
                            declinedEmbed = discord.Embed(
                                title="War declined!",
                                description=f"""{member.mention} is not interested in going to war with you.""",
                                color=discord.Color.orange()
                            )
                            await ctx.edit(embed=declinedEmbed)
                        elif uiview.accepted:
                            try:
                                await createWar(ctx, ctx.author, member, ctx.guild)
                            except sqlalchemy.exc.OperationalError:
                                db_error(ctx)

    @ewars_command_group.command(name="surrender", description="Surrender a war you have declared.")
    @guild_only()
    async def surrender_ewar(ctx: discord.ApplicationContext,
                             member: Option(discord.Member, description="The member you want to surrender the war to.", required=True)
                             ):
        eWarsChannel = db.query(Channel).filter_by(guild_id=ctx.guild.id, channel_type="e-wars").first()
        if eWarsChannel is None:
            noAllowedEmbed = discord.Embed(
                title="Command disabled!",
                description="""This command has been disabled in this server.
                This is because there is no channel marked as a E-Wars channel.""",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=noAllowedEmbed)
        else:
            if not areAtWar(user1=ctx.author.id, user2=member.id, guild_id=ctx.guild.id):
                notAtWarEmbed = discord.Embed(
                    title="Not at war!",
                    description=f"""You are not at war with {member.mention}.""",
                    color=discord.Color.orange()
                )
                await ctx.respond(embed=notAtWarEmbed)
            else:
                war = identifyUserInWar(user1=ctx.author.id, user2=member.id, guild_id=ctx.guild.id)
                war.hasSurrendered = True
                war.loser_id = ctx.author.id
                war.winner_id = member.id
                db.add(war)
                db.commit()
                thread = await bot.get_guild(war.guild_id).fetch_channel(war.thread_id)
                if ctx.channel != thread:
                    surrenderedEmbedPublic = discord.Embed(
                        title="War surrendered!",
                        description=f"""{ctx.author.mention} has surrendered to {member.mention}.""",
                        color=discord.Color.green()
                    )
                    await ctx.respond(embed=surrenderedEmbedPublic)
                surrenderedEmbedThread = discord.Embed(
                    title="War surrendered!",
                    description=f"""{member.mention} has won this E-War because {ctx.author.mention} has surrendered to them.""",
                    color=discord.Color.nitro_pink()
                )
                await thread.send(embed=surrenderedEmbedThread)
                await endWar(war=war)

    
    @ewars_command_group.command(name="truce", description="Make peace with a user you are at war with.")
    @guild_only()
    async def truce_ewar(ctx: discord.ApplicationContext,
                         member: Option(discord.Member, description="The member you want to make peace with.", required=True)
                         ):
        eWarsChannel = db.query(Channel).filter_by(guild_id=ctx.guild.id, channel_type="e-wars").first()
        if eWarsChannel is None:
            notAllowedEmbed = discord.Embed(
                title="Command disabled!",
                description="""This command has been disabled in this server.
                This is because there is no channel marked as a E-Wars channel.""",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=notAllowedEmbed)
        else:
            war = identifyUserInWar(user1=ctx.author.id, user2=member.id, guild_id=ctx.guild.id)
            if war is None:
                notAtWarEmbed = discord.Embed(
                    title="Not at war!",
                    description=f"""You are not at war with {member.mention}.""",
                    color=discord.Color.orange()
                )
                await ctx.respond(embed=notAtWarEmbed)
            else:
                db.add(war)
                wantsTruceEmbed = discord.Embed(
                    title="Truce requested!",
                    description=f"""{ctx.author.mention} has requested a truce with {member.mention}.
                    They have 3 minutes to accept this truce.""",
                    color=discord.Color.green()
                )
                truceUI = TruceView(target=member)
                await ctx.respond(f"{member.mention}" ,embed=wantsTruceEmbed, view=truceUI)


                await truceUI.wait()

                if truceUI.accepted:
                    war.isDraw = True
                    war.hasEnded = True
                    db.add(war)
                    db.commit()
                    
                    thread = bot.get_guild(war.guild_id).get_channel(war.thread_id)
                    if ctx.channel != thread:
                        truceEmbedPublic = discord.Embed(
                            title="Truce accepted!",
                            description=f"""{ctx.author.mention} and {member.mention} have made peace.""",
                            color=discord.Color.green()
                        )
                        await ctx.respond(embed=truceEmbedPublic)
                    truceEmbedThread = discord.Embed(
                        title="Truce accepted!",
                        description=f"""{ctx.author.mention} and {member.mention} have made peace.""",
                        color=discord.Color.green()
                    )
                    await thread.send(embed=truceEmbedThread)
                    await endWar(war=war)
                elif not truceUI.accepted:
                    db.add(war)
                    db.commit()
                    truceDeniedEmbed = discord.Embed(
                        title="Truce denied!",
                        description=f"""{member.mention} has denied {ctx.author.mention}'s truce.
                        This war will continue to rage on.""",
                        color=discord.Color.nitro_pink()
                    )
                    await ctx.respond(embed=truceDeniedEmbed)
                    thread = ctx.guild.get_thread(war.thread_id)
                    truceDeniedEmbedThread = discord.Embed(
                        title="Truce denied!",
                        description=f"""{member.mention} has denied {ctx.author.mention}'s truce.
                        This war will continue to rage on.""",
                        color=discord.Color.nitro_pink()
                    )
                    await thread.send(embed=truceDeniedEmbedThread)


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.lower() != "e":
            pass
        else:
            if message.author == bot.user:
                war = db.query(EWar).filter_by(thread_id=message.channel.id, hasEnded=False).first()
                if war is None:
                    pass
                elif war is not None:
                    if war.last_message_id is None:
                        war.last_message_id = message.id
                        war.last_message_time = datetime.datetime.now()
                        db.add(war)
                        db.commit()
                    else:
                        if getWarUser(war_id=war.id, user_id=message.author.id) is None:
                            notYetSupportedEmbed = discord.Embed(
                                title="Not yet supported!",
                                description="""This feature is not yet supported.
                                We do not yet support third parties in E-Wars.""",
                                color=discord.Color.orange()
                            )
                            await message.reply(embed=notYetSupportedEmbed)
                        else:
                            if war.last_message_time + datetime.timedelta(minutes=15) < datetime.datetime.now():
                                war.hasEnded = True
                                war.winner_id = await bot.get_channel(war.thread_id).fetch_message(war.last_message_id).author.id
                                if getWarUser(war_id=war.id, user_id=war.winner_id) == 1:
                                    war.loser_id = war.second_user_id
                                elif getWarUser(war_id=war.id, user_id=war.winner_id) == 2:
                                    war.loser_id = war.first_user_id
                                db.add(war)
                                db.commit()
                                await endWar(war=war)
                                thread = await bot.get_guild(war.guild_id).fetch_channel(war.thread_id)
                                endEmbedThread = discord.Embed(
                                    title="War ended!",
                                    description=f"""{bot.get_user(war.winner_id).mention} has won this E-War because {bot.get_user(war.loser_id).mention} held the last 'E' for 15 minutes.""",
                                    color=discord.Color.nitro_pink()
                                )
                                await thread.send(embed=endEmbedThread)
                            else:
                                war.last_message_id = message.id
                                war.last_message_time = datetime.datetime.now()
                                db.add(war)
                                db.commit()

    @tasks.loop(seconds=3)
    async def checkAllWars(self):
        wars = db.query(EWar).filter_by(hasEnded=False).all()
        if wars is None:
            pass
        else:
            for war in wars:
                if war.last_message_time + datetime.timedelta(seconds=10) < datetime.datetime.now():
                    war.hasEnded = True
                    channel = bot.get_channel(war.thread_id)
                    message = await channel.fetch_message(war.last_message_id)
                    war.winner_id = message.author.id
                    if getWarUser(war_id=war.id, user_id=war.winner_id) == 1:
                        war.loser_id = war.second_user_id
                    else:
                        war.loser_id = war.first_user_id
                    db.add(war)
                    db.commit()
                    await endWar(war=war)
                    thread = await bot.get_guild(war.guild_id).fetch_channel(war.thread_id)
                    endEmbedThread = discord.Embed(
                        title="War ended!",
                        description=f"""{bot.get_user(war.winner_id).mention} has won this E-War because {bot.get_user(war.loser_id).mention} held the last 'E' for 15 minutes.""",
                        color=discord.Color.nitro_pink()
                    )
                    await thread.send(embed=endEmbedThread)
                else:
                    pass


    @commands.Cog.listener()
    async def on_ready(self):
        self.checkAllWars.start()

    # @commands.Cog.listener()
    # async def on_message(self, message):
        
    #     if message.content.lower() == 'e':
            
    #         channel = db.query(EWar).filter_by(thread_id=message.channel.id, hasEnded=False).first()
    #         if channel is None:
    #             pass
    #         else:
    #             war = db.query(EWar).filter_by(thread_id=message.channel.id).first()
    #             if war.last_message_id is None:
    #                 war.last_message_id = message.id
    #                 war.last_message_time = datetime.datetime.now()
    #                 db.add(war)
    #             else:
    #                 print("bleep")
    #                 if message.author.id == war.first_user_id or war.second_user_id:
    #                     if war.last_message_time + datetime.timedelta(minutes=15) < datetime.datetime.now():
    #                         if message.author.id == war.first_user_id:
    #                             war.winner_id = war.second_user_id
    #                             loser = bot.get_user(war.first_user_id)
    #                             db.add(war)
    #                         else:
    #                             war.winner_id = war.first_user_id
    #                             loser = bot.get_user(war.second_user_id)
    #                             db.add(war)
                                
    #                         war.hasEnded = True
    #                         winnerObj = db.query(User).filter_by(user_id=war.winner_id).first()
    #                         loserObj = db.query(User).filter_by(user_id=war.loser_id).first()
    #                         winnerObj.e_exp += eRewards["win"]
    #                         loserObj.e_exp += eRewards["loss"]
    #                         db.add_all(winnerObj, loserObj)
    #                         endEmbed = discord.Embed(
    #                             title="E-War ended!",
    #                             description=f"""The E-War between {bot.get_user(war.first_user_id).mention} and {bot.get_user(war.second_user_id).mention} has ended.
    #                               The winner was {bot.get_user(war.winner_id)} has won.
    #                               This thread will be closed in 10 seconds.
    #                               """,
    #                             color=discord.Color.nitro_pink()
    #                         )
    #                         await bot.get_channel(war.thread_id).send(embed=endEmbed)
    #                         await asyncio.sleep(10)
    #                         await bot.get_channel(war.thread_id).delete()
    #                     else:
    #                         war.last_message_id = message.id
    #                         war.last_message_time = datetime.datetime.now()
    #                         db.add(war)
    #                 else:
    #                     notYetSupportedEmbed = discord.Embed(
    #                         title="Not yet supported!",
    #                         description="E-Wars do not yet support third parties.",
    #                         color=discord.Color.orange()
    #                     )
    #                     await message.channel.send(embed=notYetSupportedEmbed, empheral=True)
    #             db.commit()
                        
    # @tasks.loop(seconds=10)
    # async def check_e_wars(self):
    #     allWars = db.query(EWar).filter_by(hasStarted=True, hasEnded=False).all()
    #     for war in allWars:
    #         if war.hasStarted:   
    #             if war.last_message_time + datetime.timedelta(seconds=10) < datetime.datetime.now():
    #                 war.hasEnded = True
    #                 war.ended_on = datetime.datetime.now()
    #                 channel = bot.get_channel(war.thread_id)
    #                 winner_message = await channel.fetch_message(war.last_message_id)
    #                 war.winner_id = winner_message.author.id
    #                 if db.query(EWar).filter_by(first_user_id=war.winner_id).first():
    #                     loser = war.second_user_id
    #                 else:
    #                     loser = war.first_user_id
    #                 db.add(war)
    #                 winnerObj = db.query(User).filter_by(user_id=war.first_user_id).first()
    #                 if winnerObj is None:
    #                     newUser = User(user_id=war.first_user_id)
    #                     db.add(newUser)
    #                 loserObj = db.query(User).filter_by(user_id=loser).first()
    #                 if loserObj is None:
    #                     print("bleep")
    #                     newUser = User(user_id=loser)
    #                     db.add(newUser)
    #                 db.commit()

    #                 # winnerObj = db.query(User).filter_by(user_id=war.winner_id).first()
    #                 winnerObj.e_exp += eRewards["win"]
    #                 # loserObj = db.query(User).filter_by(user_id=loser).first()
    #                 loserObj.e_exp += eRewards["loss"]
    #                 db.add(winnerObj)
    #                 db.add(loserObj)
    #                 endEmbed = discord.Embed(
    #                     title="E-War ended!",
    #                     description=f"""The E-War between {bot.get_user(war.first_user_id).mention} and {bot.get_user(war.second_user_id).mention} has ended.
    #                     The winner was {bot.get_user(war.winner_id)}.
    #                     """,
    #                     color=discord.Color.nitro_pink()
    #                 )
    #                 await bot.get_channel(war.thread_id).send(embed=endEmbed)
    #                 await asyncio.sleep(10)
    #                 await bot.get_channel(war.thread_id).delete()
    #             else:
    #                 pass
    #         db.commit()

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     self.check_e_wars.start()

def setup(bot):
    bot.add_cog(EWars(bot))