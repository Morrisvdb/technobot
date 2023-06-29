import discord
from discord import guild_only, Option
from discord.ext import commands, tasks
import asyncio, datetime, sqlalchemy, time
"""Modular imports"""
from models import Channel, EWar, User, Guild, AcceptWarView, TruceView, EWarsHelpView, identifyUserInWar, areAtWar, getWarUser, createUser, createGuild
from init import db, bot, db_error, updateCycle

ewars_command_group = bot.create_group("ewars", "E-Wars commands.")

async def endWar(war):
    guild = db.query(Guild).filter_by(guild_id=war.guild_id).first()
    if war.last_message_id is None:
        war.winner_id = war.first_user_id
        war.loser_id = war.second_user_id
    createUser(war.winner_id)
    createUser(war.loser_id)
    if war.isDraw == True:
        user1 = db.query(User).filter_by(user_id=war.first_user_id).first()
        user2 = db.query(User).filter_by(user_id=war.second_user_id).first()

        
        user1.e_exp += guild.ereward_draw
        user2.e_exp += guild.ereward_draw
        db.add(user1, user2)
        noMessageEmbed = discord.Embed(
            title="War ended!",
            description=f"""The war between {bot.get_user(war.first_user_id).mention} and {bot.get_user(war.second_user_id).mention} has ended in a draw!""",
            color=discord.Color.nitro_pink()
        )
        channel = await bot.get_guild(war.guild_id).fetch_channel(war.thread_id)
        await channel.send(embed=noMessageEmbed)
    else:
        winner_id = war.winner_id
        loser_id = war.loser_id
        winner = db.query(User).filter_by(user_id=winner_id).first()
        loser = db.query(User).filter_by(user_id=loser_id).first()
        guild 
        if war.hasSurrendered:
            winner.e_exp += guild.ereward_win
            loser.e_exp += guild.ereward_loss
        else:
            winner.e_exp += guild.ereward_win
            loser.e_exp += guild.ereward_loss
            db.add(winner)
            db.add(loser)
    war.hasEnded = True
    war.ended_on = datetime.datetime.now()
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
    await thread.edit(locked=True)
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
    await thread.edit(locked=False)
    await thread.send("E!")
    
class EWars(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO: Add admin tools

    @ewars_command_group.command(name="declare", description="Declare war on a member.")
    @guild_only()
    async def declare_ewar(ctx: discord.ApplicationContext,
                            member: Option(discord.Member, description="The member you want to declare war on.", required=True)
                            ):
        guild = db.query(Guild).filter_by(guild_id=ctx.guild.id).first()
        runningWars_count = db.query(EWar).filter_by(guild_id=ctx.guild.id, hasEnded=False).count()

        if runningWars_count >= guild.max_ewars_server:
            maxEwarsEmbed = discord.Embed(
                title="Cannot declare!",
                description=f"""There are already {runningWars_count}/{guild.max_ewars_server} wars running in this server.""",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=maxEwarsEmbed)
            return

        runningWars = db.query(EWar).filter_by(guild_id=ctx.guild.id, hasEnded=False).all()
        userWarsCount = 0
        for war in runningWars:
            getWarUser(war_id=war.id, user_id=ctx.author.id)
            if getWarUser is not None:
                userWarsCount += 1
        if userWarsCount >= guild.max_ewars_user:
            maxUserWarsEmbed = discord.Embed(
                title="Cannot declare!",
                description=f"""You already have {userWarsCount}/{guild.max_ewars_user} wars running in this server.""",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=maxUserWarsEmbed)
            return
        
        if member == ctx.author:
            cannotDeclareEmbed = discord.Embed(
                title="Cannot declare!",
                description="You cannot declare war on yourself.",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=cannotDeclareEmbed)
        else:
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
                        # ewars_accept_duration = db.query(ConfigValue).filter_by(guild_id=ctx.guild.id, key="ewars_accept_duration").first()
                        # if ewars_accept_duration is None: ewars_accept_duration = 180
                        # else: ewars_accept_duration = int(ewars_accept_duration.value)
                        try:
                            acceptTimeFormatted = int(guild.ewars_accept_duration/60)
                        except:
                            acceptTimeFormatted = f"{guild.ewars_accept_duration//60}:{guild.ewars_accept_duration%60}"
                            if guild.ewars_accept_duration%60 < 10:
                                acceptTimeFormatted += "0"

                        declareEmbed = discord.Embed(
                            title="War Declared!",
                            description=f"""{ctx.author.mention} has declared war on {member.mention}.
                            They have {acceptTimeFormatted} minutes to accept this war.""",
                            color=discord.Color.nitro_pink()
                        )
                        
                        uiview = AcceptWarView(target=member)
                        uiview.timeout = guild.ewars_accept_duration
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
        guild = db.query(Guild).filter_by(guild_id=war.guild_id).first()
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
                try:
                    acceptTimeFormatted = int(guild.ewars_accept_duration/60)
                except:
                    acceptTimeFormatted = f"{guild.ewars_accept_duration//60}:{guild.ewars_accept_duration%60}"
                    if guild.ewars_accept_duration%60 < 10:
                        acceptTimeFormatted += "0"

                wantsTruceEmbed = discord.Embed(
                    title="Truce requested!",
                    description=f"""{ctx.author.mention} has requested a truce with {member.mention}.
                    They have 3 minutes to accept this truce.""",
                    color=discord.Color.green()
                )
                truceUI = TruceView(target=member)
                truceUI.timeout = guild.ewars_accept_duration
                await ctx.respond(f"{member.mention}" ,embed=wantsTruceEmbed, view=truceUI)


                await truceUI.wait()

                if truceUI.accepted:
                    war.isDraw = True
                    war.hasEnded = True
                    db.add(war)
                    db.commit()
                    
                    thread = await bot.fetch_channel(war.thread_id)
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
                        title="Truce declined!",
                        description=f"""{member.mention} has declined {ctx.author.mention}'s truce.
                        This war will continue to rage on.""",
                        color=discord.Color.nitro_pink()
                    )
                    await ctx.respond(embed=truceDeniedEmbed)
                    thread = await bot.fetch_channel(war.thread_id)
                    truceDeniedEmbedThread = discord.Embed(
                        title="Truce denied!",
                        description=f"""{member.mention} has denied {ctx.author.mention}'s truce.
                        This war will continue to rage on.""",
                        color=discord.Color.nitro_pink()
                    )
                    await thread.send(embed=truceDeniedEmbedThread)

    @ewars_command_group.command(name="help", description="Get the e-wars rules and settings, and get help if you need it.")
    @guild_only()
    async def help_ewar(ctx: discord.ApplicationContext):
        helpEmbed = discord.Embed(
            title="E-Wars help",
            description="""This is a simple help menu to help you understand and use E-Wars.
            Use the select item below to navigate the help menu.""",
            color=discord.Color.nitro_pink()
        )
        helpView = EWarsHelpView()
        await ctx.respond(embed=helpEmbed, view=helpView)

        # await helpView.wait()

        # if helpView.value == "rules":
        #     print("rules")
        # elif helpView.value == "idea":
        #     print("idea")
        # elif helpView.value == "help":
        #     print("help")
        # elif helpView.value == "config":
        #     print("config")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.lower() != "e":
            pass
        else:
            if message.author != bot.user:
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
                            ewars_interval = db.query(Guild).filter_by(guild_id=war.guild_id).first().ewars_interval # Time in seconds
                            if war.last_message_time + datetime.timedelta(seconds=ewars_interval) < datetime.datetime.now():
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
                                    description=f"""{bot.get_user(war.winner_id).mention} has won this E-War because {bot.get_user(war.loser_id).mention} held the last 'E' {time.strftime('%M:%S', time.gmtime(ewars_interval))} minutes.""",
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
                ewars_interval = db.query(Guild).filter_by(guild_id=war.guild_id).first().ewars_interval # Time in seconds
                if war.last_message_time + datetime.timedelta(seconds=ewars_interval) < datetime.datetime.now():
                    if war.last_message_id is None:
                        war.hasEnded = True
                        war.isDraw = True
                        db.add(war)
                        db.commit()
                        await endWar(war=war)
                    else:
                        war.hasEnded = True
                        channel = await bot.fetch_channel(war.thread_id)
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
                            description=f"""{bot.get_user(war.winner_id).mention} has won this E-War because {bot.get_user(war.loser_id).mention} held the last 'E' for {time.strftime('%M:%S', time.gmtime(ewars_interval))} minutes.""",
                            color=discord.Color.nitro_pink()
                        )
                        await thread.send(embed=endEmbedThread)
                else:
                    pass

    @commands.Cog.listener()
    async def on_ready(self):
        """Registers all guilds in the database and starts the checkAllWars loop."""
        guilds = bot.guilds
        for guild in guilds:
            createGuild(guild_id=guild.id)
        self.checkAllWars.start()


def setup(bot):
    bot.add_cog(EWars(bot))