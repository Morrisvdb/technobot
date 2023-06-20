import os
import discord
"""Imports the client from init.py"""
from init import bot, db
from keys import TOKEN


features_command_group = discord.SlashCommandGroup("feature", "Add a feature to a channel unlocking the commands paired with that feature.")
bug_command_group = discord.SlashCommandGroup("bug", "Report and resolve bugs.", guild_ids=[977513866097479760])
typo_command_group = discord.SlashCommandGroup("typo", "Report a typo to the bot admins.", guild_ids=[977513866097479760])


for f in os.listdir("./cogs"):
    if f.endswith(".py"):
        bot.load_extension(f"cogs.{f[:-3]}")
        print(f"Loaded Cog: {f[:-3]}.py")

@bot.event
async def on_ready():
    """Prints a message when the bot is ready."""
    print("------")
    print("Bot is ready!")
    print("Logged in as:")
    print(f"{bot.user.name}#{bot.user.discriminator}")
    print(f"ID: {bot.user.id}")
    print("------")


@bot.event
async def on_application_command_error(ctx, exception):
    if isinstance(exception, discord.ext.commands.errors.MissingPermissions):
        await ctx.respond("You do not have the required permissions to run this command.", ephemeral=True)
    else:
        raise exception

bot.run(TOKEN)
