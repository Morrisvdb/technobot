import discord
from discord import Option, guild_only
from discord.ext import commands
import sqlalchemy.exc
"""Import other functions"""
from init import bot, db, db_error, channelTypes
from models import Channel, BugReport

class Administration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.slash_command(name="feature",
                           description="Add a feature to a channel unclocking the commands paired with that feature.")
    @guild_only()
    async def channel_feature(self, ctx: discord.ApplicationContext,
                    action: Option(input_type=str,
                                   description="The action you want to perform.",
                                   required=True,
                                   choices=["add", "remove", "info"]),
                    
                    feature: Option(input_type=str,
                                    description="The feature you want to add or remove.",
                                    choices=channelTypes,
                                    required=False)
                    ):

        """Adds a feature to a channel unclocking the commands paired with that feature."""

        if action == "add":
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

        elif action == "remove":
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
        elif action == "info":
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
        
    @discord.slash_command(name="bugs", description="Admin tool for bugreports.", guild_ids=[977513866097479760])
    async def bug(self, ctx: discord.ApplicationContext,
                  action: Option(str, description="The action you want to perform.", required=True, choices=["list", "reslove", "inspect"], default="list"),
                  page: Option(int, description="The page you want to view. Only for the ", required=False),
                  bug: Option(int, description="The bug you want to inspect.", required=False)):
        bugs = db.query(BugReport).all()
        if action == "list":
            if page is None:
                missingValueEmbed = discord.Embed(
                    title="Missing value!",
                    description="You need to provide a page number.",
                    color=discord.Color.orange()
                )
            else:
                if bugs is None:
                    noBugsEmbed = discord.Embed(
                        title="No bugs reported!",
                        description="There are no bugs reported.",
                        color=discord.Color.green()
                    )
                    await ctx.respond(embed=noBugsEmbed)
                else:
                    embed = discord.Embed(
                        title="Bug Reports",
                        description=f"""
                        **Page {page}**
                        """,
                        color=discord.Color.green()
                    )
                    for bug in bugs[page*6-6:page*6]:
                        reporterTrimmed = bot.get_user(bug.reporter_id).display_name[:50]
                        featureTrimmed = bug.feature[:50]
                        descriptionTrimmed = bug.description[:50]
                        howTrimmed = bug.how[:50]
                        extraTrimmed = bug.extra[:50]
                        embed.add_field(
                            name=f"Bug #{bug.id}",
                            value=f"""
                            **Reporter:** {reporterTrimmed}
                            **Feature:** {featureTrimmed}
                            **Description:** {descriptionTrimmed}
                            **How to reproduce:** {howTrimmed}
                            **Extra:** {extraTrimmed}
                            """,
                            inline=True
                        )
                    await ctx.respond(embed=embed)
                
        elif action == "delete":
            bug = db.query(BugReport).filter_by(id=bug).first()
            if bug is None:
                doesNotExistEmbed = discord.Embed(
                    title="Bug does not exist!",
                    description=f"The bug with ID {bug} does not exist.",
                    color=discord.Color.orange()
                )
            else:
                bug.isResolved = True
                db.add(bug)
                db.commit()
                deletedEmbed = discord.Embed(
                    title="Bug resloved!",
                    description=f"The bug with ID {bug} has been marked as resolved.",
                    color=discord.Color.green()
                )
                await ctx.respond(embed=deletedEmbed)
        elif action == "inspect":
            bug = db.query(BugReport).filter_by(id=bug).first()
            if bug is None:
                missingValueEmbed = discord.Embed(
                    title="Missing value!",
                    description="You need to provide a bug ID.",
                    color=discord.Color.orange()
                )
                await ctx.respond(embed=missingValueEmbed)
            else:
                inspectEmbed = discord.Embed(
                    title="Bug {bug}",
                    description=f"""
                    **Reporter:** {bot.get_user(bug.reporter_id).display_name}
                    **Feature:** {bug.feature}
                    **Description:** {bug.description}
                    **How to reproduce:** {bug.how}
                    **Extra:** {bug.extra}
                    """,
                    color=discord.Color.green()
                )
                await ctx.respond(embed=inspectEmbed)
def setup(bot):
    bot.add_cog(Administration(bot))
