import discord
from discord import guild_only, Option
from discord.ext import commands
from init import db
from models import Channel
from UIComponents import AcceptWarView

class Misc(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.slash_command(name="sing", description="Create a new thread to sing like you are back in the live chat.")
    @guild_only()
    async def sing(ctx: discord.ApplicationContext,
    
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

    @discord.slash_command(name="say", description="Make the bot say something.")
    @commands.has_permissions(manage_messages=True)
    # TODO: Add an option to disable this command.
    async def say(ctx: discord.ApplicationContext,
                  message: Option(input_type=str, description="The message you want the bot to say.", required=True)):
        await ctx.respond(message)
    
    @discord.slash_command(name="test", guild_ids=[977513866097479760])
    async def test(self, ctx: discord.ApplicationContext):
        uiview = AcceptWarView()
        await ctx.respond("Test", view=uiview)
        
        await uiview.wait()

        print(uiview.accepted)

def setup(bot):
    bot.add_cog(Misc(bot))