import os
import re
import discord
import discord.ui
from discord.ext import commands
from dotenv import load_dotenv
from rich.console import Console
from PIL import Image, ImageFont, ImageDraw

console = Console()
load_dotenv()

WELCOME_CHANNEL_ID = 1037740797518430308

class infoModal(discord.ui.Modal):
    def __init__(self, bot, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot

        self.add_item(discord.ui.InputText(label="ชื่อเล่นของคุณ",placeholder="เช่น Poon", style=discord.InputTextStyle.short))
        self.add_item(discord.ui.InputText(label="ชื่อในเกม", placeholder="หากยังไม่เคยเล่นเกมให้ใส่เลข 1", style=discord.InputTextStyle.short))
    
    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        role = 1124564123640942673
        new_member_role = 1177195777278361670
        nickname = self.children[0].value
        inGameName = self.children[1].value
        if role in [r.id for r in user.roles]:
            await interaction.response.send_message(f"คุณมียศนี้อยู่แล้ว", ephemeral = True)
        else:
            await user.add_roles(user.guild.get_role(role))
            if inGameName == "1":
                await user.edit(nick=f"{nickname} [???]")
            else:
                await user.edit(nick=f"{nickname} [{inGameName}]")
            await interaction.response.send_message("ชื่อของคุณได้ถูกเปลี่ยนแล้ว คุณจะเห็นห้องทั้งหมดที่เกี่ยวข้องกับ Star Citizen", ephemeral = True)
        if new_member_role in [r.id for r in user.roles]:
            await user.remove_roles(user.guild.get_role(new_member_role))


class Roles(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    # @discord.ui.button(label="Star Citizen", custom_id="role 1", style=discord.ButtonStyle.primary, emoji="🚀")
    # async def button_callback(self, button, interaction):
    #     role = 1124564123640942673
    #     user = interaction.user
    #     regex = "^(\W|\w)+\[(\w|\W)+\]$"
    #     match = re.match(regex, user.display_name)
    #     button.disabled = True
    #     if role in [r.id for r in user.roles]:
    #         button.disabled = True
    #     else:
    #         if match:
    #             await user.add_roles(user.guild.get_role(role))
    #             await interaction.response.send_message("คุณได้รับยศแล้ว ขอให้สนุกกับการเล่น Star Citizen", ephemeral = True)
    #             console.log(f"Add role {user.guild.get_role(role).name} to {user.display_name}")
    #             new_face = 1045127837989994568
    #             await user.remove_roles(user.guild.get_role(new_face))
    #             console.log(f"Remove role {user.guild.get_role(role).name} from {user.display_name}")
    #         else:
    #             await interaction.response.send_message("กรุณาเปลี่ยนชื่อให้ถูกต้องตามกฎ เช่น Poon [CaptainWolffe]", ephemeral = True)

    # @discord.ui.button(label="เกมอื่นๆ", custom_id="role 2", style=discord.ButtonStyle.success, emoji="🎮")
    # async def button_callback_guest(self, button, interaction):
    #     role = 1092322716415172658
    #     user = interaction.user
    #     regex = "^(\W|\w)+\[(\w|\W)+\]$"
    #     match = re.match(regex, user.display_name)
    #     button.disabled = True
    #     if role in [r.id for r in user.roles]:
    #         button.disabled = True
    #     else:
    #         if match:
    #             await user.add_roles(user.guild.get_role(role))
    #             await interaction.response.send_message("คุณได้รับยศแล้ว ขอให้สนุกกับการเล่นเกมกับพวกเรา", ephemeral = True)
    #             console.log(f"Add role {user.guild.get_role(role).name} to {user.display_name}")
    #             new_face = 1045127837989994568
    #             await user.remove_roles(user.guild.get_role(new_face))
    #             console.log(f"Remove {user.guild.get_role(role).name} role from {user.display_name}")
    #         else:
    #             await interaction.response.send_message("กรุณาเปลี่ยนชื่อให้ถูกต้องตามกฎ เช่น Poon [CaptainWolffe]", ephemeral = True)
        
    @discord.ui.button(label="ยอมรับกฎเพื่อแสดงห้องทั้งหมด", custom_id="register", style=discord.ButtonStyle.primary)
    async def button_callback_guest(self, interaction):
        role = 1124564123640942673
        user = interaction.user
        modal = infoModal(self.bot, title="แจ้งข้อมูลเพื่อแสดงห้องทั้งหมด")
        if role in [r.id for r in user.roles]:
            await interaction.response.send_message(f"คุณมียศนี้อยู่แล้ว", ephemeral = True)
        else:   
            await interaction.response.send_modal(modal)

class GetRoles(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def get_role(self, role, user, interaction):
        if role in [r.id for r in user.roles]:
            await user.remove_roles(user.guild.get_role(role))
            await interaction.response.send_message(f"คุณได้คืนยศ {user.guild.get_role(role).name} แล้ว", ephemeral = True)
            console.log(f"Remove role {user.guild.get_role(role).name} from {user.display_name}")
        else:
            await user.add_roles(user.guild.get_role(role))
            await interaction.response.send_message(f"คุณได้รับยศ {user.guild.get_role(role).name} แล้ว ขอให้สนุกกับการเล่น Star Citizen", ephemeral = True)
            console.log(f"Add role {user.guild.get_role(role).name} to {user.display_name}")

    @discord.ui.button(label="Miner", custom_id="miner", style=discord.ButtonStyle.primary, emoji="⛏️")
    async def miner_button_callback(self, button, interaction):
        role = 1004496745700540427
        user = interaction.user
        await self.get_role(role, user, interaction)

    @discord.ui.button(label="Special Forces", custom_id="sf", style=discord.ButtonStyle.primary, emoji="🥷")
    async def sf_button_callback(self, button, interaction):
        role = 1004495350977011782
        user = interaction.user
        await self.get_role(role, user, interaction)

    @discord.ui.button(label="Crew", custom_id="crew", style=discord.ButtonStyle.primary, emoji="🧑‍🚀")
    async def crew_button_callback(self, button, interaction):
        role = 1013177318686081166
        user = interaction.user
        await self.get_role(role, user, interaction)

    @discord.ui.button(label="Trader", custom_id="trader", style=discord.ButtonStyle.primary, emoji="💰")
    async def trader_button_callback(self, button, interaction):
        role = 1008637643866783814
        user = interaction.user
        await self.get_role(role, user, interaction)

    @discord.ui.button(label="Medic", custom_id="medic", style=discord.ButtonStyle.primary, emoji="⛑️")
    async def medic_button_callback(self, button, interaction):
        role = 1134438399957270569
        user = interaction.user
        await self.get_role(role, user, interaction)

    @discord.ui.button(label="Engineer", custom_id="engineer", style=discord.ButtonStyle.primary, emoji="🔧")
    async def engineer_button_callback(self, button, interaction):
        role = 1134437490040766515
        user = interaction.user
        await self.get_role(role, user, interaction)

    @discord.ui.button(label="Pilot", custom_id="pilot", style=discord.ButtonStyle.primary, emoji="🛩️")
    async def pilot_button_callback(self, button, interaction):
        role = 1134438658829729833
        user = interaction.user
        await self.get_role(role, user, interaction)

    @discord.ui.button(label="Salvager", custom_id="salvager", style=discord.ButtonStyle.primary, emoji="🦺")
    async def salvager_button_callback(self, button, interaction):
        role = 1144626015168106577
        user = interaction.user
        await self.get_role(role, user, interaction)

class Welcomes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def welcome_pic(self, user):
        channel = await self.bot.fetch_channel(WELCOME_CHANNEL_ID)
        await user.display_avatar.save('Asset/avatar.png')
        avatar = Image.open('Asset/avatar.png')
        count = user.guild.member_count
        username = user.name
        text = f"Welcome {username} to IDS"
        member_text = f"Member #{count}"
        img =Image.open("Asset/ids_bg.png")
        W, H = img.size
        avatar = Image.open("Asset/avatar.png")
        size = (240, 240)
        avatar = avatar.resize(size, Image.Resampling.LANCZOS)
        mask_img = Image.new("L", avatar.size, 0)
        mask_draw = ImageDraw.Draw(mask_img)
        mask_draw.ellipse((0, 0) + avatar.size, fill=255)
        mask_img.save("Asset/mask_circle.jpg", quality=95)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 50)
        count_font = ImageFont.truetype("arial.ttf", 32)

        img.paste(avatar ,(440, 80), mask_img)
        text_size =draw.textlength(text, font=font)
        count_size =draw.textlength(member_text, font=count_font)
        draw.text(((W-text_size)/ 2, 340), text, fill=(255, 255, 255, 255), font=font, aligh="center")
        draw.text(((W-count_size)/ 2, 400), member_text, fill="grey", font=count_font, aligh="center")
        img.save('Asset/text.png')

        embed = discord.Embed(
            title = "Welcome to the verse",
            description=f"ยินดีต้อนรับคุณ <@{user.id}>  สู่ Invicta Defense Service!",
            color=discord.Color.dark_purple()
        )
        rule = "1. เปลี่ยนชื่อ : `ชื่อเล่น [ชื่อในเกม]`\nตัวอย่างการเปลี่ยนชื่อ : `Poon [CaptainWolffe]`\n2. กดรับยศเพื่อเห็นห้องของเกมที่จะเล่น"
        embed.add_field(name="__รับยศได้ด้วยตัวเอง__", value=rule, inline=False)

        embed.add_field(name="__ขอยศจากแอดมิน__", value="พิมพ์แจ้งในห้องนี้",inline=False)

        await channel.send(embed=embed, file= discord.File('Asset/text.png'), view=Roles())

    # @commands.Cog.listener()
    # async def on_member_join(self, member):
    #     role = 1045127837989994568 #give new_face role to new joiner so they can see welcome chanel
    #     await member.add_roles(member.guild.get_role(role))
    #     await self.welcome_pic(member)

    @discord.slash_command(name="welcome", description="Welcome new member")
    async def welcome(self,ctx, user: discord.Member):
        await self.welcome_pic(user)

    @discord.slash_command(name="role", description="Select a role")
    async def role(self, ctx):
        embed = discord.Embed(
                title = "Welcome to the verse",
                description=f"เลือก Role ที่เหมาะสมกับคุณ เพื่อใช้ในการสื่อสารภายในดิสคอร์ด",
                color=discord.Color.dark_purple()
            )

        await ctx.respond(embed=embed, view=Roles())
    
    @discord.slash_command(name="reg", description="Create a register button")
    @commands.has_any_role(1008638970911002684, 1037741810749030511, 1123808015536111616)
    async def reg(self, ctx):
        embed = discord.Embed(
                title = "📜      กฏการอยู่ร่วมกัน     📜",
                description="1.ที่นี่มีกฏการตั้งชื่อชัดเจน เพื่อความสะดวกในการสื่อสาร กรุณาเปลี่ยนตามรูปแบบ\n2.ไม่จำกัดการใช้คำพูดในการสนทนาแค่รู้จักให้เกียรติผู้อื่นพอ อย่าลามปามจนเกินควร\n3.การพูดคุยประเด็นละเอียดอ่อน ขอให้คำนึงถึงความรู้สึกของผู้อื่นก่อนเปิดประเด็นการสนทนา หากมีรายงานที่ไม่เหมาะสมเข้ามาแอดมินจะไม่ปล่อยไว้\n4.การสนทนาประเด็น สถาบัน ไปคุยกันที่อื่น ที่นี่ไม่หาร\n5.พฤติกรรม Toxic และ คุกคาม ทุกประเภทจะไม่ได้รับการต้อนรับจากที่นี่ หากมีการรายงานทางแอดมินจะไม่ปราณี\n6.ขอความร่วมมือในการอยู่ให้ถูกห้องตามกิจกรรมที่ทำ และโพสต์ข้อความให้ถูกห้องด้วยเพื่อความเป็นระเบียบ\n7.Spam = Ban\n8.No NSFW\n9.ที่นี่ไม่สนับสนุน FiveM, RedM เล่นเงียบ ๆ ไม่ว่า แต่จะสตรีมเชิญที่อื่น\n10.ซื้อ-ขาย ไอดีเกม ไปทำที่อื่น\n11.ไม่ต้องมาขายของที่นี่ แอดมินไม่อยากต้องมาไกล่เกลี่ยเวลามีปัญหากัน\n12.การพนันมันผิดกฏหมาย ไม่ต้องมาเล่น/มาชวนที่นี่ ห้อง IDS LAS VEGAS เป็น Mini Game ที่แอดมินท่านนึงทำไว้อยากเล่น\nเล่นได้เพื่อความบันเทิง ไม่มีรางวัลให้\n13.บุหรี่ไฟฟ้า, กัญชา, กระท่อม ป็นวัตถุต้องห้ามที่นี่ ไม่ต้องมาโฆษณาสรรพคุณ\n14.การลงทุนมีความเสี่ยง ไม่ต้องมาเป็นกูรูแถวนี้ จะเป็นไปเป็นที่อื่น\n15.ที่นี่ซีเรียสเรื่องลิขสิทธิ์ จะแชร์ จะส่งอะไรไปหลังไมค์กันเอง ไม่ต้องมาลงที่นี่\n16.มีปัญหารำคาญใครแจ้งแอดมินได้ จะขึ้นบัญชีไว้ ถ้าเจอรายงานบ่อย ๆ เดี๋ยวเขาก็หายไป\n17.ร้องเรียนใครมีหลักฐานมาด้วย แอดมินไม่ดำเนินการมั่วซั่ว\n18.Content Creator แชร์งานตัวเองได้ไม่ว่า อย่าให้รบกวนคนอื่นเกินไปเป็นพอ\n\nด้วยความปรารถนาดีจากทีมงาน",
                color=discord.Color.dark_purple()
            )

        await ctx.send(embed=embed, view=Roles(self.bot))
        await ctx.respond("สร้างข้อความที่ต้องการแล้ว", ephemeral = True)
    
    @reg.error
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.respond("คุณไม่สิทธิ์ใช้คำสั่งนี้!", ephemeral = True)
        else:
            raise error  # Here we raise other errors to ensure they aren't ignored

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Welcomes(bot)) # add the cog to the bot
