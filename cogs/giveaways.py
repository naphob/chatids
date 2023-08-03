import discord
from discord.ext import commands, bridge
from random import randrange
from rich.console import Console

console = Console()
LOG_TEXT_CHANNEL_ID = 1127257320473251840
recipients = []
reward_pool = []

class MyView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="รับรางวัล", custom_id="random", style=discord.ButtonStyle.primary, emoji="🎉", disabled=True)
    async def button_callback(self, button, interaction):
        channel = await self.bot.fetch_channel(LOG_TEXT_CHANNEL_ID)
        user = interaction.user
        coins = self.bot.get_cog('Coins')
        coin = 500.0
        embed = discord.Embed(
            title = "🎊 กิจกรรมฉลองครบรอบ 1 ปี 🎊",
                description = "เนื่องในโอกาสครบรอบ 1 ปี IDS discord server วันที่ 3 สิงหาคม ทีมงาน IDS มีกิจกรรมแจกของรางวัลให้สมาชิกทุกท่านดังนี้",
                color = discord.Color.dark_red()
        )

        if user in recipients:
            await interaction.response.send_message("คุณเคยรับของรางวัลแล้ว", ephemeral = True)
        else:
            result = self.reward_random()
            if result == 'coin':
                await coins.mint_coin(user, coin, "giveaway")
                rewards = f"`{coin} IDS Coins`"
                embed.add_field(name="รางวัลที่ได้รับ", value=rewards, inline=False)
                await interaction.response.send_message(embed=embed, ephemeral = True)
            elif result == 'star citizen':
                await coins.mint_coin(user, coin, "giveaway")
                rewards = f"1. `{coin} IDS Coins`\n2. `Star Citizen Gift Card มูลค่า $10`"
                embed.add_field(name="รางวัลที่ได้รับ", value=rewards, inline=False)
                embed.set_image(url="https://robertsspaceindustries.com/media/kh65mcqfdj5j0r/slideshow/GiftCard_10Dollars_FINAL-1-Min.png")
                await interaction.response.send_message("ขอบคุณที่มาร่วมสนุกกับ IDS ยินดีด้วยนี่คือรางวัลของคุณ",embed=embed, ephemeral = True)
                await channel.send(f"<@{user.id}> got Star Citizen gift card from giveaway")
                console.log(f"{user.display_name} got Star Citizen gift card from giveaway")
            elif result == 'nitro':
                await coins.mint_coin(user, coin, "giveaway")
                with open("nitro.txt", "r") as f:
                    lines = f.readlines()
                    nitro = lines[0]
                rewards = f"1. `{coin} IDS Coins`\n2. `Discord Nitro Gift Card 1 Month มูลค่า $9.99`\n||{nitro}||"
                embed.add_field(name="รางวัลที่ได้รับ", value=rewards, inline=False)
                await interaction.response.send_message("ขอบคุณที่มาร่วมสนุกกับ IDS ยินดีด้วยนี่คือรางวัลของคุณ",embed=embed, ephemeral = True)
                await channel.send(f"<@{user.id}> got Nitro from giveaway")
                console.log(f"{user.display_name} got Nitro from giveaway")
                with open('nitro.txt', 'r+', encoding='utf-8') as txt_file:
                    lines = txt_file.readlines()
                    txt_file.seek(0)
                    if len(lines):
                        for i, line in enumerate(lines):
                            if 1 <= i:
                                txt_file.write(line)
                        txt_file.truncate()

            recipients.append(user)
    def reward_random(self):
        global reward_pool
        result = reward_pool.pop(randrange(len(reward_pool)))
        return result

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(name="giveaway", help="This command create give away post")
    async def giveaway(self, ctx):
        if ctx.author.id == 855426672806199336:
            embed = discord.Embed(
                title = "🎊 กิจกรรมฉลองครบรอบ 1 ปี 🎊",
                description = "เนื่องในโอกาสครบรอบ 1 ปี IDS discord server วันที่ 3 สิงหาคม ทีมงาน IDS มีกิจกรรมแจกของรางวัลให้สมาชิกทุกท่านดังนี้",
                color = discord.Color.dark_purple()
            )
            rewards = "1. `500 IDS Coins`\n2. `Discord Nitro Gift Card 1 Month มูลค่า $9.99` x 3 รางวัล\n3. `Star Citizen Gift Card มูลค่า $10` x 2 รางวัล"
            remark = "1. สามารถกดรับรางวัลได้คนละ 1 ครั้งเท่านั้นและกิจกรรมจะจบลงภายในวันที่ 3 สิงหาคม เวลา 23.59 น.\n2. รางวัลในข้อ 1 จะได้รับทุกคน และรางวัลในข้อ 2 และ 3 จะเป็นการสุ่ม\n3. รางวัลในข้อ 2 จะได้รับเป็นโค้ด สามารถนำไปเติมได้ในดิสคอร์ดด้วยตัวเอง\n4. ผู้ได้รับรางวัลในข้อ 3 จะต้องแจ้งอีเมลที่ใช้เล่นเกมกับแอดมินเพื่อใช้สำหรับการมอบของรางวัล\n5. ทีมงานสงวนสิทธิ์ในการแก้ไขเปลี่ยนแปลงรางวัลโดยไม่แจ้งให้ทราบล่วงหน้า\n6. รางวัลในทุกข้อไม่สามารถแลกเปลี่ยนเป็นเงินจริงได้"
            embed.add_field(name="รางวัล", value=rewards, inline=False)
            embed.add_field(name="เงื่อนไข", value=remark, inline=False)
            view=MyView(self.bot)
            message =await ctx.send("@everyone มาร่วมกิจกรรมกัน",embed =embed, view=view)
            await message.add_reaction("🎉")
            await message.add_reaction("🎊")
            await message.add_reaction("🎁")
            await message.add_reaction("🎆")
            await message.add_reaction("💰")
        else:
            await ctx.send_response("You don't have permission for this command.", ephemeral=True)

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Giveaways(bot)) # add the cog to the bot
