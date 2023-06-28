import discord
from init import db
from models import Guild

class AcceptWarView(discord.ui.View):
    def __init__(self, target):
        self.target = target
        super().__init__()

    accepted = None
    interaction = None
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.target.id:
            self.interaction = interaction
            self.accepted = True
            await interaction.response.send_message("You have accepted the war.", ephemeral=True)
            self.disable_all_items()
            self.stop()
        else:
            await interaction.response.send_message("You cannot accept this war.", ephemeral=True)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.target.id:
            self.interaction = interaction
            self.accepted = False
            await interaction.response.send_message("You have declined the war.", ephemeral=True)
            self.disable_all_items()
            self.stop()
            
        else:
            await interaction.response.send_message("You cannot decline this war.", ephemeral=True)

class TruceView(discord.ui.View):
    def __init__(self, target):
        self.target = target
        super().__init__()


    accepted = None
    interaction = None
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.target.id:
            self.interaction = interaction
            self.accepted = True
            await interaction.response.send_message("You have accepted the truce.", ephemeral=True)
            self.stop()
        else:
            await interaction.response.send_message("You cannot accept this truce.", ephemeral=True)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.target.id:
            self.interaction = interaction
            self.accepted = False
            await interaction.response.send_message("You have declined the truce.", ephemeral=True)
            self.stop()
        else:
            await interaction.response.send_message("You cannot decline this truce.", ephemeral=True)

class EWarsHelpView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.string_select(placeholder="Select a page", options=[
        discord.SelectOption(label="Information", description="Information about the ewars system and how it works.", emoji="📚"),
        discord.SelectOption(label="Commands", description="Commands for the ewars system.", emoji="📝"),
        discord.SelectOption(label="Config", description="The current config of the ewars system.", emoji="⚙️")],
        )
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        if select.values[0] == "Information":
            newEmbed = discord.Embed(title="Information", description="""
            E-Wars is a game made up by this discord server based on the iconic **E** spam in Technoblade's chat.
            This started off as a simple E-Chain where people would just post an E every once in a while, but it has evolved into a full war system.
            The E-Wars system is a way for people to fight each other in a fun way, and it is completely optional.

            The general idea is that 2 (Sometimes even more) people would try to keep the last **E** in the E-Chain channel for as long as possible.
            Then who held the E for a certain amount of time would win the war, and be awarded E-Experience.

            The game was already played before this bot came allong, but it is made to make it a lot easier to play.
            """, color=discord.Color.nitro_pink())
        elif select.values[0] == "Commands":
            newEmbed = discord.Embed(title="Commands", description="""
            **/ewars help** - Shows the help menu.
            **/ewars declare [Member]** - Starts a war with the mentioned user.
            **/ewars truce [Member]** - Requests a truce with the mentioned user.
            **/ewars surrender** - Surrenders in the current war. (This awards the other user a win.)
            """,
            color=discord.Color.nitro_pink())
        elif select.values[0] == "Rules":
            ...
        elif select.values[0] == "Config":
            guild = db.query(Guild).filter_by(guild_id=interaction.guild.id).first()
            newEmbed = discord.Embed(title="Config", description=f"""
            **Hold Duration** - The amount of time you have to hold the E to win the war. - {guild.ewars_interval} seconds.
            **Cooldown** - The amount of time you have to wait before you can declare another war. - {guild.ewars_cooldown} seconds.
            **Truce/War accept Duration** - The amount of time you have to accept a truce or a war. - {guild.ewars_accept_duration} seconds.
            **Max EWars per User** - The maximum amount of wars a user can have at the same time. - {guild.max_ewars_user}.
            **Max EWars per Guild** - The maximum amount of wars the guild can have at the same time. - {guild.max_ewars_server}.

            **Rewards**
            **Win** - The amount of E-Experience you get for winning a war. - {guild.ereward_win}.
            **Loss** - The amount of E-Experience you get for losing a war. - {guild.ereward_loss}.
            **Truce/Tie** - The amount of E-Experience you get for accepting a truce. - {guild.ereward_draw}.
            """,
            color=discord.Color.nitro_pink()
            )
        else:
            self.stop()
        await interaction.response.edit_message(embed=newEmbed, view=self)
        
class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
    
    @discord.ui.string_select(placeholder="Select a page", options=[
        discord.SelectOption(label="Information", description="Information about the bot and how it works.", emoji="📚"),
        discord.SelectOption(label="Commands", description="Commands for the bot.", emoji="📝")]
    )
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        if select.values[0] == "Information":
            informationEmbed = discord.Embed(title="Information", description="""
            This is a custom discord bot designed by lagg_mine for the TechnoCult server.
            It is open to suggestions, and any porblems that are found can be reported using the **/bug** command.
            """, color=discord.Color.blue())
            await interaction.response.edit_message(embed=informationEmbed, view=self)
        elif select.values[0] == "Commands":
            admin_commands = ""
            commandsEmbed = discord.Embed(title="Commands", color=discord.Color.blue())
            if interaction.user.guild_permissions.administrator:
                commandsEmbed.add_field(name="Config", value="""
                **/config set [Setting] [Value]** - Sets the value of the specified setting.
                **/config get [Setting]** - Gets the value of the specified setting.
                """, inline=False)
                commandsEmbed.add_field(name="Channel-Features", value="""
                **/feature add [Feature]** - Adds the specified feature to the current channel.
                **/feature remove [Feature]** - Removes the specified feature from the current channel.
                **/feature info** - Gives info about the current channel.
                """, inline=False)
                commandsEmbed.add_field(name="Bugreports", value="""
                **/bug list** - Lists all the bugreports.
                **/bug inspect [ID]** - Gives info about the specified bugreport.
                **/bug resolve [ID]** - Resolves the specified bugreport.
                """, inline=False)
                commandsEmbed.add_field(name="Misc", value="""
                **/say [Message]** - Makes the bot say the given message.
                **/typo remove [Link] <Block>** - Removes the specified typo.
                """, inline=False)
            commandsEmbed.add_field(name="Misc", value="""
            **/help** - Shows this help menu.
            """
            , inline=False)
            commandsEmbed.add_field(name="E-Wars", value="""
            **/ewars help** - Shows the ewars help menu.
            **/ewars declare [Member]** - Starts a war with the mentioned user.
            **/ewars truce [Member]** - Requests a truce with the mentioned user.
            **/ewars surrender [Member]** - Surrenders to the mentioned user. (This awards the other user a win.)
            """, inline=False)
            await interaction.response.edit_message(embed=commandsEmbed, view=self)