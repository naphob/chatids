import discord
from discord.ext import commands
from rich.console import Console

console = Console()

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name='move_all', description='This command will move all users to another voice channel')
    @commands.has_any_role(1008638970911002684, 1037741810749030511, 1123808015536111616)
    async def move_all(self, ctx, before: discord.VoiceChannel, after: discord.VoiceChannel):
        channel = before
        for member in channel.members:
            await member.move_to(after)
        await ctx.respond(f"Move all user to {after}")


def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Utils(bot)) # add the cog to the bot
