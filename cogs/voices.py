import re
import random
import discord
from discord.ext import commands
import asyncio
from gtts import gTTS
from queue import Queue
from rich.console import Console
from discord.utils import get

console = Console()
q = Queue()
connections = {}
room_no = 0

class Voices(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def noti(self, member, channel, message):
        username = member.display_name.split('[')
        tts_message = f'{username[0]} {message}'
        if not self.bot.voice_clients:
            try:
                vc = await channel.channel.connect()
            except:
                vc = self.bot.voice_clients[0]
                print("Bot is busy in another room")
            sound = gTTS(text=tts_message, lang="th", slow=False)
            sound.save("join.mp3")
            tts_audio_file = await discord.FFmpegOpusAudio.from_probe('join.mp3', method="fallback")
            vc.play(tts_audio_file)
            while vc.is_playing():  # Wait for the TTS audio to finish playing
                await asyncio.sleep(1)
            console.log(tts_message)
            await vc.disconnect()
        else:
            console.log(f"Bot is still busy at channel {self.bot.voice_clients[0].channel}")
            await asyncio.sleep(3)
            if not self.bot.voice_clients:
                try:
                    vc = await channel.channel.connect()
                except:
                    vc = self.bot.voice_clients[0]
                    print("Bot is busy in another room")
                sound = gTTS(text=tts_message, lang="th", slow=False)
                sound.save("join.mp3")
                tts_audio_file = await discord.FFmpegOpusAudio.from_probe('join.mp3', method="fallback")
                vc.play(tts_audio_file)
                while vc.is_playing():  # Wait for the TTS audio to finish playing
                    await asyncio.sleep(1)
                console.log(tts_message)
                await vc.disconnect()

    async def tts_vc(self, ctx, user, message, err_msg):
        if user.voice is not None:
            q.put(message)
            try:
                vc = await user.voice.channel.connect()
            except:
                vc = ctx.voice_client
            while not q.empty():
                if not vc.is_playing():
                    tts_message = q.get()
                    console.log(tts_message)
                    sound = gTTS(text=tts_message, lang="th", slow=False)
                    sound.save("tts.mp3")
                    source = await discord.FFmpegOpusAudio.from_probe("tts.mp3", method="fallback")
                    vc.play(source)
                    await ctx.send(tts_message)
                    while vc.is_playing():
                        await asyncio.sleep(3)
                else:
                    await asyncio.sleep(8)
            if q.empty():
                await asyncio.sleep(3)
                await vc.disconnect()
        else:
            await ctx.respond(err_msg)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        global room_no
        regex = "🚀Gaming\s\d+$"
        if before.channel is None and after.channel is not None and not after.afk and not member.bot:
            # A user joined a voice channel
            if after.channel.id == 1147446860961816648:
                room_no += 1
                temp_channel = await after.channel.clone(name=f"🚀Gaming 0{room_no}")
                if temp_channel is not None:
                    await member.move_to(temp_channel)
            else:
                message = 'เข้ามาในห้องแล้ว'
                await self.noti(member, after, message)
                coins = self.bot.get_cog('Coins')
                coin = random.random()
                await coins.mint_coin(member, coin, "joining vc")
        elif after.channel and not before.suppress and not before.deaf and not before.mute and not before.self_mute and not before.self_stream and not before.self_video and not before.self_deaf and not after.self_mute and not after.self_stream and not after.self_video and not after.self_deaf and not after.deaf and not after.mute and not after.suppress and not member.bot:
            # A user moved to another voice channel
            match = re.match(regex, before.channel.name)
            after_match = re.match(regex, after.channel.name)
            if before.channel is not None and match :
                console.log(f"channel members before: {len(before.channel.members)}")
                if len(before.channel.members) == 0:
                    console.log(f"channel members after left channel: {len(before.channel.members)}")
                    console.log(f"{before.channel.name} is deleted")
                    await before.channel.delete()
                    room_no -= 1
            elif after.channel.id == 1147446860961816648:
                room_no += 1
                temp_channel = await after.channel.clone(name=f"🚀Gaming 0{room_no}")
                if temp_channel is not None:
                    await member.move_to(temp_channel)
            elif not after_match:
                console.log(match)
                message = 'ย้ายมาในห้องนี้แล้ว'
                await self.noti(member, after, message)
        elif before.channel is not None and after.channel is not None and not before.afk and not after.afk and not member.bot:
                message = 'ย้ายมาในห้องนี้แล้ว'
                await self.noti(member, after, message)
        elif after.channel and before.afk and not after.afk and not member.bot:
            # A user's back from AFK to voice channel
            message = 'กลับมาจาก AFK แล้ว'
            await self.noti(member, after, message)
        elif after.channel is None and before.channel is not None and not member.bot:
            # A user left the voice channel
            match = re.match(regex, before.channel.name)
            if match :
                console.log(f"channel members before: {len(before.channel.members)}")
                if len(before.channel.members) == 0:
                    console.log(f"channel members after left channel: {len(before.channel.members)}")
                    # console.log(f"{before.channel.member} left channel {before.channel.name}")
                    console.log(f"{before.channel.name} is deleted")
                    await before.channel.delete()
                    room_no -= 1
                elif len(before.channel.members) > 0 or before.channel.id != 1147446860961816648 :
                    message = 'ออกห้องไปแล้ว'
                    await self.noti(member, before, message)
                    console.log(f"channel members after left channel: {len(before.channel.members)-1}")
            elif len(before.channel.members) > 0 :
                message = 'ออกห้องไปแล้ว'
                await self.noti(member, before, message)
                console.log(f"channel members after left channel: {len(before.channel.members)-1}")

    @discord.slash_command(name='summon', description='This command will make the bot join the voice channel')
    async def summon(self, ctx):
        """
        command to join voice channel
        """
        if not ctx.author.voice:
            await ctx.send_response(f"{ctx.author.display_name} is not connected to a voice channel", ephemeral = True)
            return
        else:
            channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send_response("bot connected to a voice channel", ephemeral = True)

    @discord.slash_command(name='leave', description='This command will make the bot leave the voice channel')
    async def leave(self, ctx):
        """
        command to leave voice channel
        """
        vc = ctx.voice_client
        if not vc:
            await ctx.send_response("Bot is not connected to a voice channel.", ephemeral = True)
            return

        await vc.disconnect()
        await ctx.send_response("bot disconnected tfrom voice channel", ephemeral = True)

    @discord.slash_command(name="say", description="This command will make the bot speak what you want in the voice channel")
    async def say(self, ctx, words):
        """
        Command to play voice message in the user's current voice channel
        """
        coins = self.bot.get_cog('Coins')
        user = ctx.author
        user_balance = await coins.check_coin(user)
        await ctx.defer(ephemeral = True)
        if user_balance >= 10.0:
            await coins.deduct_coin(user, 10)
            username = user.display_name.split('[')
            message = f'{username[0]} พูดว่า {words}'
            err_msg = 'You are not in a voice channel.'
            await self.tts_vc(ctx, user, message, err_msg)
            await ctx.send_followup("คุณได้ใช้ 10 coin แล้ว ขอบคุณที่ใช้บริการน้อน", ephemeral = True)
        else:
            await ctx.send_followup("คุณมี IDS Coin ไม่พอ", ephemeral = True)

    @discord.slash_command(name="send", description="This command will send voice message to mentioned user connected to voice channel")
    async def send(self, ctx, member: discord.Member, words):
        coins = self.bot.get_cog('Coins')
        user = ctx.author
        user_balance = await coins.check_coin(user)
        await ctx.defer(ephemeral = True)
        if user_balance >= 10.0:
            username = user.display_name.split('[')
            message = f'{username[0]} ฝากบอกว่า {words}'
            err_msg = 'Receiver is not in a voice channel.'
            await self.tts_vc(ctx, member, message, err_msg)
            await ctx.send_followup("คุณได้ใช้ 10 coin แล้ว ขอบคุณที่ใช้บริการน้อน", ephemeral = True)
        else:
            await ctx.send_followup("คุณมี IDS Coin ไม่พอ", ephemeral = True)

    @discord.slash_command(name="rec", description="This command will record your voice message then send it to targeted user after stop recording")
    async def rec(self, ctx, user: discord.Member):  # If you're using commands.Bot, this will also work.
        voice = ctx.author.voice

        if not voice:
            await ctx.respond("You aren't in a voice channel!")

        vc = await voice.channel.connect()  # Connect to the voice channel the author is in.
        connections.update({ctx.guild.id: vc})  # Updating the cache with the guild and channel.

        vc.start_recording(
            discord.sinks.MP3Sink(),  # The sink type to use.
            self.once_done,  # What to do once done.
            user,  # The channel to disconnect from.
            ctx.author
        )

    async def once_done(self, sink: discord.sinks, member: discord.Member, user: discord.User, *args):
        recorded_users = [  # A list of recorded users
            f"<@{user_id}>"
            for user_id, audio in sink.audio_data.items()
        ]
        await sink.vc.disconnect()  # Disconnect from the voice channel.
        files = [discord.File(audio.file, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]  # List down the files.
        for user_id, audio in sink.audio_data.items():
            if user_id == user.id:
                with open("output.mp3", "wb") as f:
                    f.write(audio.file.getbuffer())
        vc = await member.voice.channel.connect()
        playback_voice = await discord.FFmpegOpusAudio.from_probe('output.mp3', method="fallback")

        vc.play(playback_voice)
        while vc.is_playing():
            await asyncio.sleep(10)
        await vc.disconnect()

    @discord.slash_command(name="stop_rec", description="This command will stop recording your voice message")
    async def stop_rec(self, ctx):
        if ctx.guild.id in connections:  # Check if the guild is in the cache.
            vc = connections[ctx.guild.id]
            vc.stop_recording()  # Stop recording, and call the callback (once_done).
            del connections[ctx.guild.id]  # Remove the guild from the cache.

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Voices(bot)) # add the cog to the bot
