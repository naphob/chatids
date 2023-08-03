import discord
from rich.console import Console
from discord.ext import commands, bridge

console = Console()
LOG_TEXT_CHANNEL_ID = 1127257320473251840

class ShopView(discord.ui.View):
    def __init__(self, bot, price):
        super().__init__(timeout=None)
        self.bot = bot
        self.price = price

    @discord.ui.button(label="Buy", custom_id="buy", style=discord.ButtonStyle.green, emoji="🪙", disabled=False)
    async def button_callback(self, button, interaction):
        channel = await self.bot.fetch_channel(LOG_TEXT_CHANNEL_ID)
        coins = self.bot.get_cog('Coins')
        user = interaction.user
        user_coin = await coins.check_coin(user)
        with open("nitro.txt", "r") as f:
            lines = f.readlines()
            nitro = lines[0]
            stock = len(lines)
        if user_coin >= self.price and stock > 0:
            remaining = await coins.deduct_coin(user, self.price)
            embed = discord.Embed(
            title = "Discord Nitro 1 Month",
                description = "กรุณาคลิ๊กลิงค์ข้างล่างเพื่อทำการใช้งานดิสคอร์ดไนโตร",
                color = discord.Color.dark_green()
            )
            rewards = f"Discord Nitro Gift Card 1 Month\n {nitro}"
            embed.add_field(name="รายการสินค้า", value=rewards, inline=False)
            embed.add_field(name="ราคา", value=f"{self.price:,} IDS Coin", inline=True)
            embed.add_field(name="IDS Coin ที่เหลืออยู่", value=f"{remaining}", inline=True)
            await interaction.response.send_message("ขอบคุณที่อุดหนุน IDS Shop นี่คือสินค้าของคุณ",embed=embed, ephemeral = True)
            await channel.send(f"<@{user.id}> brought Nitro from IDS Shop")
            console.log(f"{user.display_name} brought Nitro from IDS Shop")
            with open('nitro.txt', 'r+', encoding='utf-8') as txt_file:
                lines = txt_file.readlines()
                txt_file.seek(0)
                if len(lines):
                    for i, line in enumerate(lines):
                        if 1 <= i:
                            txt_file.write(line)
                    txt_file.truncate()
        else:
            await interaction.response.send_message("คุณมี IDS Coin ไม่พอ", ephemeral = True)

class Shops(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(name="shop", help="show item shop")
    async def shop(self, ctx):
        embed = discord.Embed(
            title="Discord Nitro 1 Month",
            description="ใช้ดิสดอร์ดไนโตรได้ 1 เดือน ซื้อแล้วอย่าลืมบูสเพชรให้กับ IDS ด้วยนะ",
            color=discord.Color.dark_purple()
        )
        with open("nitro.txt", "r") as f:
            lines = f.readlines()
            stock = len(lines)
            price = 1500
        embed.set_author(name="IDS Shop", icon_url="https://cdn-icons-png.flaticon.com/512/3900/3900101.png")
        embed.set_image(url="https://cdn.vcgamers.com/news/wp-content/uploads/2021/06/discord-nitro-1144x430.png")
        embed.add_field(name="Price", value=f"~~3,499~~ **{price:,}** IDS Coin")
        embed.add_field(name="Stock", value=f"{stock}")
        view=ShopView(self.bot, price)
        await ctx.respond(embed=embed, view=view)

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Shops(bot)) # add the cog to the bot
