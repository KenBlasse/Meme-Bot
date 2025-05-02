import discord
from discord.ext import commands, tasks
import aiohttp
import random
import os
from keep_alive import keep_alive  # Wenn du Replit nutzt

# Setze hier deinen echten Discord-Channel-ID ein (nach Aktivierung von Entwicklermodus)
CHANNEL_ID =  # <– HIER deine Channel-ID einfügen

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Meme-Subreddits mit IT-Bezug
it_subreddits = ["ProgrammerHumor", "codinghumor", "techhumor", "linuxmemes"]

# Wird ausgeführt, wenn der Bot bereit ist
@bot.event
async def on_ready():
    print(f"✅ {bot.user} ist online!")
    post_meme.start()  # Startet automatische Meme-Schleife

# !meme Befehl manuell
@bot.command()
async def meme(ctx):
    await send_meme(ctx.channel)

# Automatischer Poster (alle 60 Sekunden)
@tasks.loop(minutes=1)
async def post_meme():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await send_meme(channel)
    else:
        print("❌ Channel nicht gefunden. Prüfe die CHANNEL_ID.")

# Zentrale Meme-Sende-Funktion
async def send_meme(channel):
    subreddit = random.choice(it_subreddits)
    url = f"https://meme-api.com/gimme/{subreddit}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                await channel.send("⚠️ Meme API antwortet nicht.")
                return
            data = await response.json()

    title = data["title"]
    image_url = data["url"]
    await channel.send(f"**{title}**\nFrom r/{subreddit}\n{image_url}")

# Starte den Bot

keep_alive()
bot.run(token)
