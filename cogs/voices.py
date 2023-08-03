import random
import discord
from discord.ext import commands, bridge
import asyncio
from gtts import gTTS
from queue import Queue
from rich.console import Console

console = Console()
q = Queue()
connections = {}

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
            # put new tts message to queue
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
        if before.channel is None and after.channel is not None and not after.afk and not member.bot:
            # A user joined a voice channel
            message = 'เข้ามาในห้องแล้ว'
            await self.noti(member, after, message)
            coins = self.bot.get_cog('Coins')
            coin = random.random()
            await coins.mint_coin(member, coin, "joining vc")
        elif after.channel and not before.suppress and not before.deaf and not before.mute and not before.self_mute and not before.self_stream and not before.self_video and not before.self_deaf and not after.self_mute and not after.self_stream and not after.self_video and not after.self_deaf and not after.deaf and not after.mute and not after.suppress and not member.bot:
            # A user moved to another voice channel
            message = 'ย้ายมาในห้องนี้แล้ว'
            await self.noti(member, after, message)
        elif after.channel and before.afk and not after.afk and not member.bot:
            # A user's back from AFK to voice channel
            message = 'กลับมาจาก AFK แล้ว'
            await self.noti(member, after, message)
        elif after.channel is None and before.channel is not None and not member.bot:
            # A user left the voice channel
            message = 'ออกห้องไปแล้ว'
            await self.noti(member, before, message)

    @bridge.bridge_command(name='summon', help='This command will make the bot join the voice channel')
    async def summon(self, ctx):
        """
        command to join voice channel
        """
        if not ctx.author.voice:
            await ctx.respond(f"{ctx.author.display_name} is not connected to a voice channel")
            return
        else:
            channel = ctx.author.voice.channel
        await channel.connect()

    @bridge.bridge_command(name='leave', help='This command will make the bot leave the voice channel')
    async def leave(self, ctx):
        """
        command to leave voice channel
        """
        vc = ctx.voice_client
        if not vc:
            await ctx.respond("I am not connected to a voice channel.")
            return

        await vc.disconnect()

    @bridge.bridge_command(name="say", help="This command will make the bot speak what you want in the voice channel")
    async def say(self, ctx, *args):
        """
        Command to play voice message in the user's current voice channel
        """
        user = ctx.message.author
        username = user.display_name.split('[')
        message = f'{username[0]} พูดว่า {args}'
        err_msg = 'You are not in a voice channel.'
        await self.tts_vc(ctx, user, message, err_msg)


    @bridge.bridge_command(name="send", help="This command will send voice message to mentioned user connected to voice channel")
    async def send(self, ctx, member: discord.Member, *args):
        user = ctx.message.author
        username = user.display_name.split('[')
        message = f'{username[0]} ฝากบอกว่า {args}'
        err_msg = 'Receiver is not in a voice channel.'
        await self.tts_vc(ctx, member, message, err_msg)

    @bridge.bridge_command(name="rec", help="This command will record your voice message then send it to targeted user after stop recording")
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

    @bridge.bridge_command(name="stop_rec", help="This command will stop recording your voice message")
    async def stop_rec(self, ctx):
        if ctx.guild.id in connections:  # Check if the guild is in the cache.
            vc = connections[ctx.guild.id]
            vc.stop_recording()  # Stop recording, and call the callback (once_done).
            del connections[ctx.guild.id]  # Remove the guild from the cache.

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Voices(bot)) # add the cog to the bot
