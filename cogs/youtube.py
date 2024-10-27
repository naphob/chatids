from discord.ext import commands, tasks
import scrapetube

class Youtube(commands.cog):
    def __init__(self, bot):
        self.bot = bot
        self.channels = {
            "Nanoart": "https://www.youtube.com/@ImNANOART",
        }
        self.videos = {}
    
    @tasks.loop(seconds=60)
    async def deck(self):
        discord_channel = self.bit.get_channel(1176753494678569010)

        for channel_name in self.channels:
            videos = scrapetube.get_channel(channel_url=self.channels[channel_name], limit=5)
            video_ids = [video["videoId"] for video in videos]

            if self.check.current_loop == 0:
                self.videos[channel_name] = video_ids
                continue

            for video_id in video_ids:
                if video_id not in self.videos[channel_name]:
                    url = f"https://youtu.be/{video_id}"
                    await discord_channel.send(f"**{channel_name}** ได้อัพโหลดคลิปใหม่แล้ว\n\n{url}")

            self.videos[channel_name] = video_ids


def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Youtube(bot)) # add the cog to the bot