import os
import discord
import asyncio
from gtts import gTTS
from queue import Queue
from dotenv import load_dotenv
from discord.ext import commands
import speech_recognition as sr


load_dotenv()
TOKEN = os.getenv("TOKEN")
connections = {}
COMMAND_PREFIX = '!'
intents = discord.Intents.all()

client = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)
#create a queue for tts message
q = Queue()

async def noti(username, channel, message):
    tts_message = f'{username[0]} {message}'
    vc = await channel.channel.connect()
    sound = gTTS(text=tts_message, lang="th", slow=False)
    sound.save("join.mp3")
    tts_audio_file = await discord.FFmpegOpusAudio.from_probe('join.mp3', method="fallback")
    vc.play(tts_audio_file)
    while vc.is_playing():  # Wait for the TTS audio to finish playing
        await asyncio.sleep(1)
    await vc.disconnect()

async def tts_vc(ctx, user, message, err_msg):
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
                print(tts_message)
                sound = gTTS(text=tts_message, lang="th", slow=False)
                sound.save("tts.mp3")
                source = await discord.FFmpegOpusAudio.from_probe("tts.mp3", method="fallback")
                vc.play(source)
                while vc.is_playing():
                    await asyncio.sleep(10)
            else:
                await asyncio.sleep(10)
        if q.empty():
            await asyncio.sleep(10)
            await vc.disconnect()
    else:
        await ctx.send(err_msg)

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')
    await client.change_presence(activity=discord.Game(name="Star Citizen"))
    for guild in client.guilds:
		# PRINT THE SERVER'S ID AND NAME.
	    print(f"- {guild.id} (name: {guild.name})")

@client.event
async def on_voice_state_update(member, before, after):
    username = member.display_name.split('[')
    if before.channel is None and after.channel is not None and not after.afk:
        # A user joined a voice channel
        message = 'เข้ามาในห้องแล้ว'
        await noti(username, after, message)
    elif after.channel and not before.suppress and not before.deaf and not before.mute and not before.self_mute and not before.self_stream and not before.self_video and not before.self_deaf and not after.self_mute and not after.self_stream and not after.self_video and not after.self_deaf and not after.deaf and not after.mute and not after.suppress:
        # A user moved to another voice channel
        message = 'ย้านมาในห้องนี้แล้ว'
        await noti(username, after, message)
    elif after.channel and before.afk and not after.afk:
        # A user's back from AFK to voice channel
        message = 'กลับมาจาก AFK แล้ว'
        await noti(username, after, message)

#Log the errors
@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_voice_state_update':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

#command to join voice channel
@client.command(name='summon', help='This command will make the bot join the voice channel')
async def summon(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()

#command to leave voice channel
@client.command(name='leave', help='This command will make the bot leave the voice channel')
async def leave(ctx):
    vc = ctx.voice_client
    if not vc:
        await ctx.send("I am not connected to a voice channel.")
        return

    await vc.disconnect()

# Command to play voice message in the user's current voice channel
@client.command(name="say", help="This command will make the bot speak what you want in the voice channel")
async def say(ctx, *args):
    user = ctx.message.author
    username = user.display_name.split('[')
    message = f'{username[0]} พูดว่า {args}'
    err_msg = 'You are not in a voice channel.'
    await tts_vc(ctx, user, message, err_msg)

# Command to send voice message to mentioned user in a voice channel. The sender doesn't need to connect to that voice channel
@client.command(name="send", help="This command will send voice message to mentioned user connected to voice channel")
async def send(ctx, member: discord.Member, *args):
    user = ctx.message.author
    username = user.display_name.split('[')
    message = f'{username[0]} ฝากบอกว่า {args}'
    err_msg = 'Receiver is not in a voice channel.'
    await tts_vc(ctx, member, message, err_msg)


@client.command()
async def rec(ctx, user: discord.Member):  # If you're using commands.Bot, this will also work.
    voice = ctx.author.voice

    if not voice:
        await ctx.respond("You aren't in a voice channel!")

    vc = await voice.channel.connect()  # Connect to the voice channel the author is in.
    connections.update({ctx.guild.id: vc})  # Updating the cache with the guild and channel.

    vc.start_recording(
        discord.sinks.MP3Sink(),  # The sink type to use.
        once_done,  # What to do once done.
        user,  # The channel to disconnect from.
        ctx.author
    )

async def once_done(sink: discord.sinks, member: discord.Member, user: discord.User, *args):  # Our voice client already passes these in.
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

@client.command()
async def stop(ctx):
    if ctx.guild.id in connections:  # Check if the guild is in the cache.
        vc = connections[ctx.guild.id]
        vc.stop_recording()  # Stop recording, and call the callback (once_done).
        del connections[ctx.guild.id]  # Remove the guild from the cache.

client.run(TOKEN)
