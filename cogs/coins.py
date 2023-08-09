import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands, bridge
from rich.console import Console
import firebase_admin
from firebase_admin import credentials, db

console = Console()
load_dotenv()
LOG_TEXT_CHANNEL_ID = 1127257320473251840
credential = os.getenv("FIREBASE_CREDENTIALS")
DB_URL = os.getenv("DB_URL")
cred = credentials.Certificate(credential)
firebase_admin.initialize_app(cred, {
    'databaseURL': DB_URL,
    'databaseAuthVariableOverride' : {
        'uid' : 'ids-bot'
    }
})
ref = db.reference('users')

class Coins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def mint_coin(self, user, amount, source):
        channel = await self.bot.fetch_channel(LOG_TEXT_CHANNEL_ID)
        coin = amount
        if not user.bot:
            await channel.send(f"<@{user.id}> recieved {coin} IDS Coins from {source}.")
            console.log(f"{user.display_name} recieved {coin} IDS Coins from {source}.")
            user_coin = ref.child(f"{user.id}").child('coin').get()
            if user_coin:
                coin += user_coin
            ref.child(f"{user.id}").set({
            'coin' : coin
            })

    async def check_coin(self, user):
        if ref.child(f"{user.id}") is not None:
            coin = ref.child(f"{user.id}").child('coin').get()
            return coin
        else:
            return 0

    async def add_coin(self, user, amount):
        user_amount = await self.check_coin(user)
        if amount > 0:
            remaining_amount = user_amount + amount
            ref.child(f"{user.id}").set({
                'coin' : remaining_amount
                })
            return remaining_amount

    async def deduct_coin(self, user, amount):
        user_amount = await self.check_coin(user)
        if user_amount >= amount and amount > 0:
            remaining_amount = user_amount - amount
            ref.child(f"{user.id}").set({
                'coin' : remaining_amount
                })
            return remaining_amount

    @commands.Cog.listener()
    async def on_message(self, message):
        # bot_command = ["!balance", "!say", "!send", "!rec", "!summon", "!leave", "!give", "!stop"]
        user = message.author
        coin = random.random()
        if message.type == discord.MessageType.premium_guild_subscription:
            await self.mint_coin(user, 150.0,"boosting the server")
        elif user.id != self.bot.user.id or not message.content.startswith('!'):
            await self.mint_coin(user, coin,"new message")
        # await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        user = payload.member
        coin = random.random()
        await self.mint_coin(user, coin, "reaction")

    @bridge.bridge_command(name="balance", help="This command will return coins balance")
    async def balance(self, ctx):
        user = ctx.author
        coin = await self.check_coin(user)
        embed = discord.Embed(
            color=discord.Color.dark_purple(),
            description= f"Balance: `{coin:,.2f}`",
            title= f"{user.display_name}'s Wallet"
        )
        embed.set_author(name="Bank of IDS")
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/d/d6/Gold_coin_icon.png")
        if coin:
            await ctx.respond(embed=embed)
            console.log(f"{user.display_name}'s balance: {coin:,.2f} IDS Coins.")
        else:
            await ctx.respond("You have no IDS coins")

    @bridge.bridge_command(name="give", help="This command will transfer coins to other's wallet")
    async def give(self, ctx, user: discord.Member, amount: float):
        channel = await self.bot.fetch_channel(LOG_TEXT_CHANNEL_ID)
        sender = ctx.author
        receiver = user
        # sender_coin = await self.check_coin(sender) #ref.child(f"{sender.id}").child('coin').get()
        # receiver_coin = await self.check_coin(receiver) #ref.child(f"{receiver.id}").child('coin').get()
        if amount > 0:
            await self.deduct_coin(sender, amount)
            await self.add_coin(receiver, amount)
            embed = discord.Embed(
            color=discord.Color.dark_purple(),
            title= f"Bank of IDS",
            description= f"IDS Coin Transfer Transaction"
            )

            embed.add_field(name="Sender", value=sender.display_name, inline=True)
            embed.add_field(name=":arrow_right:", value=f"`{amount}`", inline=True)
            embed.add_field(name="Recipient", value=receiver.display_name, inline=True)

            # await ctx.send(f"<@{sender.id}> transfered {amount} IDS Coins to <@{receiver.id}>.")
            await ctx.respond(embed=embed)
            await channel.send(f"<@{sender.id}> transfered {amount} IDS Coins to <@{receiver.id}>.")
            console.log(f"{sender.display_name} transfered {amount} IDS Coins to {receiver.display_name}.")
        else:
            await ctx.respond("Insufficient IDS coin balance or wrong amount")

    @bridge.bridge_command(name="rank", help="This command show richest users ranking")
    async def rank(self, ctx):
        result = ref.order_by_child('coin').limit_to_last(10).get()
        ranks = list(result.items())
        ranks.reverse()
        leaderboard = {}
        for key, val in ranks:
            leaderboard[key] = val['coin']

        embed = discord.Embed(
            color=discord.Color.dark_purple(),
            description= "The Richest Leaderboard",
            title= "Bank of IDS"
        )
        names = ''
        for rank, user in enumerate(leaderboard):
            if rank+1 == 1:
                rank =":first_place:"
            elif rank+1 == 2:
                rank =":second_place:"
            elif rank+1 == 3:
                rank =":third_place:"
            else:
                rank = rank+1
            names += f"{rank} <@{user}> : {leaderboard[user]:,.2f} :coin:\n"
        embed.add_field(name="Names", value=names, inline=False)
        await ctx.respond(embed=embed)

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Coins(bot)) # add the cog to the bot
