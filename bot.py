import os
import re
import random
import discord
import asyncio
import discord.ui
from gtts import gTTS
from queue import Queue
from dotenv import load_dotenv
from discord.ext import commands
from rich.console import Console
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from PIL import Image, ImageFont, ImageDraw

console = Console()
load_dotenv()
credential = os.getenv("FIREBASE_CREDENTIALS")
DB_URL = os.getenv("DB_URL")
cred = credentials.Certificate(credential)
firebase_admin.initialize_app(cred, {
    'databaseURL': DB_URL
})

ref = db.reference('users')
TOKEN = os.getenv("TOKEN")
TEXT_CHANNEL_ID = os.getenv("TEXT_CHANNEL_ID")
WELCOME_CHANNEL_ID = 1037740797518430308
counter = 0
connections = {}
COMMAND_PREFIX = '!'
intents = discord.Intents.all()

client = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, descriptioin="IDS's discord bot assistant")

#create a queue for tts message
q = Queue()

class Roles(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Star Citizen", custom_id="role 1", style=discord.ButtonStyle.primary, emoji="🚀")
    async def button_callback(self, button, interaction):
        role = 1124564123640942673
        user = interaction.user
        regex = "^(\W|\w)+\[(\w|\W)+\]$"
        match = re.match(regex, user.display_name)
        button.disabled = True
        if role in [r.id for r in user.roles]:
            button.disabled = True
        else:
            if match:
                await user.add_roles(user.guild.get_role(role))
                await interaction.response.send_message("คุณได้รับยศแล้ว ขอให้สนุกกับการเล่น Star Citizen", ephemeral = True)
                console.log(f"Add role to {user.display_name}")
                new_face = 1045127837989994568
                await user.remove_roles(user.guild.get_role(new_face))
                console.log(f"Remove role from {user.display_name}")
            else:
                await interaction.response.send_message("กรุณาเปลี่ยนชื่อให้ถูกต้องตามกฎ เช่น Poon [CaptainWolffe]", ephemeral = True)

    @discord.ui.button(label="Guest", custom_id="role 2", style=discord.ButtonStyle.primary, emoji="🙏")
    async def button_callback_guest(self, button, interaction):
        role = 1092322716415172658
        user = interaction.user
        regex = "^(\W|\w)+\[(\w|\W)+\]$"
        match = re.match(regex, user.display_name)
        button.disabled = True
        if role in [r.id for r in user.roles]:
            button.disabled = True
        else:
            if match:
                await user.add_roles(user.guild.get_role(role))
                await interaction.response.send_message("คุณได้รับยศแล้ว ขอให้สนุกกับการเล่นเกมกับพวกเรา", ephemeral = True)
                console.log(f"Add role to {user.display_name}")
                new_face = 1045127837989994568
                await user.remove_roles(user.guild.get_role(new_face))
                console.log(f"Remove role from {user.display_name}")
            else:
                await interaction.response.send_message("กรุณาเปลี่ยนชื่อให้ถูกต้องตามกฎ เช่น Poon [CaptainWolffe]", ephemeral = True)

async def noti(member, channel, message):
    username = member.display_name.split('[')
    tts_message = f'{username[0]} {message}'
    try:
        vc = await channel.channel.connect()
    except:
        vc = member.voice_client
    sound = gTTS(text=tts_message, lang="th", slow=False)
    sound.save("join.mp3")
    tts_audio_file = await discord.FFmpegOpusAudio.from_probe('join.mp3', method="fallback")
    vc.play(tts_audio_file)
    while vc.is_playing():  # Wait for the TTS audio to finish playing
        await asyncio.sleep(1)
    console.log(tts_message)
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
                console.log(tts_message)
                sound = gTTS(text=tts_message, lang="th", slow=False)
                sound.save("tts.mp3")
                source = await discord.FFmpegOpusAudio.from_probe("tts.mp3", method="fallback")
                vc.play(source)
                while vc.is_playing():
                    await asyncio.sleep(5)
            else:
                await asyncio.sleep(10)
        if q.empty():
            await asyncio.sleep(5)
            await vc.disconnect()
    else:
        await ctx.send(err_msg)

async def add_coin(user, amount,source):
    channel = await client.fetch_channel(TEXT_CHANNEL_ID)
    coin = amount
    if not user.bot:
        await channel.send(f"<@{user.id}> recieved {coin} IDS Coins from {source}.")
        console.log(f"{user.display_name} recieved {coin} IDS Coins from {source}.")
        user_coin = ref.child(f"{user.id}").child('coin').get()
        if user_coin:
            coin += user_coin
        ref.child(f"{user.id}").set({
        'coin' : coin
        })

async def welcome_pic(user):
    channel = client.get_channel(WELCOME_CHANNEL_ID)
    await user.display_avatar.save('Asset/avatar.png')
    avatar = Image.open('Asset/avatar.png')
    count = user.guild.member_count
    username = user.name
    text = f"Welcome {username} to IDS"
    member_text = f"Member #{count}"
    img =Image.open("Asset/ids_bg.png")
    W, H = img.size
    avatar = Image.open("Asset/avatar.png")
    size = (240, 240)
    avatar = avatar.resize(size, Image.Resampling.LANCZOS)
    mask_img = Image.new("L", avatar.size, 0)
    mask_draw = ImageDraw.Draw(mask_img)
    mask_draw.ellipse((0, 0) + avatar.size, fill=255)
    mask_img.save("Asset/mask_circle.jpg", quality=95)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 50)
    count_font = ImageFont.truetype("arial.ttf", 32)

    img.paste(avatar ,(440, 80), mask_img)
    text_size =draw.textlength(text, font=font)
    count_size =draw.textlength(member_text, font=count_font)
    draw.text(((W-text_size)/ 2, 340), text, fill=(255, 255, 255, 255), font=font, aligh="center")
    draw.text(((W-count_size)/ 2, 400), member_text, fill="grey", font=count_font, aligh="center")
    img.save('Asset/text.png')

    embed = discord.Embed(
        title = "Welcome to the verse",
        description=f"ยินดีต้อนรับคุณ <@{user.id}>  สู่ Intergalactic Defense Security!",
        color=discord.Color.dark_purple()
    )
    rule = "1. เปลี่ยนชื่อ : `ชื่อเล่น [ชื่อในเกม]`\nตัวอย่างการเปลี่ยนชื่อ : `Poon [CaptainWolffe]`\n2. กดรับยศเพื่อเห็นห้องที่เกี่ยวข้อง"
    embed.add_field(name="อย่าลืม!", value=rule)

    await channel.send(embed=embed, file= discord.File('Asset/text.png'), view=Roles())

@client.event
async def on_ready():
    console.log(f'{client.user.name} has connected to Discord!')
    client.add_view(Roles())
    await client.change_presence(activity=discord.Game(name="Star Citizen"))
    for guild in client.guilds:
		# PRINT THE SERVER'S ID AND NAME.
	    console.log(f"- {guild.id} | {guild.name}")


@client.event
async def on_message(message):
    bot_command = ["!balance", "!say", "!send", "!rec", "!summon", "!leave", "!give", "!stop"]
    user = message.author
    coin = random.random()
    if user.id != client.user.id and message.content not in bot_command:
        await add_coin(user, coin,"new message")
    elif message.type == discord.MessageType.premium_guild_subscription:
        await add_coin(user, 150.0,"boosted the server")
    await client.process_commands(message)

@client.event
async def on_raw_reaction_add(payload):
    user = await client.fetch_user(payload.user_id)
    coin = random.random()
    await add_coin(user, coin, "reaction")

@client.event
async def on_member_join(member):
    # coin = random.random()
    # await add_coin(member, coin, "new member")
    role = 1045127837989994568
    await member.add_roles(member.guild.get_role(role))
    await welcome_pic(member)

@client.event
async def on_voice_state_update(member, before, after):
    # username = member.display_name.split('[')
    if before.channel is None and after.channel is not None and not after.afk and not member.bot:
        # A user joined a voice channel
        message = 'เข้ามาในห้องแล้ว'
        await noti(member, after, message)
        coin = random.random()
        await add_coin(member, coin, "join vc")
    elif after.channel and not before.suppress and not before.deaf and not before.mute and not before.self_mute and not before.self_stream and not before.self_video and not before.self_deaf and not after.self_mute and not after.self_stream and not after.self_video and not after.self_deaf and not after.deaf and not after.mute and not after.suppress and not member.bot:
        # A user moved to another voice channel
        message = 'ย้านมาในห้องนี้แล้ว'
        await noti(member, after, message)
    elif after.channel and before.afk and not after.afk and not member.bot:
        # A user's back from AFK to voice channel
        message = 'กลับมาจาก AFK แล้ว'
        await noti(member, after, message)

# @client.event
# async def on_error(event, *args, **kwargs):
#     """
#     Log the errors
#     """
#     with open('err.log', 'a') as f:
#         if event == 'on_voice_state_update':
#             f.write(f'Unhandled message: {args[0]}\n')
#         else:
#             raise


@client.command(name='summon', help='This command will make the bot join the voice channel')
async def summon(ctx):
    """
    command to join voice channel
    """
    if not ctx.author.voice:
        await ctx.send(f"{ctx.author.display_name} is not connected to a voice channel")
        return
    else:
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
        description= f"Balance: `{coin}`",
        title= f"{user.display_name}'s Wallet"
    )
    embed.set_author(name="Bank of IDS")
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/d/d6/Gold_coin_icon.png")
    if coin:
        await ctx.send(embed=embed)
        console.log(f"{user.id}'s balance: {coin} IDS Coins.")
    else:
        await ctx.send("You have no IDS coins")

@client.command(name="give", help="This command will return coins balance")
async def give(ctx, user: discord.Member, amount: float):
    channel = await client.fetch_channel(TEXT_CHANNEL_ID)
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

        embed = discord.Embed(
        color=discord.Color.dark_purple(),
        title= f"Bank of IDS",
        description= f"IDS Coin Transfer Transaction"
        )

        embed.add_field(name="Sender", value=sender.display_name, inline=True)
        embed.add_field(name=":arrow_right:", value=f"`{amount}`", inline=True)
        embed.add_field(name="Recipient", value=receiver.display_name, inline=True)

        # await ctx.send(f"<@{sender.id}> transfered {amount} IDS Coins to <@{receiver.id}>.")
        await ctx.send(embed=embed)
        await channel.send(f"<@{sender.id}> transfered {amount} IDS Coins to <@{receiver.id}>.")
        console.log(f"{sender.display_name} transfered {amount} IDS Coins to {receiver.display_name}.")
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
        if rank+1 == 1:
            rank =":first_place:"
        elif rank+1 == 2:
            rank =":second_place:"
        elif rank+1 == 3:
            rank =":third_place:"
        else:
            rank = rank+1
        names += f"{rank}. <@{user}> : {leaderboard[user]} :coin:\n"
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

@client.command(name="welcome", help="Welcome new member")
async def welcome(ctx, user: discord.Member):
    # await ctx.author.display_avatar.save('Asset/avatar.png')
    # avatar = Image.open('Asset/avatar.png')
    # count = ctx.guild.member_count
    # username = ctx.author.name
    # text = f"Welcome {username} to IDS"
    # member_text = f"Member #{count}"
    # img =Image.open("Asset/ids_bg.png")
    # W, H = img.size
    # avatar = Image.open("Asset/avatar.png")

    # mask_img = Image.new("L", avatar.size, 0)
    # mask_draw = ImageDraw.Draw(mask_img)
    # mask_draw.ellipse((0, 0) + avatar.size, fill=255)
    # mask_img.save("Asset/mask_circle.jpg", quality=95)

    # draw = ImageDraw.Draw(img)
    # font = ImageFont.truetype("arial.ttf", 50)
    # count_font = ImageFont.truetype("arial.ttf", 32)
    # img.paste(avatar ,(400, 50), mask_img)
    # text_size =draw.textlength(text, font=font)
    # count_size =draw.textlength(member_text, font=count_font)
    # draw.text(((W-text_size)/ 2, 340), text, fill=(255, 255, 255, 255), font=font, aligh="center")
    # draw.text(((W-count_size)/ 2, 400), member_text, fill="grey", font=count_font, aligh="center")
    # img.save("text.png")
    # await ctx.send(file= discord.File("text.png"))
    await welcome_pic(user)

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
async def stop_rec(ctx):
    if ctx.guild.id in connections:  # Check if the guild is in the cache.
        vc = connections[ctx.guild.id]
        vc.stop_recording()  # Stop recording, and call the callback (once_done).
        del connections[ctx.guild.id]  # Remove the guild from the cache.

client.run(TOKEN)
