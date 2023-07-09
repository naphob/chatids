import os
import random
import discord
import asyncio
from gtts import gTTS
from queue import Queue
from dotenv import load_dotenv
from discord.ext import commands
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


load_dotenv()
credential = os.getenv("FIREBASE_CREDENTIALS")
cred = credentials.Certificate(credential)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ids-bot-9ac6a-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

ref = db.reference('users')
TOKEN = os.getenv("TOKEN")
TEXT_CHANNEL_ID = os.getenv("TEXT_CHANNEL_ID")
counter = 0
connections = {}
COMMAND_PREFIX = '!'
intents = discord.Intents.all()

client = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, descriptioin="IDS's discord bot assistant")

#create a queue for tts message
q = Queue()

async def noti(username, channel, message):
    tts_message = f'{username[0]} {message}'
    vc = await channel.channel.connect()
    print(tts_message)
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
            await asyncio.sleep(5)
            await vc.disconnect()
    else:
        await ctx.send(err_msg)

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')
    await client.change_presence(activity=discord.Game(name="Star Citizen"))
    for guild in client.guilds:
		# PRINT THE SERVER'S ID AND NAME.
	    print(f"- {guild.id} | {guild.name}")

async def add_coin(user,source):
    channel = await client.fetch_channel(TEXT_CHANNEL_ID)
    coin = random.random()
    if not user.bot:
        await channel.send(f"<@{user.id}> recieved {coin} IDS Coins from {source}.")
        print(f"{user.display_name} recieved {coin} IDS Coins from {source}.")
        user_coin = ref.child(f"{user.id}").child('coin').get()
        if user_coin:
            coin += user_coin
        ref.child(f"{user.id}").set({
        'coin' : coin
        })

command = ["!balance", "!say", "!send", "!rec", "!summon", "!leave", "!give", "!stop"]

@client.event
async def on_message(message):
    user = message.author
    if user.id != client.user.id and message.content not in command:
        await add_coin(user, "new message")
    await client.process_commands(message)

@client.event
async def on_raw_reaction_add(payload):
    user = await client.fetch_user(payload.user_id)
    await add_coin(user, "reaction")

@client.event
async def on_member_join(member):
    await add_coin(member, "new member")

@client.event
async def on_voice_state_update(member, before, after):
    username = member.display_name.split('[')
    if before.channel is None and after.channel is not None and not after.afk:
        # A user joined a voice channel
        message = 'เข้ามาในห้องแล้ว'
        await add_coin(member, "join vc")
        await noti(username, after, message)
    elif after.channel and not before.suppress and not before.deaf and not before.mute and not before.self_mute and not before.self_stream and not before.self_video and not before.self_deaf and not after.self_mute and not after.self_stream and not after.self_video and not after.self_deaf and not after.deaf and not after.mute and not after.suppress:
        # A user moved to another voice channel
        message = 'ย้านมาในห้องนี้แล้ว'
        await noti(username, after, message)
    elif after.channel and before.afk and not after.afk:
        # A user's back from AFK to voice channel
        message = 'กลับมาจาก AFK แล้ว'
        await noti(username, after, message)

@client.event
async def on_error(event, *args, **kwargs):
    """
    Log the errors
    """
    with open('err.log', 'a') as f:
        if event == 'on_voice_state_update':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise


@client.command(name='summon', help='This command will make the bot join the voice channel')
async def summon(ctx):
    """
    command to join voice channel
    """
    channel = ctx.author.voice.channel
    await channel.connect()

@client.command(name='leave', help='This command will make the bot leave the voice channel')
async def leave(ctx):
    """
    command to leave voice channel
    """
    vc = ctx.voice_client
    if not vc:
        await ctx.send("I am not connected to a voice channel.")
        return

    await vc.disconnect()

@client.command(name="balance", help="This command will return coins balance")
async def balance(ctx):
    user = ctx.author
    coin = ref.child(f"{user.id}").child('coin').get()
    embed = discord.Embed(
        color=discord.Color.dark_purple(),
        description= f"Balance: {coin}",
        title= f"{user.display_name}'s Wallet"
    )
    embed.set_author(name="Bank of IDS")
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/d/d6/Gold_coin_icon.png")
    if coin:
        await ctx.send(embed=embed)
        print(f"{user.id}'s balance: {coin} IDS Coins.")
    else:
        await ctx.send("You have no IDS coins")

@client.command(name="give", help="This command will return coins balance")
async def give(ctx, user: discord.Member, amount: float):
    sender = ctx.author
    receiver = user
    sender_coin = ref.child(f"{sender.id}").child('coin').get()
    receiver_coin = ref.child(f"{receiver.id}").child('coin').get()
    if sender_coin >= amount:
        remaining_coin = sender_coin - amount
        if receiver_coin:
            received_coin = receiver_coin + amount
        else:
            received_coin = amount
        ref.child(f"{sender.id}").set({
        'coin' : remaining_coin
        })
        ref.child(f"{receiver.id}").set({
        'coin' : received_coin
        })
        await ctx.send(f"<@{sender.id}> transfered {amount} IDS Coins to <@{receiver.id}>.")
        print(f"{sender.display_name} transfered {amount} IDS Coins to {receiver.display_name}.")
    else:
        await ctx.send("Insufficient IDS coin balance")

@client.command(name="rank", help="This command show richest users ranking")
async def rank(ctx):
    result = ref.order_by_child('coin').limit_to_last(10).get()
    ranks = list(result.items())
    ranks.reverse()
    leaderboard = {}
    for key, val in ranks:
        leaderboard[key] = val['coin']

    embed = discord.Embed(
        color=discord.Color.dark_purple(),
        description= "The Richest Leaderboard",
        title= "Bank of IDS"
    )
    names = ''
    for rank, user in enumerate(leaderboard):
        names += f"{rank+1}. <@{user}> : {leaderboard[user]} :coin:\n"
    embed.add_field(name="Names", value=names, inline=False)
    await ctx.send(embed=embed)

@client.command(name="say", help="This command will make the bot speak what you want in the voice channel")
async def say(ctx, *args):
    """
    Command to play voice message in the user's current voice channel
    """
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
