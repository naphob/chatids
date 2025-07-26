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
        await ctx.respond(f"Move all user to {after.mention}")
    
    @move_all.error
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.respond("คุณไม่สิทธิ์ใช้คำสั่งนี้!", ephemeral = True)
        else:
            raise error  # Here we raise other errors to ensure they aren't ignored

    @discord.slash_command(name='kick', description='Command to Kick user from voice channel')
    @commands.has_any_role(1008638970911002684, 1037741810749030511, 1123808015536111616)
    async def kick(self, ctx, member : discord.Member): # default reason is none so that it is optional in the slash command
        # side note for nextcord.Member, having it there makes it so that there's a drop down menu that functions the same way as if you were to @ someone in a message. This makes it easier to kick the right person        
        if member.voice.channel is not None:
            embed = discord.Embed(description=f'{member.display_name} has been kicked from voice channel') # setting up embed to send
            await ctx.respond(embed=embed, ephemeral = True) # sends the embed in chat letting people know the person has been kicked
            await member.move_to(None)

    @kick.error
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.respond("คุณไม่สิทธิ์ใช้คำสั่งนี้!", ephemeral = True)
        else:
            raise error  # Here we raise other errors to ensure they aren't ignored
        
    @discord.slash_command(name='nuke', description='Command to Kick all user from voice channel')
    @commands.has_any_role(1008638970911002684, 1037741810749030511, 1123808015536111616)
    async def nuke(self, ctx, before: discord.VoiceChannel): # default reason is none so that it is optional in the slash command
        # side note for nextcord.Member, having it there makes it so that there's a drop down menu that functions the same way as if you were to @ someone in a message. This makes it easier to kick the right person
        for member in before.members:
            await member.move_to(None)
        await ctx.respond(f"All users have been kicked from {before.mention}", ephemeral = True)

    @nuke.error
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.respond("คุณไม่สิทธิ์ใช้คำสั่งนี้!", ephemeral = True)
        else:
            raise error  # Here we raise other errors to ensure they aren't ignored

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Utils(bot)) # add the cog to the bot
