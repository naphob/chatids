import os
import secrets
import discord
from dotenv import load_dotenv
from discord.ext import commands
from rich.console import Console
from firebase_admin import db
from starcitizenapi import __main__

load_dotenv()
api_key = os.getenv("API_KEY")
Client = __main__.Client(api_key)
console = Console()

async def search_user(rsi_handle: str):
        """Search for a user by RSI handle."""
        try:
            user_data = await Client.get_user(rsi_handle) 
            if user_data.success == 1:
                return user_data.data
            else:
                console.log(f"Error: User data for {rsi_handle} not found.")
                return None
        except Exception as e:
            console.log(f"An error occurred while searching for user {rsi_handle}: {e}")
            return None

class VerificationView(discord.ui.View):
    def __init__(self, bot, user_id,rsi_handle: str):
        super().__init__(timeout=None)  # Set timeout to None for persistent view
        self.bot = bot
        self.user_id = user_id
        self.rsi_handle = rsi_handle

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green)
    async def verify_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = 1298490370845577237
        user = interaction.user
        rsi_data = await search_user(self.rsi_handle) 
        user_ref = db.reference('users')
        user_data = user_ref.child(str(self.user_id)).get()

        if user_data and user_data.get('verify_code') == rsi_data.profile.bio:
            # Update the user's verification status
            user_ref.child(str(self.user_id)).update({
                'verified': True,
                'verify_code': None  # Clear the verification code after successful verification
            })
            await user.add_roles(user.guild.get_role(role))
            await interaction.response.send_message(f"Your RSI handle `{self.rsi_handle}` has been successfully verified!", ephemeral=True)
        elif user_data.get('verified'):
            await interaction.response.send_message("ไอดีของคุณเคยได้รับการยืนยันแล้ว", ephemeral=True)
        else:
            await interaction.response.send_message("Verification failed. Please try again.", ephemeral=True)

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.console = Console()
        self.user_ref = db.reference('users')

    async def search_user(self, rsi_handle: str):
        """Search for a user by RSI handle."""
        try:
            user_data = await Client.get_user(rsi_handle)  # ใช้ await กับ async function
            if user_data.success == 1:
                return user_data.data
            else:
                self.console.log(f"Error: User data for {rsi_handle} not found.")
                return None
        except Exception as e:
            self.console.log(f"An error occurred while searching for user {rsi_handle}: {e}")
            return None

    @discord.slash_command(name='verify', description='Verify your RSI handle.')
    async def verify(self, ctx, rsi_handle: str):
        user_id = str(ctx.author.id)
        user_data = await self.search_user(rsi_handle)
        verify_code = secrets.token_hex(16)
        if self.user_ref.child(user_id).get().get('verified'):
            await ctx.send_response("ไอดีของคุณเคยได้รับการยืนยันแล้ว", ephemeral=True)
            return
        elif user_data is None:
            await ctx.send_response(f"Failed to verify RSI handle {rsi_handle}", ephemeral=True)
            return
        else:
            self.console.log(user_data.profile.display)

        #Store the verified RSI handle in the database
        self.user_ref.child(user_id).update({
            'rsi_handle': rsi_handle,
            'verified': False,
            'verify_code': verify_code
        })
        

        embed = discord.Embed(
            title="ยืนยันไอดี Star Citizen ของคุณ",
            description=f"กรุณาล็อคอินไอดีของคุณที่ robertsspaceindustries.com และกรอก Verification Code \n```{verify_code}```\nในช่อง Short Bio\nหลังจากนั้นให้กดปุ่ม Verify เพื่อยืนยันตัวตนของคุณ",
            color=discord.Color.dark_purple()
        )

        await ctx.send_response(embed=embed, view=VerificationView(self.bot, user_id, rsi_handle), ephemeral=True)
        self.console.log(f"{ctx.author.display_name} has requested for verification code with RSI handle: {rsi_handle}")

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Verification(bot)) # add the cog to the bot