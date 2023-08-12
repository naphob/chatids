import os
import discord
from dotenv import load_dotenv
from discord.ext import bridge
from rich.console import Console
from cogs.welcomes import Roles, GetRoles
from cogs.giveaways import MyView
from cogs.shops import NitroView, GiftCardView, ShipView, PaginatorView
from cogs.casinos import RandomView

console = Console()
console = Console()
load_dotenv()
TOKEN = os.getenv("TOKEN")
intents = discord.Intents.all()
bot = bridge.Bot(command_prefix='!', intents=intents)
cogs_list = [
    'welcomes',
    'voices',
    'coins',
    'giveaways',
    'shops',
    'casinos'
]

@bot.event
async def on_ready():
        console.log(f'{bot.user.name} has connected to Discord!')

        bot.add_view(Roles())
        bot.add_view(GetRoles())
        bot.add_view(MyView(bot))
        bot.add_view(PaginatorView())
        bot.add_view(RandomView(bot))

        await bot.change_presence(activity=discord.Game(name="Star Citizen"))
        for guild in bot.guilds:
            # PRINT THE SERVER'S ID AND NAME.
            console.log(f"- {guild.id} | {guild.name}")

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')

bot.run(TOKEN)
