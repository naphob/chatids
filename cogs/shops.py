import discord
from rich.console import Console
from discord.ext import commands, bridge, pages

console = Console()
LOG_TEXT_CHANNEL_ID = 1127257320473251840
room_number = 0

class PaginatorView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.page_buttons = [
            pages.PaginatorButton(
                "first", label="<<-", style=discord.ButtonStyle.green
            ),
            pages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.green),
            pages.PaginatorButton(
                "page_indicator", style=discord.ButtonStyle.gray, disabled=True
            ),
            pages.PaginatorButton("next", label="->", style=discord.ButtonStyle.green),
            pages.PaginatorButton("last", label="->>", style=discord.ButtonStyle.green),
        ]

    def get_buttons(self):
        return self.page_buttons

class NitroView(discord.ui.View):
    def __init__(self, bot, price):
        super().__init__(timeout=None)
        self.bot = bot
        self.price = price

    @discord.ui.button(label="Buy", custom_id="buy", style=discord.ButtonStyle.blurple, emoji="🪙", disabled=False)
    async def nitro_button_callback(self, button, interaction):
        global room_number
        channel = await self.bot.fetch_channel(LOG_TEXT_CHANNEL_ID)
        coins = self.bot.get_cog('Coins')
        user = interaction.user
        user_coin = await coins.check_coin(user)
        if user_coin >= self.price:
            await coins.deduct_coin(user, self.price)

            room_number += 1
            channel_name = f"{room_number}-รับสินค้า"
            guild = await discord.utils.get_or_fetch(self.bot, 'guild', 1004082951753052232)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False),
                guild.me: discord.PermissionOverwrite(read_messages=True, view_channel=True),
                guild.get_member(user.id): discord.PermissionOverwrite(read_messages=True, view_channel=True),
                guild.get_member(855426672806199336): discord.PermissionOverwrite(read_messages=True, view_channel=True)
            }
            category_name = 'IDS-SHOP'
            category = discord.utils.get(guild.categories, name=category_name)
            text_channel = await guild.create_text_channel(channel_name, position=1, overwrites=overwrites, category=category)
            await text_channel.send("คุณจะได้รับ Discord Nitro Gift Card 1 Month ภายใน 24 ชั่วโมงในห้องรับสินค้าที่ถูกสร้างขึ้นใหม่ หากมีข้อสงสัยให้ทิ้งข้อความไว้ให้แอดมินช่วยเหลือต่อไป")
            await interaction.response.send_message(f"ขอบคุณที่อุดหนุน IDS Shop คุณจะได้รับสินค้าภายใน 24 ชั่วโมงในห้อง <#{text_channel.id}> ที่ถูกสร้างขึ้นใหม่", ephemeral = True)
            await channel.send(f"<@{user.id}> bought Nitro from IDS Shop")
            console.log(f"{user.display_name} bought Nitro from IDS Shop")
        else:
            await interaction.response.send_message("คุณมี IDS Coin ไม่พอ", ephemeral = True)


class GiftCardView(discord.ui.View):
    def __init__(self, bot, price):
        super().__init__(timeout=None)
        self.bot = bot
        self.price = price

    @discord.ui.button(label="Buy", custom_id="buy", style=discord.ButtonStyle.blurple, emoji="🪙", disabled=False)
    async def button_callback(self, button, interaction):
        global room_number
        channel = await self.bot.fetch_channel(LOG_TEXT_CHANNEL_ID)
        coins = self.bot.get_cog('Coins')
        user = interaction.user
        user_coin = await coins.check_coin(user)
        if user_coin >= self.price:
            await coins.deduct_coin(user, self.price)

            room_number += 1
            channel_name = f"{room_number}-รับสินค้า"
            guild = await discord.utils.get_or_fetch(self.bot, 'guild', 1004082951753052232)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False),
                guild.me: discord.PermissionOverwrite(read_messages=True, view_channel=True),
                guild.get_member(user.id): discord.PermissionOverwrite(read_messages=True, view_channel=True),
                guild.get_member(855426672806199336): discord.PermissionOverwrite(read_messages=True, view_channel=True)
            }
            category_name = 'IDS-SHOP'
            category = discord.utils.get(guild.categories, name=category_name)
            text_channel = await guild.create_text_channel(channel_name, position=1, overwrites=overwrites, category=category)
            await text_channel.send("คุณจะได้รับ Star Citizen $10 Gift Card ภายใน 24 ชั่วโมงในห้องรับสินค้าที่ถูกสร้างขึ้นใหม่ หากมีข้อสงสัยให้ทิ้งข้อความไว้ให้แอดมินช่วยเหลือต่อไป")
            await interaction.response.send_message(f"ขอบคุณที่อุดหนุน IDS Shop คุณจะได้รับสินค้าภายใน 24 ชั่วโมงในห้อง <#{text_channel.id}> ที่ถูกสร้างขึ้นใหม่", ephemeral = True)
            await channel.send(f"<@{user.id}> bought SC Gift Card from IDS Shop")
            console.log(f"{user.display_name} bought SC Gift Card from IDS Shop")
        else:
            await interaction.response.send_message("คุณมี IDS Coin ไม่พอ", ephemeral = True)

class ShipView(discord.ui.View):
    def __init__(self, bot, price):
        super().__init__(timeout=None)
        self.bot = bot
        self.price = price

    @discord.ui.button(label="Buy", custom_id="buy", style=discord.ButtonStyle.blurple, emoji="🪙", disabled=False)
    async def button_callback(self, button, interaction):
        global room_number
        channel = await self.bot.fetch_channel(LOG_TEXT_CHANNEL_ID)
        coins = self.bot.get_cog('Coins')
        user = interaction.user
        user_coin = await coins.check_coin(user)
        if user_coin >= self.price:
            await coins.deduct_coin(user, self.price)

            room_number += 1
            channel_name = f"{user.name}-{room_number}-รับสินค้า"
            guild = await discord.utils.get_or_fetch(self.bot, 'guild', 1004082951753052232)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False),
                guild.me: discord.PermissionOverwrite(read_messages=True, view_channel=True),
                guild.get_member(user.id): discord.PermissionOverwrite(read_messages=True, view_channel=True),
                guild.get_member(855426672806199336): discord.PermissionOverwrite(read_messages=True, view_channel=True)
            }
            category_name = 'IDS-SHOP'
            category = discord.utils.get(guild.categories, name=category_name)
            text_channel = await guild.create_text_channel(channel_name, position=1, overwrites=overwrites, category=category)
            await text_channel.send("คุณจะได้รับ MUSTANG ALPHA STARTER PACK ภายใน 24 ชั่วโมงในห้องรับสินค้าที่ถูกสร้างขึ้นใหม่ หากมีข้อสงสัยให้ทิ้งข้อความไว้ให้แอดมินช่วยเหลือต่อไป")
            await interaction.response.send_message(f"ขอบคุณที่อุดหนุน IDS Shop คุณจะได้รับสินค้าภายใน 24 ชั่วโมงในห้อง <#{text_channel.id}> ที่ถูกสร้างขึ้นใหม่", ephemeral = True)
            await channel.send(f"<@{user.id}> bought MUSTANG ALPHA STARTER PACK from IDS Shop")
            console.log(f"{user.display_name} bought MUSTANG ALPHA STARTER PACK from IDS Shop")
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
        embed.set_thumbnail(url="https://static-00.iconduck.com/assets.00/discord-icon-512x511-blfje7wy.png")
        embed.add_field(name="Price", value=f"~~3,499~~ **{price:,}** IDS Coin")
        view= NitroView(self.bot, price)
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
        else:
            await ctx.respond("You don't have permissioin to run this command.", ephemeral=True)

    # @bridge.bridge_command(name="page")
    # async def page(self, ctx: discord.ApplicationContext):
    #     sale_page = []
    #     embed = discord.Embed(
    #                 title="Discord Nitro 1 Month",
    #                 description="ใช้ดิสดอร์ดไนโตรได้ 1 เดือน ซื้อแล้วอย่าลืมบูสเพชรให้กับ IDS ด้วยนะ",
    #                 color=discord.Color.dark_purple()
    #             )
    #     embed.set_author(name="IDS Shop", icon_url="https://cdn-icons-png.flaticon.com/512/3900/3900101.png")
    #     embed.set_image(url="https://cdn.vcgamers.com/news/wp-content/uploads/2021/06/discord-nitro-1144x430.png")
    #     embed.set_thumbnail(url="https://static-00.iconduck.com/assets.00/discord-icon-512x511-blfje7wy.png")
    #     embed.add_field(name="Price", value=f"~~3,499~~ **1,500** IDS Coin")

    #     embed2 = discord.Embed(
    #                 title="Star Citizen $10 Gift Card",
    #                 description="ใช้สำหรับซื้่อของในเกม Star Citizen",
    #                 color=discord.Color.dark_blue()
    #             )
    #     embed2.set_author(name="IDS Shop", icon_url="https://cdn-icons-png.flaticon.com/512/3900/3900101.png")
    #     embed2.set_image(url="https://robertsspaceindustries.com/media/kh65mcqfdj5j0r/slideshow/GiftCard_10Dollars_FINAL-1-Min.png")
    #     embed2.set_thumbnail(url="https://cdn.icon-icons.com/icons2/2407/PNG/512/star_citizen_icon_146095.png")
    #     embed2.add_field(name="Price", value=f"~~3,499~~ **1,500** IDS Coin")

    #     embed3 = discord.Embed(
    #                 title="MUSTANG ALPHA STARTER PACK",
    #                 description="ตัวเกม Star Citizen พร้อมยาน MUSTANG ALPHA มูลค่า $45",
    #                 color=discord.Color.dark_blue()
    #             )
    #     embed3.set_author(name="IDS Shop", icon_url="https://cdn-icons-png.flaticon.com/512/3900/3900101.png")
    #     embed3.set_image(url="https://media.robertsspaceindustries.com/hq53y1xaq86zn/slideshow.png")
    #     embed3.set_thumbnail(url="https://cdn.icon-icons.com/icons2/2407/PNG/512/star_citizen_icon_146095.png")
    #     embed3.add_field(name="Price", value=f"15,000 IDS Coin")

    #     page = pages.Page(
    #             embeds=[embed],
    #             custom_view=NitroView(self.bot, 1500)
    #         )
    #     page2 = pages.Page(
    #             embeds=[embed2],
    #             custom_view=GiftCardView(self.bot, 1500)
    #         )
    #     page3 = pages.Page(
    #             embeds=[embed3],
    #             custom_view=ShipView(self.bot, 15000)
    #         )

    #     sale_page.append(page)
    #     sale_page.append(page2)
    #     sale_page.append(page3)

    #     custom_buttons = PaginatorView.get_buttons()
    #     paginator = pages.Paginator(pages=sale_page)
    #     paginator.remove_button("first")
    #     paginator.remove_button("last")

    #     await paginator.send(ctx)

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Shops(bot)) # add the cog to the bot
