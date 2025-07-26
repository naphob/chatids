import discord
import discord.ui
from discord.ext import commands

class AnnouceModal(discord.ui.Modal):
    def __init__(self, bot, channel: discord.TextChannel, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, timeout=None)
        self.bot = bot
        self.channel = channel

        self.add_item(discord.ui.InputText(label="หัวข้อ", style=discord.InputTextStyle.short))
        # self.add_item(discord.ui.InputText(label="รายละเอียดหัวข้อ", style=discord.InputTextStyle.short, required=False))
        # self.add_item(discord.ui.InputText(label="หัวข้อย่อย", style=discord.InputTextStyle.short, required=False))
        
        self.add_item(discord.ui.InputText(label="ลิงค์รูปแบนเนอร์", style=discord.InputTextStyle.short, placeholder="https://example.com/link-to-my-banner.png", required=False))
        self.add_item(discord.ui.InputText(label="เนื้อหา", style=discord.InputTextStyle.long, placeholder="จัดรูปแบบด้วย markdown"))

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
                    title=self.children[0].value,
                    description= self.children[2].value,
                    color= discord.Color.from_rgb(255, 79, 0)
        )
        # embed.add_field(name=self.children[2].value , value=self.children[3].value)
        embed.set_footer(text=f"โพสต์โดย {interaction.user.display_name}")
        embed.set_image(url=self.children[1].value)

        await self.channel.send(embed=embed)
        await interaction.response.send_message(f"ส่งประกาศไปที่ {self.channel.mention} แล้ว", ephemeral=True)

class Announces(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="announce", description="make an announcement")
    @commands.has_any_role(1008638970911002684, 1037741810749030511, 1123808015536111616)
    async def announce(self, ctx, channel:discord.TextChannel):
        modal = AnnouceModal(self.bot, channel, title="ประกาศ")
        await ctx.send_modal(modal)
    
        
    @announce.error
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.respond("คุณไม่สิทธิ์ใช้คำสั่งนี้!", ephemeral = True)
        else:
            raise error  # Here we raise other errors to ensure they aren't ignored
    
    @discord.slash_command(name="post", description="post an announcement to text channel")
    @commands.has_any_role(1008638970911002684, 1037741810749030511, 1123808015536111616)
    async def post(self, ctx):
        modal = AnnouceModal(self.bot, ctx.channel, title="ประกาศ")
        await ctx.send_modal(modal)
    
    @post.error
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.respond("คุณไม่สิทธิ์ใช้คำสั่งนี้!", ephemeral = True)
        else:
            raise error  # Here we raise other errors to ensure they aren't ignored

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Announces(bot)) # add the cog to the bot