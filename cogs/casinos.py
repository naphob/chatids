import discord
import random
from rich.console import Console
from discord.ext import commands, bridge

class RandomView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="โยก", custom_id="buy", style=discord.ButtonStyle.blurple, emoji="🕹️")
    async def slot_button_callback(self, button, interaction):
        result = self.random_slot()
        user = interaction.user
        embed = discord.Embed(
            title="Slot Machine",
            color=discord.Color.dark_orange()
        )
        slot_result = f"{result[0]} {result[1]} {result[2]}"
        coins = self.bot.get_cog('Coins')
        user_balance = await coins.check_coin(user)
        await coins.deduct_coin(user, 10)
        if result[0] == result[1] and result[0] == result[2]:
            rewards = 50000
            await coins.mint_coin(user, rewards, "slot machine")
        elif result[0] == result[1] or result[1] == result[2]:
            rewards = 100
            await coins.mint_coin(user, rewards, "slot machine")
        elif result[0] == result[1] or result[0] == result[2]:
            rewards = 1000
            await coins.mint_coin(user, rewards, "slot machine")
        elif result[0] == "7️⃣" and result[1] == "7️⃣" and result[2] == "7️⃣":
            rewards= 1000000
            await coins.mint_coin(user, rewards, "slot machine")
        else:
            rewards = 0

        embed.add_field(name="Result", value=slot_result, inline=False)
        embed.add_field(name="Player", value=user.display_name, inline=False)
        embed.add_field(name="Balance", value=f"`{user_balance:,.2f}`", inline=True)
        embed.add_field(name="Rewards", value=f"`{rewards}` 🪙", inline=True)

        await interaction.response.send_message(embed=embed, ephemeral = True)

    def random_slot(self):
        self.items = [
                    "🥝", "🥥", "🍇", "🍈", "🍉", "🍊", "🍋", "🍍", "🥭", "🍎", "🥜",
                    "🍏", "🍐", "🍑", "🍒", "🍓", "🫐", "🍅", "🫒", "🍆", "🌽", "🌶️",
                    "🫑", "🍄", "🥑", "🥒", "🥬", "🥦", "🥔", "🧄", "🧅", "🥕", "🌰",
                    "🫘", "🍯", "🍮", "🍡", "🍭", "🍬", "🍫", "🧁", "🍰", "🎂", "🍪",
                    "🍩", "🍨", "🍧", "🍦", "🥧", "🥣", "🍝", "🫕", "🍲", "🥘", "🧆",
                    "🍢", "🥮", "🍥", "🍤", "🍣", "🦪", "🍜", "🍛", "🍚", "🍙", "🍘",
                    "🍱", "🥡", "🥠", "🥟", "🍠", "🥩", "🍗", "🍖", "🥫", "🫔", "🌯",
                    "🌮", "🥪", "🥙", "🥗", "🧀", "🫓", "🥖", "🥯", "🥨", "🥐", "🍞",
                    "🥓", "🥚", "🍳", "🧇", "🥞", "🧈", "🧂", "🍿", "🌭", "🍟", "🍔",
                    "🍕", "7️⃣"
                ]
        result = random.choices(self.items, k=3)
        print(result)
        return result

class Casinos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(name="slot", help="play slot machine")
    async def slot(self, ctx):
        embed = discord.Embed(
            title="Slot Machine",
            description="โยกสล็อตแมตชีนลุ้นรางวัลสูงสุด 1,000,000 IDS Coin"
        )
        example = "🍎🍌🍊  ไม่ได้รางวัล\n🍎🍎🍊  `100` IDS Coin\n🍎🍌🍎  `1,000` IDS Coin\n🍎🍎🍎  `50,000` IDS Coin\n7️⃣7️⃣7️⃣ `1,000,000` IDS Coin"
        fee="`10` 🪙"
        # embed.add_field(name="รางวัล", value=rewards)
        embed.add_field(name="Example", value= example)
        embed.add_field(name="Fee", value= fee)
        embed.set_footer(text="การพนันมีความเสี่ยง โปรดตั้งสติทุกครั้งก่อนโยก")
        view = RandomView(self.bot)
        await ctx.respond(embed=embed, view=view)

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Casinos(bot)) # add the cog to the bot
