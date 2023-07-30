import os
import discord
from dotenv import load_dotenv
from discord.ext import bridge
from rich.console import Console

console = Console()
load_dotenv()
TOKEN = os.getenv("TOKEN")
counter = 0
intents = discord.Intents.all()
bot = bridge.Bot(command_prefix='!', intents=intents)
cogs_list = [
    'welcomes',
    'voices',
    'coins'
]

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')

bot.run(TOKEN)
