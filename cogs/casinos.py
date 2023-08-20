import json
import discord
import random
from datetime import date
from rich.console import Console
from discord.ext import commands, bridge
from firebase_admin import db


console = Console()

class RandomView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot,
        self.coins = bot.get_cog('Coins')
        self.user = self.coins.get_user()

    @discord.ui.button(label="โยก", custom_id="buy", style=discord.ButtonStyle.blurple, emoji="🕹️")
    async def slot_button_callback(self, button, interaction):
        user = interaction.user
        quota_count = self.quota_check(user)
        if quota_count == True:
            result = self.random_slot()
            embed = discord.Embed(
                title="Slot Machine",
                color=discord.Color.dark_orange()
            )
            slot_result = f"{result[0]} {result[1]} {result[2]}"
            console.log(f"{user.display_name} : {slot_result}")
            coins = self.coins
            user_balance = await coins.check_coin(user)
            try:
                await coins.deduct_coin(user, 10)
                if result[0] == "🧂" and result[1] == "🧂" and result[2] == "🧂":
                    rewards= 1000000
                    await coins.mint_coin(user, rewards, "slot machine")
                elif result[0] == result[1] and result[0] == result[2]:
                    rewards = 50000
                    await coins.mint_coin(user, rewards, "slot machine")
                elif result[0] == result[1] or result[1] == result[2]:
                    rewards = 100
                    await coins.mint_coin(user, rewards, "slot machine")
                elif result[0] == result[1] or result[0] == result[2]:
                    rewards = 1000
                    await coins.mint_coin(user, rewards, "slot machine")
                else:
                    rewards = 0

                embed.add_field(name="Result", value=slot_result, inline=False)
                embed.add_field(name="Player", value=user.display_name, inline=False)
                embed.add_field(name="Balance", value=f"`{user_balance:,.2f}`", inline=True)
                embed.add_field(name="Rewards", value=f"`{rewards}` 🪙", inline=True)

                await interaction.response.send_message(embed=embed, ephemeral = True)
            except:
                await interaction.response.send_message("คุณมีเหรียญไม่พอ", ephemeral = True)
        else:
            await interaction.response.send_message("คุณโยกสล็อตเกินโควต้าต่อวันแล้ว", ephemeral = True)

    def random_slot(self):
        items = [
                    "🥝", "🥥", "🍇", "🍈", "🍉", "🍊", "🍋", "🍍", "🥭", "🍎", "🥜",
                    "🍏", "🍐", "🍑", "🍒", "🍓", "🫐", "🍅", "🫒", "🍆", "🌽", "🌶️",
                    "🫑", "🍄", "🥑", "🥒", "🥬", "🥦", "🥔", "🧄", "🧅", "🥕", "🌰",
                    "🫘", "🍯", "🍮", "🍡", "🍭", "🍬", "🍫", "🧁", "🍰", "🎂", "🍪",
                    "🍩", "🍨", "🍧", "🍦", "🥧", "🥣", "🍝", "🫕", "🍲", "🥘", "🧆",
                    "🍢", "🥮", "🍥", "🍤", "🍣", "🦪", "🍜", "🍛", "🍚", "🍙", "🍘",
                    "🍱", "🥡", "🥠", "🥟", "🍠", "🥩", "🍗", "🍖", "🥫", "🫔", "🌯",
                    "🌮", "🥪", "🥙", "🥗", "🧀", "🫓", "🥖", "🥯", "🥨", "🥐", "🍞",
                    "🥓", "🥚", "🍳", "🧇", "🥞", "🧈", "🧂", "🍿", "🌭", "🍟", "🍔",
                    "🍕"
                ]
        result = random.choices(items, k=3)
        return result

    # def quota_check(self, user):
    #     if user not in quota:
    #         quota[user] = {}
    #         quota[user]['date'] = date.today()
    #         quota[user]['count'] = quota[user].get('count', 0) + 1
    #         # print(f"{user}: {quota[user]['count']}")
    #         return True
    #     elif quota[user]['date'] == date.today() and quota[user]['count'] < 10:
    #         quota[user]['count'] = quota[user].get('count', 0) + 1
    #         # print(f"{user}: {quota[user]['count']}")
    #         return True
    #     elif quota[user]['date'] != date.today():
    #         quota[user]['date'] = date.today()
    #         quota[user]['count'] = 1
    #         # print(f"{user}: {quota[user]['count']}")
    #         return True
    #     elif quota[user]['count'] >= 10:
    #         # print(f"{user}: {quota[user]['count']}")
    #         return False

    def quota_check(self, user):
        user_info = self.user.child(f"{user.id}")
        quota_date = user_info.child('date').get()
        quota_count = user_info.child('count').get()
        today = date.today()
        today_str = today.strftime("%Y-%m-%d")
        today_json = json.dumps(today_str)
        if user_info is None:
            # print(f"{user}: {quota[user]['count']}")
            return False
        elif quota_date == today_json and quota_count < 10:
            user_info.update({
                'count' :  quota_count + 1
                })
            # print(f"{user}: {quota[user]['count']}")
            return True
        elif quota_date != today_json:
            user_info.update({
                'date' : today_json,
                'count' : 1
                })
            # print(f"{user}: {quota[user]['count']}")
            return True
        elif quota_date == today_str and quota_count >= 10:
            # print(f"{user}: {quota[user]['count']}")
            return False

class DiceView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="โยก", custom_id="buy", style=discord.ButtonStyle.blurple, emoji="🕹️")
    async def dice_button_callback(self, button, interaction):
        user = interaction.user
        quota_count = self.quota_check(user)
        if quota_count == True:
            result = self.random_dice()


    def ramdom_dice(self):
        dices = [1, 2, 3, 4, 5, 6]
        result = random.choices(dices, k=3)
        return result

class Casinos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(name="slot", description="play slot machine")
    async def slot(self, ctx):
        embed = discord.Embed(
            title="เครื่องผลิต🧂",
            description="โยกสล็อตแมตชีนลุ้นรางวัลสูงสุด 1,000,000 IDS Coin"
        )
        example = "🍎🍌🍊  ไม่ได้รางวัล\n🍎🍎🍊  `100` IDS Coin\n🍎🍌🍎  `1,000` IDS Coin\n🍎🍎🍎  `50,000` IDS Coin\n🧂🧂🧂 `1,000,000` IDS Coin"
        fee="`10` 🪙"
        # embed.add_field(name="รางวัล", value=rewards)
        embed.set_author(name="IDS Casino", icon_url="https://phoneky.co.uk/thumbs/screensavers/down/original/animatedsl_ylrdr78z.gif")
        embed.add_field(name="Example", value= example)
        embed.add_field(name="Fee", value= fee)
        embed.set_footer(text="การพนันมีความเสี่ยง โปรดตั้งสติทุกครั้งก่อนโยก", icon_url="https://cdn-icons-png.flaticon.com/512/4201/4201973.png")
        view = RandomView(self.bot)
        await ctx.respond(embed=embed, view=view)

    @bridge.bridge_command(name="dice", description="play dice high-low")
    async def dice(self, ctx):
        embed = discord.Embed(
            title="ไฮโล🎲",
            description="มาวัดดวงกับลูกเต๋ากันว่าใครจะเฮง"
        )
        example = "สูง-ต่ำ x1 จากเดิมพัน\nคู่-คี่ x1.5 จากเดิมพัน\nตอง x3 จากเดิมพัน"
        # embed.add_field(name="รางวัล", value=rewards)
        embed.set_author(name="IDS Casino", icon_url="https://phoneky.co.uk/thumbs/screensavers/down/original/animatedsl_ylrdr78z.gif")
        embed.add_field(name="รางวีล", value= example)
        # embed.add_field(name="Fee", value= fee)
        embed.set_footer(text="การพนันมีความเสี่ยง โปรดตั้งสติทุกครั้งก่อนโยก", icon_url="https://cdn-icons-png.flaticon.com/512/4201/4201973.png")
        view = DiceView(self.bot)
        await ctx.respond(embed=embed, view=view)

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Casinos(bot)) # add the cog to the bot
