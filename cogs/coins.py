import random
import discord
from dotenv import load_dotenv
from discord.ext import commands, bridge
from rich.console import Console
from firebase_admin import db

console = Console()
load_dotenv()
LOG_TEXT_CHANNEL_ID = 1127257320473251840

# ref = db.reference('users')

class Coins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user = db.reference('users')

    def get_user(self):
        return self.user

    async def mint_coin(self, user, amount, source):
        channel = await self.bot.fetch_channel(LOG_TEXT_CHANNEL_ID)
        coin = amount
        if not user.bot:
            await channel.send(f"{user.display_name} recieved {coin} IDS Coins from {source}.")
            console.log(f"{user.display_name} recieved {coin} IDS Coins from {source}.")
            user_coin = self.user.child(f"{user.id}").child('coin').get()
            if user_coin:
                coin += user_coin
            self.user.child(f"{user.id}").update({
            'coin' : coin
            })

    async def check_coin(self, user):
        if self.user.child(f"{user.id}") is not None:
            coin = self.user.child(f"{user.id}").child('coin').get()
            return coin
        else:
            return 0

    async def add_coin(self, user, amount):
        user_amount = await self.check_coin(user)
        if amount > 0:
            remaining_amount = user_amount + amount
            self.user.child(f"{user.id}").update({
                'coin' : remaining_amount
                })
            return remaining_amount

    async def deduct_coin(self, user, amount):
        user_amount = await self.check_coin(user)
        if user_amount >= amount and amount > 0:
            remaining_amount = user_amount - amount
            self.user.child(f"{user.id}").update({
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

    @discord.slash_command(name="balance", description="This command will return coins balance")
    async def balance(self, ctx):
        user = ctx.author
        coin = await self.check_coin(user)
        embed = discord.Embed(
            color=discord.Color.dark_purple(),
            description= f"Balance: `{coin:,.2f}`",
            title= f"{user.display_name}'s Wallet"
        )
        embed.set_author(name="Bank of IDS", icon_url="https://media.discordapp.net/attachments/1128316572134539305/1130354286900031499/imnanoart_an_illustration_of_a_space_logo_with_the_combination__62ac037c-ecee-4a48-a815-977746c10bd2.png?width=837&height=837")
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/d/d6/Gold_coin_icon.png")
        if coin:
            await ctx.send_response(embed=embed, ephemeral = True)
            console.log(f"{user.display_name}'s balance: {coin:,.2f} IDS Coins.")
        else:
            await ctx.send_response("You have no IDS coins", ephemeral = True)

    @discord.slash_command(name="give", description="This command will transfer coins to other's wallet")
    async def give(self, ctx, user: discord.Member, amount: float):
        channel = await self.bot.fetch_channel(LOG_TEXT_CHANNEL_ID)
        sender = ctx.author
        receiver = user
        coin = await self.check_coin(sender)
        if amount > 0 and coin > 0:
            await self.deduct_coin(sender, amount)
            await self.add_coin(receiver, amount)
            embed = discord.Embed(
            color=discord.Color.dark_purple(),
            title="IDS Coin Transfer Transaction"
            )
            embed.set_author(name="Bank of iDS", icon_url="https://media.discordapp.net/attachments/1128316572134539305/1130354286900031499/imnanoart_an_illustration_of_a_space_logo_with_the_combination__62ac037c-ecee-4a48-a815-977746c10bd2.png?width=837&height=837")
            embed.add_field(name="Sender", value=sender.display_name, inline=True)
            embed.add_field(name=":arrow_right:", value=f"`{amount}`", inline=True)
            embed.add_field(name="Recipient", value=receiver.display_name, inline=True)

            # await ctx.send(f"<@{sender.id}> transfered {amount} IDS Coins to <@{receiver.id}>.")
            await ctx.respond(embed=embed)
            await channel.send(f"<@{sender.id}> transfered {amount} IDS Coins to <@{receiver.id}>.")
            console.log(f"{sender.display_name} transfered {amount} IDS Coins to {receiver.display_name}.")
        else:
            await ctx.send_response("Insufficient IDS coin balance or wrong amount", ephemeral = True)

    @discord.slash_command(name="rank", description="This command show richest users ranking")
    async def rank(self, ctx):
        result = self.user.order_by_child('coin').limit_to_last(10).get()
        ranks = list(result.items())
        ranks.reverse()
        leaderboard = {}
        for key, val in ranks:
            leaderboard[key] = val['coin']

        embed = discord.Embed(
            color=discord.Color.dark_purple(),
            title= "The Richest Leaderboard"
        )
        embed.set_author(name="Bank of iDS", icon_url="https://media.discordapp.net/attachments/1128316572134539305/1130354286900031499/imnanoart_an_illustration_of_a_space_logo_with_the_combination__62ac037c-ecee-4a48-a815-977746c10bd2.png?width=837&height=837")
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
