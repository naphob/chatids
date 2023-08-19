import discord
from discord.ext import commands, bridge
from rich.console import Console

console = Console()

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(name='move_all', description='This command will move all users to another voice channel')
    async def move_all(self, ctx, vc: discord.VoiceChannel):
        channel = ctx.author.voice.channel
        for member in channel.members:
            await member.move_to(vc)
        await ctx.respond(f"Move all user to #<{vc}>")


def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Utils(bot)) # add the cog to the bot
