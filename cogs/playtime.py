import time
import discord
import pytz
from datetime import datetime, timedelta
import asyncio
from discord.ext import commands, tasks
from rich.console import Console
from firebase_admin import db


class Playtime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user = db.reference('users')
        self.console = Console()
        self.reset_leaderboard_loop.start()

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if before.activity != after.activity:
            if after.activity and after.activity.name == "Star Citizen":
                # record the start time when the user starts playing Star Citizen
                user_id = str(after.id)
                start_time = time.time()
                user_ref = self.user.child(f"{user_id}")

                # Initialize the user data if it's the first time they play
                user_data = user_ref.get()
                if user_data is None:
                    user_ref.set({'start_time': start_time, 'total_time': 0})
                else:
                    user_ref.update({'start_time': start_time, 'total_time': user_data.get('total_time', 0)})

                self.console.log(f"{after.display_name} started playing Star Citizen!")

        elif before.activity and before.activity.name == "Star Citizen" and (not after.activity or after.activity.name != "Star Citizen"):
            # record the stop time and calculate the play time
            user_id = str(before.id)
            user_ref = self.user.child(f"{user_id}")

            # Get user data from Firebase
            user_data = user_ref.get()

            if user_data and 'start_time' in user_data:
                start_time = user_data['start_time']
                play_time = time.time() - start_time
                total_time = user_data.get('total_time', 0) + play_time

                # Update total_time and clear start_time
                user_ref.update({'total_time': total_time, 'start_time': None})
                self.console.log(f"{before.display_name} stopped playing Star Citizen. Total time played: {play_time / 3600:.2f} hours.")
            else:
                self.console.log(f"{before.display_name} stopped playing Star Citizen, but no start_time found.")

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
            # If user is None, skip this user
            if user is None:
                continue
            total_time = data.get('total_time', 0)
            # If total_time is None or 0, skip this user
            if total_time is None or total_time == 0:
                continue

            hours_played = total_time / 3600
            name += f"{i}. {user.display_name} : {hours_played:.2f} hours\n"

        embed.add_field(name="Names", value=name, inline=False)
        embed.set_footer(text=f"ข้อมูลขั่วโมงการเล่นเกมจะถูกรีเซ็ตอีกครั้งในวันที่ {self.calculate_next_reset_time().strftime('%Y-%m-%d %H:%M:%S')} (GMT+7)", icon_url="https://cdn-icons-png.flaticon.com/512/4201/4201973.png")

        await ctx.respond(embed=embed)

    # calculate the next reset time for the leaderboard
    def calculate_next_reset_time(self):
        # switch to the timezone of Bangkok
        tz = pytz.timezone('Asia/Bangkok')
        now = datetime.now(tz)

        # calculate the next reset time
        next_reset_time = now + timedelta(days=(6 - now.weekday()))  # finding the next Sunday
        next_reset_time = next_reset_time.replace(hour=23, minute=59, second=59, microsecond=0)  # setting time to 11:59 PM

        # if the current time is past the next reset time, set it to the next week
        if now > next_reset_time:
            next_reset_time += timedelta(weeks=1)

        return next_reset_time

    @tasks.loop(hours=168)  #excute every 168 hours (1 week)
    async def reset_leaderboard_loop(self):
        # calculate the next reset time
        next_reset_time = self.calculate_next_reset_time()

        # calculate the time until the next reset
        time_until_reset = next_reset_time - datetime.now(pytz.timezone('Asia/Bangkok'))
        self.console.log(f"Next reset will occur at {next_reset_time} (GMT+7)")

        # wait until the reset time
        await asyncio.sleep(time_until_reset.total_seconds())  # wait until the reset time

        # reset the leaderboard
        leaderboard_ref = db.reference('users')  # find the database that stores player playtime

        # remove total_time for all users
        users_data = leaderboard_ref.get()  # get all user data
        for user_id, data in users_data.items():
            if 'total_time' in data:
                user_ref = leaderboard_ref.child(user_id)
                user_ref.child('total_time').delete()  # remove total_time for user

        # send a message to the Discord channel
        channel = self.bot.get_channel(1127257320473251840)  # enter the ID of the Discord channel you want to send the message to
        await channel.send("Leaderboard has been reset for the new week! ⏰")
        self.console.log("Leaderboard has been reset for the new week! ⏰")

        # set the next loop interval (make it repeat every 1 week)
        self.reset_leaderboard_loop.change_interval(hours=168)  # set loop to run every 168 hours (1 week)

def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(Playtime(bot))  # add the cog to the bot
