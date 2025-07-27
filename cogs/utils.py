import discord
from discord.ext import commands
from rich.console import Console
import asyncio

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
        await ctx.respond(f"Moved all users to {after.mention}", ephemeral = True)

    @discord.slash_command(name='kick', description='Command to Kick user from voice channel') 
    @commands.has_any_role(1008638970911002684, 1037741810749030511, 1123808015536111616)
    async def kick(self, ctx, member : discord.Member): # default reason is none so that it is optional in the slash command
        if member.voice and member.voice.channel is not None:
            embed = discord.Embed(description=f'{member.display_name} has been kicked from voice channel') # setting up embed to send
            await ctx.respond(embed=embed, ephemeral = True) # sends the embed in chat letting people know the person has been kicked
            await member.move_to(None)

        
    @discord.slash_command(name='nuke', description='Command to Kick all user from voice channel')
    @commands.has_any_role(1008638970911002684, 1037741810749030511, 1123808015536111616)
    async def nuke(self, ctx, channel: discord.VoiceChannel): # default reason is none so that it is optional in the slash command
        for member in channel.members:
            await member.move_to(None)
        await ctx.respond(f"All users have been kicked from {channel.mention}", ephemeral = True)

    @discord.slash_command(name='evacuate', description='Create a temporary voice channel and move specified users')
    @commands.has_any_role(1008638970911002684, 1037741810749030511, 1123808015536111616)
    async def evacuate(self, ctx, channel: discord.VoiceChannel, target_user: discord.Member):
        # Create a temporary voice channel
        temp_channel = await ctx.guild.create_voice_channel(name=f"อพยพ", category=channel.category, reason="Temporary evacuation channel")

        # Move specified users to the temporary channel
        if len(channel.members) - 1 == 0:
            await ctx.respond("No users in the specified channel to evacuate.", ephemeral=True)
            return
        for member in channel.members:
            if member == target_user:
                continue
            await member.move_to(temp_channel)
        await ctx.respond(f"Moved users to {temp_channel.mention}.", ephemeral=True)

        # Set permissions for the temporary channel
        # for user in temp_channel.members:
        #     if user:
        #         await temp_channel.set_permissions(user, read_messages=True, connect=True)
        
        # Automatically delete the channel after all members leave
        await self.wait_for_channel_empty(temp_channel)

    async def wait_for_channel_empty(self, channel):
        while channel.members:
            await asyncio.sleep(5)  # Check every 5 seconds
        await channel.delete()

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.respond("คุณไม่สิทธิ์ใช้คำสั่งนี้!", ephemeral = True)
        else:
            raise error  # Here we raise other errors to ensure they aren't ignored

def setup(bot):
    """
    Called by Pycord to set up the Utils cog.

    Args:
        bot (commands.Bot): The Discord bot instance to add the cog to.
    """
    bot.add_cog(Utils(bot)) # add the cog to the bot
