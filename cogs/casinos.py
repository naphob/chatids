import json
import discord
import random
from datetime import date
from discord.interactions import Interaction
from rich.console import Console
from discord.ext import commands, bridge
from firebase_admin import db


console = Console()
MAX_QUOTA = 20

class RandomView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
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
            await interaction.response.send_message("คุณใช้โควต้าต่อวันเกินกำหนดแล้ว", ephemeral = True)

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

    def quota_check(self, user):
        user_info = self.user.child(f"{user.id}")
        quota_date = user_info.child('date').get()
        quota_count = user_info.child('count').get()
        today = date.today()
        today_str = today.strftime("%Y-%m-%d")
        today_json = json.dumps(today_str)
        if user_info is None:
            return False
        elif quota_date == today_json and quota_count < MAX_QUOTA:
            user_info.update({
                'count' :  quota_count + 1
                })
            return True
        elif quota_date != today_json:
            user_info.update({
                'date' : today_json,
                'count' : 1
                })
            return True
        elif quota_date == today_str and quota_count >= MAX_QUOTA:
            return False

class MyModal(discord.ui.Modal):
    def __init__(self, bot, prediction, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, timeout=None)
        self.bot = bot
        self.prediction = prediction
        self.coins = bot.get_cog('Coins')
        self.user = self.coins.get_user()

        self.add_item(discord.ui.InputText(label="เงินเดิมพัน"))
        if self.prediction == "favorite":
            self.add_item(discord.ui.InputText(label="ทายผลเลขตัวที่ 1", max_length=1, style=discord.InputTextStyle.short))
        elif self.prediction == "tod":
            self.add_item(discord.ui.InputText(label="ทายผลเลขตัวที่ 1", max_length=1, style=discord.InputTextStyle.short))
            self.add_item(discord.ui.InputText(label="ทายผลเลขตัวที่ 2", max_length=1, style=discord.InputTextStyle.short))

    async def callback(self, interaction: discord.Interaction):
        stake = float(self.children[0].value)
        user = interaction.user
        if self.prediction == "favorite":
            slot1 = self.children[1].value
        elif self.prediction == "tod":
            slot1 = self.children[1].value
            slot2 = self.children[2].value
        coins = self.coins
        user_balance = await coins.check_coin(user)
        if user_balance >= stake:
            quota_count = RandomView(self.bot)
            quota_count = quota_count.quota_check(user)
            if quota_count == True:
                result = RandomDice()
                result = result.random()
                embed = discord.Embed(
                    title="ไฮโล 🎲",
                    color=discord.Color.dark_orange()
                )
                dices = {
                    1:"<:dice1:1140218148109439087>",
                    2:"<:dice2:1140218191101042739>",
                    3:"<:dice3:1140218230259077172>",
                    4:"<:dice4:1140218258180546602>",
                    5:"<:dice5:1140218314388414534>",
                    6:"<:dice6:1140218345141055488>"
                    }
                roll_result = f"{dices[result[0]]}   {dices[result[1]]}  {dices[result[2]]}"
                console.log(f"{user.display_name} : {roll_result}")
                coins = self.coins
                dice_sum = result[0] + result[1] + result[2]
                num_tpye = dice_sum % 2
                rewards = 0
                if self.prediction == 'high' and dice_sum >= 10:
                    rewards = stake
                    await coins.mint_coin(user, rewards, "roll dice")
                elif self.prediction == 'low' and dice_sum <= 12:
                    rewards = stake
                    await coins.mint_coin(user, rewards, "roll dice")
                elif self.prediction == 'even' and num_tpye == 0:
                    rewards = stake
                    await coins.mint_coin(user, rewards, "roll dice")
                elif self.prediction == 'odd' and num_tpye != 0:
                    rewards = stake
                    await coins.mint_coin(user, rewards, "roll dice")
                elif self.prediction == 'tripple' and result[0] == result[1] and result[0] == result[2]:
                    rewards = stake * 3.0
                    await coins.mint_coin(user, rewards, "roll dice")
                elif self.prediction == 'eleven' and dice_sum == 11:
                    rewards = stake * 7.0
                    await coins.mint_coin(user, rewards, "roll dice")
                elif self.prediction == 'favorite' and slot1 in result:
                    rewards = stake
                    await coins.mint_coin(user, rewards, "roll dice")
                elif self.prediction == 'tod' and slot1 in result and slot2 in result:
                    if slot1 != slot2:
                        rewards = stake * 5.0
                        await coins.mint_coin(user, rewards, "roll dice")
                    else:
                        rewards = 0
                        await coins.deduct_coin(user, stake)
                else:
                    rewards = 0
                    await coins.deduct_coin(user, stake)
                embed.add_field(name="Prediction", value=self.prediction, inline=False)
                embed.add_field(name="Result", value=roll_result, inline=True)
                embed.add_field(name="Sum", value=dice_sum , inline=True)
                embed.add_field(name="Player", value=user.display_name, inline=False)
                embed.add_field(name="Balance", value=f"`{user_balance:,.2f}`", inline=True)
                embed.add_field(name="Rewards", value=f"`{rewards}` 🪙", inline=True)
                await interaction.response.send_message(embed=embed, ephemeral = True)
            else:
                await interaction.response.send_message("คุณใช้โควต้าต่อวันเกินกำหนดแล้ว", ephemeral = True)
        else:
                await interaction.response.send_message("คุณมีเหรียญไม่พอ", ephemeral = True)

class RandomDice:
    def __init__(self):
        self.dices = [1, 2, 3, 4, 5, 6]

    def random(self):
        return random.choices(list(self.dices), k=3)


class DiceView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="สูง", custom_id="high", style=discord.ButtonStyle.green)
    async def high_button_callback(self, button, interaction):
        modal = MyModal(self.bot, "high", title="ทายผล: สูง")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="ต่ำ", custom_id="low", style=discord.ButtonStyle.green)
    async def low_button_callback(self, button, interaction):
        modal = MyModal(self.bot, "low", title="ทายผล: ต่ำ")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="คู่", custom_id="even", style=discord.ButtonStyle.green)
    async def even_button_callback(self, button, interaction):
        modal = MyModal(self.bot, "even", title="ทายผล: คู่")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="คี่", custom_id="odd", style=discord.ButtonStyle.green)
    async def odd_button_callback(self, button, interaction):
        modal = MyModal(self.bot, "odd", title="ทายผล: คี่")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="ตอง", custom_id="triple", style=discord.ButtonStyle.blurple)
    async def triple_button_callback(self, button, interaction):
        modal = MyModal(self.bot, "triple", title="ทายผล: ตอง")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="เต็ง", custom_id="favorite", style=discord.ButtonStyle.green)
    async def favorite_button_callback(self, button, interaction):
        modal = MyModal(self.bot, "favorite", title="ทายผล: เต็ง")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="โต๊ด", custom_id="tod", style=discord.ButtonStyle.blurple)
    async def tod_button_callback(self, button, interaction):
        modal = MyModal(self.bot, "tod", title="ทายผล: โต๊ด")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="11 ไฮโล", custom_id="eleven", style=discord.ButtonStyle.red)
    async def eleven_button_callback(self, button, interaction):
        modal = MyModal(self.bot, "eleven", title="ทายผล: 11 ไฮโล")
        await interaction.response.send_modal(modal)

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
        embed.set_footer(text="การพนันมีความเสี่ยง โปรดตั้งสติทุกครั้งก่อนเล่น", icon_url="https://cdn-icons-png.flaticon.com/512/4201/4201973.png")
        view = RandomView(self.bot)
        await ctx.respond(embed=embed, view=view)

    @bridge.bridge_command(name="dice", description="play dice high-low")
    async def dice(self, ctx):
        embed = discord.Embed(
            title="ไฮโล 🎲",
            description="มาวัดดวงกับลูกเต๋ากันว่าใครจะเฮง"
        )
        example = "สูง-ต่ำ x1 จากเดิมพัน\nคู่-คี่ x1 จากเดิมพัน\nเต็ง x1 จากเดิมพัน\nตอง x3 จากเดิมพัน\nโต๊ด x5 จากเดิมพัน\n11 ไฮโล x7 จากเดิมพัน"
        # embed.add_field(name="รางวัล", value=rewards)
        embed.set_author(name="IDS Casino", icon_url="https://phoneky.co.uk/thumbs/screensavers/down/original/animatedsl_ylrdr78z.gif")
        embed.add_field(name="รางวัล", value= example)
        embed.set_footer(text="การพนันมีความเสี่ยง โปรดตั้งสติทุกครั้งก่อนเล่น", icon_url="https://cdn-icons-png.flaticon.com/512/4201/4201973.png")
        view = DiceView(self.bot)
        await ctx.respond(embed=embed, view=view)

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Casinos(bot)) # add the cog to the bot
