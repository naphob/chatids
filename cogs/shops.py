import discord
from rich.console import Console
from discord.ext import commands, bridge

console = Console()
LOG_TEXT_CHANNEL_ID = 1127257320473251840
room_number = 0

class ShopView(discord.ui.View):
    def __init__(self, bot, price):
        super().__init__(timeout=None)
        self.bot = bot
        self.price = price

    @discord.ui.button(label="Buy", custom_id="buy", style=discord.ButtonStyle.green, emoji="🪙", disabled=False)
    async def button_callback(self, button, interaction):
        global room_number
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
            room_number += 1
            channel_name = f"{room_number}-รับสินค้า"
            guild = await discord.utils.get_or_fetch(self.bot, 'guild', 1004082951753052232)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True, view_channel=True),
                guild.get_member(user.id): discord.PermissionOverwrite(read_messages=True, view_channel=True),
                guild.get_member(855426672806199336): discord.PermissionOverwrite(read_messages=True, view_channel=True)
            }
            category_name = 'IDS-SHOP'
            category = discord.utils.get(guild.categories, name=category_name)
            text_channel = await guild.create_text_channel(channel_name, position=1, overwrites=overwrites, category=category)
            await text_channel.send("คุณจะได้รับ Discord Nitro Gift Card 1 Month ภายใน 24 ชั่วโมงในห้องรับสินค้าที่ถูกสร้างขึ้นใหม่ หากมีข้อสงสัยให้ทิ้งข้อความไว้ให้แอดมินช่วยเหลือต่อไป")

            embed.add_field(name="รายการสินค้า", value=rewards, inline=False)
            embed.add_field(name="ราคา", value=f"{self.price:,} IDS Coin", inline=True)
            embed.add_field(name="IDS Coin ที่เหลืออยู่", value=f"{remaining}", inline=True)
            await interaction.response.send_message(f"ขอบคุณที่อุดหนุน IDS Shop คุณจะได้รับสินค้าภายใน 24 ชั่วโมงในห้อง <#{text_channel.id}> ที่ถูกสร้างขึ้นใหม่", ephemeral = True)
            await channel.send(f"<@{user.id}> bought Nitro from IDS Shop")
            console.log(f"{user.display_name} bought Nitro from IDS Shop")
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
        price = 1500
        embed.set_author(name="IDS Shop", icon_url="https://cdn-icons-png.flaticon.com/512/3900/3900101.png")
        embed.set_image(url="https://cdn.vcgamers.com/news/wp-content/uploads/2021/06/discord-nitro-1144x430.png")
        embed.add_field(name="Price", value=f"~~3,499~~ **{price:,}** IDS Coin")
        view=ShopView(self.bot, price)
        await ctx.send(embed=embed, view=view)


    @bridge.bridge_command(name="nitro", help="send item to buyer")
    async def nitro(self, ctx, url, channel : discord.TextChannel):
        if ctx.author.id == 855426672806199336:
            embed = discord.Embed(
                title="Discord Nitro 1 Month",
                description=f"ใช้ดิสดอร์ดไนโตรได้ 1 เดือน ซื้อแล้วอย่าลืมบูสเพชรให้กับ IDS ด้วยนะ\n{url}",
                color=discord.Color.dark_purple()
            )
            embed.set_author(name="IDS Shop", icon_url="https://cdn-icons-png.flaticon.com/512/3900/3900101.png")
            embed.set_image(url="https://cdn.vcgamers.com/news/wp-content/uploads/2021/06/discord-nitro-1144x430.png")
            embed.set_footer(text="กดที่ลิงค์เพื่อใช้ไนโตรภายใน 24 ชั่วโมงก่อนลิงค์จะหมดอายุ")
            await channel.send(embed=embed)

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Shops(bot)) # add the cog to the bot
