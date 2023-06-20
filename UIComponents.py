import discord

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