import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from rich.console import Console
import firebase_admin
from firebase_admin import credentials
from cogs.welcomes import Roles, GetRoles
from cogs.giveaways import MyView
# from cogs.shops import NitroView, GiftCardView, ShipView, PaginatorView
from cogs.casinos import RandomView, DiceView

console = Console()
load_dotenv()
TOKEN = os.getenv("TOKEN")
cogs_list = [
    'welcomes',
    'voices',
    'coins',
    'giveaways',
    # 'shops',
    'casinos',
    'utils',
    'announces',
    'verification',
    'playtime',
]
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
credential = os.getenv("FIREBASE_CREDENTIALS")
DB_URL = os.getenv("DB_URL")
UID = os.getenv("UID")
cred = credentials.Certificate(credential)
firebase_admin.initialize_app(cred, {
    'databaseURL': DB_URL,
    'databaseAuthVariableOverride' : {
        'uid' : UID
    }
})

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')

@bot.event
async def on_ready():
        
        console.log(f'{bot.user.name} has connected to Discord!')

        bot.add_view(Roles(bot))
        bot.add_view(GetRoles())
        bot.add_view(MyView(bot))
        # bot.add_view(PaginatorView())
        bot.add_view(RandomView(bot))
        bot.add_view(DiceView(bot))

        await bot.change_presence(activity=discord.Game(name="Star Citizen"))
        for guild in bot.guilds:
            # PRINT THE SERVER'S ID AND NAME.
            console.log(f"- {guild.id} | {guild.name}")

bot.run(TOKEN)
