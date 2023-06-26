import os
import discord
import asyncio
from gtts import gTTS
from queue import Queue
from dotenv import load_dotenv
from discord.ext import commands


load_dotenv()
TOKEN = os.getenv("TOKEN")
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
    for guild in client.guilds:
		# PRINT THE SERVER'S ID AND NAME.
	    print(f"- {guild.id} (name: {guild.name})")

@client.event
async def on_voice_state_update(member, before, after):
    username = member.display_name.split('[')
    if before.channel is None and after.channel is not None and not after.afk:
        # A user joined a voice channel
        message = 'เข้ามาในห้องแล้ว'
        await noti(username[0], after, message)
    elif after.channel and not before.suppress and not before.deaf and not before.mute and not before.self_mute and not before.self_stream and not before.self_video and not before.self_deaf and not after.self_mute and not after.self_stream and not after.self_video and not after.self_deaf and not after.deaf and not after.mute and not after.suppress:
        # A user moved to another voice channel
        message = 'ย้านมาในห้องนี้แล้ว'
        await noti(username[0], after, message)
    elif after.channel and before.afk and not after.afk:
        # A user's back from AFK to voice channel
        message = 'กลับมาจาก AFK แล้ว'
        await noti(username[0], after, message)

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
    await tts_vc(ctx, user, message, err_msg)

client.run(TOKEN)
