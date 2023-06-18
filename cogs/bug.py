import discord
from discord import Option
from discord.ext import commands
import sqlalchemy
"""Modular imports"""
from init import db, db_error, bot
from models import BugReport

bug_command_group = bot.create_group("bug", "Report and resolve bugs.")

class Bug(discord.Cog):
    def __init__(self, bot):
        super().__init__()
    
    @bug_command_group.command()
    @commands.has_permissions(administrator=True)
    async def list_bug(ctx: discord.ApplicationContext,
                   page: Option(int, description="The page you want to view.", required=True)):
        bugs = db.query(BugReport).all()
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

    @bug_command_group.command()
    @commands.has_permissions(administrator=True)
    async def resolve_bug(ctx: discord.ApplicationContext,
                      bug: Option(int, description="The bug you want to resolve.", required=True)):
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
            
    @bug_command_group.command()
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
            await ctx.respond(embed=missingValueEmbed)
        else:
            inspectEmbed = discord.Embed(
                title="Bug {bug}",
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

    @bug_command_group.command(name="report", description="Block a bug report from being seen by the bot admins.", guild_ids=[977513866097479760])
    async def report_bug(ctx: discord.ApplicationContext,
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

def setup(bot):
    bot.add_cog(Bug(bot))