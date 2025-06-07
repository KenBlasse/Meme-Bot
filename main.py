import discord
from discord.ext import commands, tasks
import aiohttp
import random
import os
import asyncio
import datetime
from openai import OpenAI
from keep_alive import keep_alive

keep_alive() 


MEME_CHANNEL_ID =  1367850811610366012
FEATURE_CHANNEL_ID = 1367963171612266598
NEWS_CHANNEL_ID = 1367973360818192476
# Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

# Meme-Subreddits mit IT-Bezug
it_subreddits = ["ProgrammerHumor", "codinghumor", "techhumor", "linuxmemes"]

# Wird ausgeführt, wenn der Bot bereit ist
@bot.event
async def on_ready():
    print(f"✅ {bot.user} ist online!")
    post_meme.start()
    post_news.start()

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
    
    try:
        rolls, limit = map(int, dice.lower().split("d"))
        results = [random.randint(1, limit) for _ in range(rolls)]
        await ctx.send(f"🎲 {dice}: {results} → Total: {sum(results)}")
    except:
        await ctx.send("❌ Format: z.B. !roll 2d10")

@bot.command()
async def weather(ctx, ort: str):
    allowed_channel_id = FEATURE_CHANNEL_ID
    datum = datetime.date.today().strftime("%d.%m.%Y")
    
    if ctx.channel.id != allowed_channel_id:
        await ctx.send("❌ Dieser Befehl ist in diesem Channel nicht erlaubt.")
        return

    if ort is None:
        await ctx.send("❗ Bitte gib einen Ort an. Beispiel: `!weather Hohen-Sülzen`")
        return

    prompt = f"Gib mir einen ausführlichen Wetterbericht für {ort} am {datum}."

    await ctx.send("Hole aktuellen Wetterbericht...")

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role":"user", "content":prompt}],
            temperature=0.7,
            max_tokens=800
        )

        bericht = response.choices[0].message.content
        for chunk in[bericht[i:i+2000] for i in range (0, len(bericht),2000)]:
            await ctx.send(chunk)

    except Exception as e:
        await ctx.send(f"❌ Fehler beim Abrufen: {e}")
    

@tasks.loop(minutes=240)
async def post_news():
    channel = bot.get_channel(NEWS_CHANNEL_ID)
    if channel:
        await send_news(channel)
    else:
        print("❌ Channel nicht gefunden. Prüfe die CHANNEL_ID.")

@bot.command()
async def news(ctx):
    if ctx.channel.id != NEWS_CHANNEL_ID:
        await ctx.send("❌ Dieser Befehl ist in diesem Channel nicht erlaubt.")
        return

    await send_news(ctx.channel)

async def send_news(channel):
    async with aiohttp.ClientSession() as session:
        top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        async with session.get(top_url) as response:
            ids = await response.json()
        
        headlines = []
        for id in ids[:2]:
            item_url = f"https://hacker-news.firebaseio.com/v0/item/{id}.json"
            async with session.get(item_url) as item_response:
                item = await item_response.json()
                headlines.append(f"({item.get('url', 'https://news.ycombinator.com/item?id='+str(id))})")

    await channel.send("\n".join(headlines))


# Starte den Bot
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
