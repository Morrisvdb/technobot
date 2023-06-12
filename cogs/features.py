import discord
from discord import Option, guild_only
from discord.ext import commands, tasks
import sqlalchemy.exc

"""Import other functions"""
from init import db, db_error, bot, eRewards
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
                    except sqlalchemy.exc.OperationalError:
                        db_error(ctx)
            else:
                embed = discord.Embed(
                    title="Invalid link!",
                    description="The message link you provided is invalid. Please provide a valid link.",
                    colour=discord.Color.orange()
                )
                await ctx.respond(embed=embed)

    @discord.slash_command(name="ewars")
    @guild_only()
    async def ewars(self, ctx: discord.ApplicationContext,
                    action: Option(input_type=str, description="The action you want to perform.", required=True, choices=["declare", "surrender", "peace"]),
                    member: Option(discord.Member, description="The member you want to declare war on.", required=True)
                    ):
        eWarsChannel = db.query(Channel).filter_by(guild_id=ctx.guild.id, channel_type="e-wars").first()
        if eWarsChannel is None:
            disabledEmbed = discord.Embed(
                title="Command disabled!",
                description="""This command has been disabled in this server.
                This is because there is no channel marked as a E-Wars channel.""",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=disabledEmbed)
        else:
            if action == "declare" or "surrender" or "peace":
                if action == "declare":
                    is_declaring = db.query(EWar).filter_by(guild_id=ctx.guild.id, first_user_id=member.id, second_user_id=ctx.author.id).first()
                    if is_declaring is not None and not is_declaring.hasStarted:
                        if is_declaring.declared_on + datetime.timedelta(minutes=15) < datetime.datetime.now():
                            expiredEmbed = discord.Embed(
                                title="E-war expired!",
                                description=f"The decleration of war by {ctx.author.mention} on {member.mention} has expired.",
                                color=discord.Color.orange()
                            )
                            db.delete(is_declaring)
                            await ctx.respond(embed=expiredEmbed)
                        else:
                            is_declaring.hasStarted = True
                            is_declaring.started_on = datetime.datetime.now()
                            acceptedEmbed = discord.Embed(
                                title="War accepted!",
                                description=f"Success, {ctx.author.mention} has accepted war with {member.mention}",
                                colour=discord.Color.green()
                            )
                            await ctx.respond(embed=acceptedEmbed)
                            startedEmbed = discord.Embed(
                                title="War accepted!",
                                description=f"Sharpen your E's, because {ctx.author.mention} has accepted an e-war with {member.mention}. \n Please use the included thread to fight.",
                                color=discord.Color.blue()
                            )
                            startedMessage = await ctx.send(embed=startedEmbed)
                            thread = await startedMessage.create_thread(name=f"{ctx.author.display_name} vs {member.display_name}", auto_archive_duration=1440)
                            is_declaring.thread_id = thread.id
                            db.add(is_declaring)
                            await thread.send("Ready?")
                            await asyncio.sleep(3)
                            await thread.send("3")
                            await asyncio.sleep(1)
                            await thread.send("2")
                            await asyncio.sleep(1)
                            await thread.send("1")
                            await asyncio.sleep(1)
                            await thread.send("E")

                    elif is_declaring is None:
                        newDeclaration = EWar(guild_id=ctx.guild.id, first_user_id=ctx.author.id, second_user_id=member.id, declared_on=datetime.datetime.now(), hasStarted=False)
                        db.add(newDeclaration)
                        declaredEmbed = discord.Embed(
                            title="War declared!",
                            description=f"{ctx.author.mention} has declared war on {member.mention}. \n {member.mention} has 15 minutes to accept the war.",
                            color=discord.Color.blue()
                        )
                        await ctx.respond(embed=declaredEmbed)
                elif action == "surrender":
                    war = db.query(EWar).filter_by(guild_id=ctx.guild.id, first_user_id=ctx.author.id, second_user_id=member.id).first()
                    if war is None:
                        noWarEmbed = discord.Embed(
                            title="You are not at war!",
                            description="You are not at war with this user right now. \n To declare war, use the /ewars declare command.",
                            color=discord.Color.orange()
                        )
                    else:
                        war.winner_id = member.id
                        war.surrenderer_id = ctx.author.id
                        war.hasEnded = True
                        war.ended_on = datetime.datetime.now()
                        db.add(war)
                        winnerObj = db.query(User).filter_by(user_id=war.winner_id).first()
                        winnerObj.e_exp += eRewards["win"]
                        surrendererObj = db.query(User).filter_by(user_id=war.surrenderer_id).first()
                        surrendererObj.e_exp += eRewards["loss"]
                        db.add_all(winnerObj, surrendererObj)
                        endEmbed = discord.Embed(
                            title="E-War ended!",
                            description=f"The E-War between {bot.get_user(war.first_user_id).mention} and {bot.get_user(war.second_user_id).mention} has ended because {ctx.author.mention} has surrendered. \n The winner was {bot.get_user(war.winner_id)}.",
                            color=discord.Color.nitro_pink()
                        )
                        await bot.get_channel(war.thread_id).send(embed=endEmbed)
                elif action == "peace":
                    war = db.query(EWar).filter_by(guild_id=ctx.guild.id, first_user_id=ctx.author.id, second_user_id=member.id).first()
                    if war is None:
                        noWarEmbed = discord.Embed(
                            title="You are not at war!",
                            description="You are not at war with this user right now. \n To declare war, use the /ewars declare command.",
                            color=discord.Color.orange()
                        )
                        await ctx.respond(embed=noWarEmbed)
                    else:
                        if war.wants_peace_id is None:
                            war.wants_peace_id = ctx.author.id
                            war.declared_peace_on = datetime.datetime.now()
                            wantsPeaceEmbed = discord.Embed(
                                title="Peace requested!",
                                description=f"{ctx.author.mention} has requested peace with {member.mention}. \n {member.mention} has 15 minutes to accept the peace.",
                                color=discord.Color.nitro_pink()
                            )
                            await ctx.respond(embed=wantsPeaceEmbed)
                        else:
                            war.isDraw = True
                            war.ended_on = datetime.datetime.now()
                            war.hasEnded = True
                            db.add(war)
                            firstUserObj = db.query(User).filter_by(user_id=war.first_user_id).first()
                            secondUserObj = db.query(User).filter_by(user_id=war.second_user_id).first()
                            firstUserObj.e_exp += eRewards["draw"]
                            secondUserObj.e_exp += eRewards["draw"]
                            db.add_all(firstUserObj, secondUserObj)
                            isPeaceEmbed = discord.Embed(
                                title="E-War ended!",
                                description=f"""
                                The E-War betweet {bot.get_user(war.first_user_id).mention} and {bot.get_user(war.second_user_id).mention} has ended peacefully.
                                May this truce last forever.
                                """,
                                color=discord.Color.nitro_pink()
                            )

                db.commit()
                
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.lower() == 'e':
            channel = db.query(Channel).filter_by(channel_id=message.channel.id, channel_type="e-wars").first()
            if channel is None:
                pass
            else:
                war = db.query(EWar).filter_by(thread_id=message.thread.id).first()
                if message.author.id == war.first_user_id or war.second_user_id:
                    if message.channel.fetch_message(war.last_message_id).created_at + datetime.timedelta(minutes=15) < datetime.datetime.now():
                        if message.author.id == war.first_user_id:
                            war.winner_id = war.second_user_id
                            loser = bot.get_user(war.first_user_id)
                            db.add(war)
                        else:
                            war.winner_id = war.first_user_id
                            loser = bot.get_user(war.second_user_id)
                            db.add(war)
                            
                        war.hasEnded = True
                        winnerObj = db.query(User).filter_by(user_id=war.winner_id).first()
                        loserObj = db.query(User).filter_by(user_id=war.loser_id).first()
                        winnerObj.e_exp += eRewards["win"]
                        loserObj.e_exp += eRewards["loss"]
                        endEmbed = discord.Embed(
                            title="E-War ended!",
                            description=f"The E-War between {bot.get_user(war.first_user_id).mention} and {bot.get_user(war.second_user_id).mention} has ended. \n The winner was {bot.get_user(war.winner_id)} has won.",
                            color=discord.Color.nitro_pink()
                        )
                        await bot.get_channel(war.thread_id).send(embed=endEmbed)
                    else:
                        war.last_message_id = message.id
                else:
                    notYetSupportedEmbed = discord.Embed(
                        title="Not yet supported!",
                        description="E-Wars do not yet support third parties.",
                        color=discord.Color.orange()
                    )
                    await message.channel.send(embed=notYetSupportedEmbed, empheral=True)
                    

    @tasks.loop(minutes=5)
    async def check_e_wars(self):
        allWars = db.query(EWar).filter_by(hasStarted=True).all()
        for war in allWars:
            if war.last_message_id + datetime.timedelta(minutes=15) < datetime.datetime.now():
                war.hasEnded = True
                war.ended_on = datetime.datetime.now()
                war.winner_id = bot.get_channel(war.thread_id).fetch_message(war.last_message_id).author
                if db.query(EWar).filter_by(first_user_id=war.winner_id).first():
                    loser = war.second_user_id
                else:
                    loser = war.first_user_id
                db.add(war)
                winnerObj = db.query(User).filter_by(user_id=war.winner_id).first()
                winnerObj.e_exp += eRewards["win"]
                loserObj = db.query(User).filter_by(user_id=loser).first()
                loserObj.e_exp += eRewards["loss"]
                db.add_all(winnerObj, loserObj)
                endEmbed = discord.Embed(
                    title="E-War ended!",
                    description=f"The E-War between {bot.get_user(war.first_user_id).mention} and {bot.get_user(war.second_user_id).mention} has ended. \n The winner was {bot.get_channel(war.thread_id).fetch_message(war.last_message_id).author.mention}.",
                    color=discord.Color.nitro_pink()
                )
                await bot.get_channel(war.thread_id).send(embed=endEmbed)
            else:
                pass
        db.commit()

def setup(bot):
    bot.add_cog(Features(bot))