import discord
from discord.ext import commands, tasks
import aiohttp
import random
import os
from keep_alive import keep_alive

keep_alive() 


MEME_CHANNEL_ID =  1367850811610366012# <– HIER deine Channel-ID einfügen
FEATURE_CHANNEL_ID = 1367963171612266598
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

# Schleife für send_meme
@tasks.loop(minutes=5)
async def post_meme():
    channel = bot.get_channel(MEME_CHANNEL_ID)
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

@bot.command()
async def roll(ctx, dice: str = "1d6"):
    allowed_channel_id = FEATURE_CHANNEL_ID

    if ctx.channel.id != allowed_channel_id:
        await ctx.send("❌ Dieser Befehl ist in diesem Channel nicht erlaubt.")
        return
    
    import random
    try:
        rolls, limit = map(int, dice.lower().split("d"))
        results = [random.randint(1, limit) for _ in range(rolls)]
        await ctx.send(f"🎲 {dice}: {results} → Total: {sum(results)}")
    except:
        await ctx.send("❌ Format: z.B. !roll 2d10")

# Starte den Bot
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
