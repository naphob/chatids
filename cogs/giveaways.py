import discord
from discord.ext import commands
import random
from rich.console import Console
from firebase_admin import db

console = Console()
LOG_TEXT_CHANNEL_ID = 1127257320473251840



class MyView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.coins = bot.get_cog('Coins')
        self.user = self.coins.get_user()
        # self.reward_pool = self.load_reward_pool()
        # self.recipients = self.load_recipients()

    def load_reward_pool(self):
        """โหลด reward_pool จาก Firebase"""
        reward_pool_ref = db.reference('giveaway/reward_pool')
        return reward_pool_ref.get()

    def load_recipients(self):
        """โหลด recipients จาก Firebase ทุกครั้ง"""
        recipients_ref = db.reference('giveaway/recipients')
        return recipients_ref.get() or []

    def update_reward_pool(self, reward_pool):
        """อัปเดต reward_pool ใน Firebase"""
        reward_pool_ref = db.reference('giveaway/reward_pool')
        reward_pool_ref.set(reward_pool)  # อัปเดต reward_pool
        console.log(f"Updated reward pool: {reward_pool}")

    def update_recipients(self, recipients):
        """อัปเดต recipients ใน Firebase"""
        recipients_ref = db.reference('giveaway/recipients')
        recipients_ref.set(recipients)  # อัปเดต recipients
        console.log(f"Updated recipients: {recipients}")

    @discord.ui.button(label="สุ่มรางวัล", custom_id="random", style=discord.ButtonStyle.primary, emoji="🎉", disabled=False)
    async def button_callback(self, button, interaction):
        channel = await self.bot.fetch_channel(LOG_TEXT_CHANNEL_ID)
        user = interaction.user
        coins = self.bot.get_cog('Coins')
        coin = 333.0
        embed = discord.Embed(
            title = "🎊 กิจกรรมฉลองครบรอบ 3 ปี IDS 🎊",
                description = "เนื่องในโอกาสครบรอบ 3 ปี IDS discord server วันที่ 3 สิงหาคม 2025 ทีมงาน IDS มีกิจกรรมแจกของรางวัลให้สมาชิกทุกท่านดังนี้",
                color = discord.Color.dark_red()
        )

        recipients = self.load_recipients()

        if user.id in recipients:
            await interaction.response.send_message("คุณเคยรับของรางวัลแล้ว", ephemeral = True)
        else:
            result = self.reward_random()
            if result == 'coin':
                await coins.mint_coin(user, coin, "giveaway")
                rewards = f"`{coin} IDS Coins`"
                embed.add_field(name="รางวัลที่ได้รับ", value=rewards, inline=False)
                await interaction.response.send_message(embed=embed, ephemeral = True)
            elif result == 'gift_card':
                await coins.mint_coin(user, coin, "giveaway")
                rewards = f"1. `{coin} IDS Coins`\n2. `Star Citizen Gift Card มูลค่า $10`"
                embed.add_field(name="รางวัลที่ได้รับ", value=rewards, inline=False)
                embed.set_image(url="https://robertsspaceindustries.com/media/kh65mcqfdj5j0r/slideshow/GiftCard_10Dollars_FINAL-1-Min.png")
                await interaction.response.send_message("ขอบคุณที่มาร่วมสนุกกับ IDS ยินดีด้วยนี่คือรางวัลของคุณ",embed=embed, ephemeral = True)
                await channel.send(f"<@{user.id}> got Star Citizen gift card from giveaway")
                await interaction.channel.send(f"🎉 ยินดีด้วย 🎉<@{user.id}> got Star Citizen gift card from giveaway")
                console.log(f"{user.display_name} got Star Citizen gift card from giveaway")
            elif result == 'miner_pack':
                await coins.mint_coin(user, coin, "giveaway")
                rewards = f"1. `{coin} IDS Coins`\n2. `Star Citizen Miner Starter Pack มูลค่า $75`"
                embed.add_field(name="รางวัลที่ได้รับ", value=rewards, inline=False)
                embed.set_image(url="https://robertsspaceindustries.com/i/b2ead2c1836d12f273851edc8cd33ea3eb7b42cf/resize(910,512,cover,ADdPNihJzmPbNuTnFsH1DqUeqBRpXdSXVVtgJTyDDgscGKrzJuoFjReseHAbaLQcuxXnjfkVH9umUvGrGRsxv5xkW)/source.webp")
                await interaction.response.send_message("ขอบคุณที่มาร่วมสนุกกับ IDS ยินดีด้วยนี่คือรางวัลของคุณ",embed=embed, ephemeral = True)
                await channel.send(f"<@{user.id}> got Star Citizen Miner Starter Pack from giveaway")
                await interaction.channel.send(f"🎉 ยินดีด้วย 🎉<@{user.id}> got Star Citizen Miner Starter Pack from giveaway")
                console.log(f"{user.display_name} got Star Citizen Miner Starter Pack from giveaway")

            recipients.append(user.id)
            self.update_recipients(recipients)  # อัปเดต recipients หลังจากที่มีการรับรางวัลแล้ว

    def reward_random(self):
        """สุ่มรางวัลโดยใช้ความน่าจะเป็น และตรวจสอบจำนวนรางวัลที่เหลือ"""
        reward_pool = self.load_reward_pool()

        reward_chances = {
            'coin': 60,
            'gift_card': 30,
            'miner_pack': 10
        }

        # ตรวจสอบว่ามีรางวัลเหลืออยู่หรือไม่
        available_rewards = {reward: chance for reward, chance in reward_chances.items() if reward_pool.get(reward, 0) > 0}

        if not available_rewards:
            return None  # ถ้าไม่มีรางวัลเหลือเลย

        # สุ่มรางวัลจากรางวัลที่เหลือ
        random_choice = random.choices(
            population=list(available_rewards.keys()),
            weights=list(available_rewards.values()),
            k=1
        )[0]

        # ลดจำนวนรางวัลที่เหลือ
        reward_pool[random_choice] -= 1
        self.update_reward_pool(reward_pool)  # อัปเดต Firebase หลังจากลดจำนวนรางวัล

        return random_choice

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="giveaway", description="This command create give away post")
    async def giveaway(self, ctx):
        if ctx.author.id == 855426672806199336:
            embed = discord.Embed(
                title = "🎊 กิจกรรมฉลองครบรอบ 3 ปี IDS 🎊",
                description = "เนื่องในโอกาสครบรอบ 3 ปี IDS discord server วันที่ 3 สิงหาคม 2025 ทีมงาน IDS มีกิจกรรมแจกของรางวัลให้สมาชิกทุกท่านดังนี้",
                color = discord.Color.dark_purple()
            )
            rewards = "1. `Star Citizen Miner Starter Pack มูลค่า $75` x 1 รางวัล\n2. `Star Citizen Gift Card มูลค่า $10` x 2 รางวัล\n3. `333 IDS Coins`"
            remark = "1. สามารถกดรับรางวัลได้คนละ 1 ครั้งเท่านั้นและกิจกรรมจะจบลงภายในวันที่ 3 สิงหาคม 2025 เวลา 23.59 น.\n2. รางวัลในข้อ 3 จะได้รับทุกคน\n3. ผู้ได้รับรางวัลในข้อ 1 และ 2 จะต้องแจ้งอีเมลที่ใช้เล่นเกมกับแอดมินเพื่อใช้สำหรับการมอบของรางวัล\n4. ทีมงานสงวนสิทธิ์ในการแก้ไขเปลี่ยนแปลงรางวัลโดยไม่แจ้งให้ทราบล่วงหน้า\n5. รางวัลในทุกข้อไม่สามารถแลกเปลี่ยนเป็นเงินจริงได้"
            embed.add_field(name="รางวัล", value=rewards, inline=False)
            embed.add_field(name="เงื่อนไข", value=remark, inline=False)
            view=MyView(self.bot)
            message =await ctx.send("@everyone มาร่วมกิจกรรมกัน",embed =embed, view=view)
            await ctx.send_response("โพสต์กิจกรรมแจกของรางวัลเรียบร้อยแล้ว", ephemeral=True)
            await message.add_reaction("🎉")
            await message.add_reaction("🎊")
            await message.add_reaction("🎁")
            await message.add_reaction("🎆")
            # await message.add_reaction("💰")
        else:
            await ctx.send_response("You don't have permission for this command.", ephemeral=True)

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Giveaways(bot)) # add the cog to the bot
