import time
import discord
from dotenv import load_dotenv
from discord.ext import commands
from rich.console import Console
from firebase_admin import db



class Playtime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user = db.reference('users')
        self.console = Console()

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
         if before.activity != after.activity:
            if after.activity and after.activity.name == "Star Citizen":
                # record the start time when the user starts playing Star Citizen
                user_id = str(after.id)
                start_time = time.time()
                user_ref = self.user.child(f"{user_id}")
                user_ref.set({'start_time': start_time, 'total_time': user_ref.get().get('total_time', 0)})
                self.console.log(f"{after.display_name} started playing Star Citizen!")
            elif before.activity and before.activity.name == "Star Citizen" and (not after.activity or after.activity.name != "Star Citizen"):
                # record the stop time and calculate the play time
                user_id = str(before.id)
                user_ref = self.user.child(f"{user_id}")
                if 'start_time' in user_ref.get():
                    start_time = user_ref.get()['start_time']
                    play_time = time.time() - start_time
                    total_time = user_ref.get()['total_time'] + play_time
                    user_ref.update({'total_time': total_time})
                    user_ref.update({'start_time': None})
                    self.console.log(f"{before.display_name} stopped playing Star Citizen. Total time played: {play_time / 3600:.2f} hours.")

    @discord.slash_command(name='leaderboard', description='Show the leaderboard for Star Citizen playtime.')
    async def leaderboard(self, ctx):
        result = self.user.order_by_child('total_time').limit_to_last(10).get()
        if not result:
            await ctx.send_response("No playtime data available.", ephemeral=True)
            return
        else:
            ranks = list(result.items())
            ranks.reverse()

        embed = discord.Embed(
            color=discord.Color.dark_purple(),
            title= "This Week Star Citizen Leaderboard"
        )
        embed.set_author(name="🎉IDS🎉Invicta Corporation", icon_url="https://cdn.discordapp.com/attachments/1298700318179070033/1302313032554254360/IDS-01.png?ex=67547c06&is=67532a86&hm=83aa5b35dcec1b9346378b8f7d535dc787ab8fcf2f49befd4484749fbcdaf666&")
        name =''
        for i, (user_id, data) in enumerate(ranks):
            user = ctx.guild.get_member(int(user_id))
            if user is None:
                continue
            total_time = data.get('total_time', 0)
            total_time = total_time if total_time else 0
            hours_played = total_time / 3600
            name += f"{i}. {user.display_name} : {hours_played:.2f} hours\n"

        embed.add_field(name="Names", value=name, inline=False)
        embed.set_footer(text="ข้อมูลขั่วโมงการเล่นเกมจะถูกรีเซ็ตทุกสัปดาห์", icon_url="https://cdn-icons-png.flaticon.com/512/4201/4201973.png")

        await ctx.respond(embed=embed)

def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(Playtime(bot))  # add the cog to the bot
