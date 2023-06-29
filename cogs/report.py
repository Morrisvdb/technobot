import discord
from discord import Option
from discord.ext import commands
import sqlalchemy
"""Modular imports"""
from init import db, db_error, bot
from models import BugReport, Channel

user_report_command_group = bot.create_group("report", "Reports suggestions bug and other users.")
bug_command_group = bot.create_group("bug", "Report and resolve bugs.")

# TODO: Add suggestions and player-reports

class Report(discord.Cog):
    def __init__(self, bot):
        super().__init__()
    
    @bug_command_group.command(name="list", description="List all bugs")
    @commands.has_permissions(administrator=True)
    async def list_bug(ctx: discord.ApplicationContext,
                   page: Option(int, description="The page you want to view.", required=False, default=1)):
        bugs = db.query(BugReport).filter_by(isResolved=False).all()
        if bugs is None:
            noBugsEmbed = discord.Embed(
                title="No bugs reported!",
                description="There are no bugs reported. \n or all bugs have been resolved. \n Congratulations! Now get a cup of tea and take a break!",
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

    @bug_command_group.command(name="resolve", description="Resolve a bug.")
    @commands.has_permissions(administrator=True)
    async def resolve_bug(ctx: discord.ApplicationContext,
                      bug_id: Option(int, description="The bug you want to resolve.", required=True),
                      message: Option(str, description="The message you want to send to the reporter.", required=False, default="Your bug has been resolved!")):
        bug = db.query(BugReport).filter_by(id=bug_id, isResolved=False).first()
        if bug is None:
            doesNotExistEmbed = discord.Embed(
                title="Bug does not exist!",
                description=f"The bug with ID {bug_id} does not exist, or has already been resolved.",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=doesNotExistEmbed, ephemeral=True)
        else:
            bug.isResolved = True
            bug.resolvedMessage = message
            db.add(bug)
            db.commit()
            user = bot.get_user(bug.reporter_id)
            dm_channel = await bot.create_dm(user)
            await dm_channel.send(
f"""
**Dear {user.display_name},**
{message}
Sincerely,
**The TechnoBot dev team.**
""")
            deletedEmbed = discord.Embed(
                title="Bug resloved!",
                description=f"The bug with ID {bug_id} has been marked as resolved.",
                color=discord.Color.green()
            )
            await ctx.respond(embed=deletedEmbed)
            
    @bug_command_group.command(name="inspect", description="Inspect a bug.")
    @commands.has_permissions(administrator=True)
    async def inspect_bug(ctx: discord.ApplicationContext,
                        bug: Option(int, description="The bug you want to inspect.", required=True)):
        bug = db.query(BugReport).filter_by(id=bug).first()
        if bug is None:
            missingValueEmbed = discord.Embed(
                title="Missing value!",
                description="You need to provide a bug ID.",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=missingValueEmbed, ephemeral=True)
        else:
            inspectEmbed = discord.Embed(
                title=f"Bug {bug}",
                description=f"""
                **Reporter:** {bot.get_user(bug.reporter_id).display_name}#{bot.get_user(bug.reporter_id).discriminator}
                **Feature:** {bug.feature}
                **Description:** {bug.description}
                **How to reproduce:** {bug.how}
                **Extra:** {bug.extra}
                """,
                color=discord.Color.green()
            )
            await ctx.respond(embed=inspectEmbed)

    @bug_command_group.command(name="report", description="Report a bug to the bot developer(s).")
    async def report_bug(ctx: discord.ApplicationContext,
                    feature: Option(input_type=str, description="The feature that has the bug.", required=True),
                    description: Option(input_type=str, description="The description of the bug.", required=True),
                    how: Option(input_type=str, description="How to reproduce the bug.", required=True),
                    extra: Option(input_type=str, description="Extra information about the bug.", required=False)
                    ):
        """Report a bug to the bot developers."""
        newBugReport = BugReport(reporter_id=ctx.author.id, feature=feature, description=description, how=how, extra=extra)
        bugsChannel = db.query(Channel).filter_by(guild_id=ctx.guild.id, channel_type="bugs").first()
        try:
            db.add(newBugReport)
            db.commit()
            if bugsChannel is not None:
                adminEmbed = discord.Embed(
                    title="New bug report!",
                    description=f"""
                    **Reporter:** {ctx.author.display_name}
                    **Feature:** {feature}
                    **Description:** {description}
                    **How to reproduce:** {how}
                    **Extra:** {extra}

                    For more info run **/bug inspect {newBugReport.id}**
                    """,
                    color=discord.Color.blue()
                )
                await bot.get_channel(bugsChannel.channel_id).send(embed=adminEmbed)
            reportedEmbed = discord.Embed(
                title="Bug reported!",
                description="Your bug has been reported to the bot developers. \n Thank you for your contribution!",
                color=discord.Color.green()
            )
            await ctx.respond(embed=reportedEmbed)
        except sqlalchemy.exc.OperationalError:
            db.rollback()
            await db_error(ctx)

    @bug_command_group.command(name="my", description="View your own bug reports.")
    async def my_bug(ctx: discord.ApplicationContext,
                     page: Option(discord.SlashCommandOptionType.integer, description="The page number you wish to view. (Only when index is None)", required=False, default=1),
                     index: Option(discord.SlashCommandOptionType.integer, description="The bug index number of the bug you wish to view.", required=False),
                     solved: Option(discord.SlashCommandOptionType.boolean, description="Whether you want to view your solved bugs or not.", required=False, default=False)
                     ):
        if index is None:
            bugs = db.query(BugReport).filter_by(reporter_id=ctx.author.id, isResolved=solved).all()
            embed = discord.Embed(
                title=f"Page #{page} of your Reports:",
                description="",
                color=discord.Color.blue()
            )
            for bug in bugs[page*6-6:page*6]:
                embed.add_field(
                    name=f"Bug #{bug.id}",
                    value=f"""
                    **Feature:** {bug.feature}
                    **Description:** {bug.description}
                    **How to reproduce:** {bug.how}
                    **Extra:** {bug.extra}
                    """,
                    inline=True
                )
            await ctx.respond(embed=embed)
        else:
            bug = db.query(BugReport).filter_by(id=index, reporter_id=ctx.author.id).first()
            if bug is None:
                notYourBugEmbed = discord.Embed(
                    title="Not your bug!",
                    description="The bug with this ID does not belong to your account.",
                    color=discord.Color.orange()
                )
                await ctx.respond(embed=notYourBugEmbed, ephemeral=True)
                return
            if bug.isResolved:
                status="Resolved"
            else:
                status="Unresolved"
            inspectEmbed = discord.Embed(
                title=f"Bug #{bug.id}",
                description=f"""
                **Reporter:** {bot.get_user(bug.reporter_id).display_name}#{bot.get_user(bug.reporter_id).discriminator}
                **Feature:** {bug.feature}
                **Description:** {bug.description}
                **How to reproduce:** {bug.how}
                **Extra:** {bug.extra}
                **Status:** {status}
                """,
                color=discord.Color.green()
            )
            await ctx.respond(embed=inspectEmbed)

def setup(bot):
    bot.add_cog(Report(bot))