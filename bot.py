import discord
from discord.ext import commands
from gtts import gTTS
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
COMMAND_PREFIX = '!'
TEXT_CHANNEL_ID = os.getenv("TEXT_CHANNEL_ID")
intents = discord.Intents.all()

client = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')
    for guild in client.guilds:
		# PRINT THE SERVER'S ID AND NAME.
	    print(f"- {guild.id} (name: {guild.name})")

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        # A user joined a voice channel
        if member.nick is not None:
            message = f'{member.nick} เข้ามาในห้องแล้ว'
        else:
            message = f'{member.name} เข้ามาในห้องแล้ว'
        vc = await after.channel.connect()
        sound = gTTS(text=message, lang="th", slow=False)
        sound.save("join.mp3")
        tts_audio_file = await discord.FFmpegOpusAudio.from_probe('join.mp3', method="fallback")
        vc.play(tts_audio_file)
        while vc.is_playing():  # Wait for the TTS audio to finish playing
            await asyncio.sleep(1)
        await vc.disconnect()
    elif after.channel and not before.suppress and not before.deaf and not before.mute and not before.self_mute and not before.self_stream and not before.self_video and not before.self_deaf and not after.self_mute and not after.self_stream and not after.self_video and not after.self_deaf and not after.deaf and not after.mute and not after.suppress:
        # A user moved to voice channel
        if member.nick is not None:
            message = f'{member.nick} ย้านมาในห้องนี้แล้ว'
        else:
            message = f'{member.name} ย้านมาในห้องนี้แล้ว'
        vc = await after.channel.connect()
        sound = gTTS(text=message, lang="th", slow=False)
        sound.save("join.mp3")
        tts_audio_file = await discord.FFmpegOpusAudio.from_probe('join.mp3', method="fallback")
        vc.play(tts_audio_file)
        while vc.is_playing():  # Wait for the TTS audio to finish playing
            await asyncio.sleep(1)
        await vc.disconnect()
    elif after.channel and before.afk:
         # A user back from AFK to voice channel
        if member.nick is not None:
            message = f'{member.nick} กลับมาจาก AFK แล้ว'
        else:
            message = f'{member.name} กลับมาจาก AFK แล้ว'
        vc = await after.channel.connect()
        sound = gTTS(text=message, lang="th", slow=False)
        sound.save("join.mp3")
        tts_audio_file = await discord.FFmpegOpusAudio.from_probe('join.mp3', method="fallback")
        vc.play(tts_audio_file)
        while vc.is_playing():  # Wait for the TTS audio to finish playing
            await asyncio.sleep(1)
        await vc.disconnect()

    # notify user join voice channel to specific text channel
    # text_channel = client.get_channel(TEXT_CHANNEL_ID)
    # if text_channel is not None:
    #     command = f'{COMMAND_PREFIX}join'
    #     await text_channel.send(f'{member.name} joined voice channel {after.channel.mention}.')

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

# Command to play the join sound in the user's current voice channel
@client.command(name="speak", help="This command will make the bot speak example setence in the voice channel")
async def speak(ctx):
    user = ctx.message.author
    if user.voice is not None:
        try:
            vc = await user.voice.channel.connect()
        except:
            vc = ctx.voice_client

        sound = gTTS(text="This is a tts message", lang="en", slow=False)
        sound.save("tts.mp3")

        if vc.is_playing():
            vc.stop()

        source = discord.FFmpegOpusAudio.from_probe("tts.mp3", method="fallback")
        vc.play(source)
    else:
        await ctx.send("You are not in a voice channel.")


client.run(TOKEN)


