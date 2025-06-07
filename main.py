import discord
from discord.ext import commands, tasks
import aiohttp
import random
import os
import asyncio
import datetime
from keep_alive import keep_alive
from py_steam_reviews.translate_reviews import run_review_pipeline

keep_alive() 

# Channel IDs
MEME_CHANNEL_ID =  1367850811610366012
FEATURE_CHANNEL_ID = 1367963171612266598
NEWS_CHANNEL_ID = 1367973360818192476
REVIEW_CHANNEL_ID = 1368590938787545211

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
    post_meme.start()
    post_news.start()

# !meme Befehl manuell
@bot.command()
async def meme(ctx):
    await send_meme(ctx.channel)


import asyncio

@bot.command()
async def steamreviews(ctx, appid: str, limit: str = "100"):
    if ctx.channel.id != REVIEW_CHANNEL_ID:
        await ctx.send("❌ Dieser Befehl ist nur im Review-Channel erlaubt.")
        return

    status = await ctx.send(f"📦 Lade Reviews für App-ID `{appid}`...")

    if limit.lower() == "all":
        max_reviews = None
    else:
        try:
            max_reviews = int(limit)
        except ValueError:
            await status.edit(content="Ungültige Zahl. Bitte 'all' oder eine Zahl eingeben")
            return

    try:
        await status.edit(content="⏳ Übersetzung läuft im Hintergrund...")
        loop = asyncio.get_event_loop()
        file_path, total, translated, skipped, errors = await asyncio.to_thread(
            run_review_pipeline,
            appid,
            True,
            True,
            max_reviews,
            ctx.channel,
            loop
        )
        
        await ctx.send(
            f"📊 Ergebnis für `{appid}`:\n"
            f"✅ Übersetzt: {translated}/{total}\n"
            f"⚠️ Übersprungen (Deutsch): {skipped}\n"
            f"❌ Fehler: {errors}"
        )

        await status.edit(content=f"✅ {total} Reviews verarbeitet. Sende Datei...")
        await ctx.send(file=discord.File(file_path))

    except Exception as e:
        await status.edit(content=f"❌ Fehler: {str(e)}")



# Schleife für send_meme
@tasks.loop(minutes=15)
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
async def weather(ctx, *, ort_input: str):
    allowed_channel_id = FEATURE_CHANNEL_ID

    if ctx.channel.id != allowed_channel_id:
        await ctx.send("❌ Dieser Befehl ist in diesem Channel nicht erlaubt.")
        return

    await ctx.send("🌍 Suche Wetterdaten...")

    try:
        ort = None
        lat = None
        lon = None

        async with aiohttp.ClientSession() as session:
            # 🏷️ Prüfe, ob PLZ (nur Ziffern)
            if ort_input.strip().isdigit():
                async with session.get(f"http://api.zippopotam.us/de/{ort_input.strip()}") as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Ungültige PLZ.")
                        return
                    data = await resp.json()
                    ort = data['places'][0]['place name']
                    lat = data['places'][0]['latitude']
                    lon = data['places'][0]['longitude']
            else:
                # 📍 Ortsname via Nominatim (OpenStreetMap)
                async with session.get(f"https://nominatim.openstreetmap.org/search?q={ort_input}&format=json&limit=1") as resp:
                    nominatim = await resp.json()
                    if not nominatim:
                        await ctx.send("❌ Ort nicht gefunden.")
                        return
                    ort = nominatim[0]["display_name"].split(",")[0]
                    lat = nominatim[0]["lat"]
                    lon = nominatim[0]["lon"]

        # 🌦 Wetterdaten via Open-Meteo
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            ) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Wetterdaten konnten nicht abgerufen werden.")
                    return
                weather_data = await resp.json()

        weather = weather_data["current_weather"]
        temp = weather["temperature"]
        wind = weather["windspeed"]
        code = weather["weathercode"]

        # 🧠 Mapping von Wettercode → Beschreibung + Farbe
        weather_map = {
            0:  ("☀️ Klarer Himmel", 0xf1c40f),
            1:  ("🌤️ Teilweise bewölkt", 0xf39c12),
            2:  ("⛅ Wechselhaft", 0xf39c12),
            3:  ("☁️ Bewölkt", 0x95a5a6),
            45: ("🌫️ Nebel", 0x7f8c8d),
            48: ("🌫️ Nebel mit Reif", 0x7f8c8d),
            51: ("🌦️ Leichter Nieselregen", 0x3498db),
            61: ("🌧️ Leichter Regen", 0x3498db),
            63: ("🌧️ Mäßiger Regen", 0x2980b9),
            65: ("🌧️ Starker Regen", 0x2c3e50),
            80: ("🌦️ Regenschauer", 0x3498db),
            95: ("⛈️ Gewitter", 0xe74c3c),
        }

        beschreibung, farbe = weather_map.get(code, ("🌍 Wetterdaten", 0x1abc9c))

        # 📦 Embed erstellen
        embed = discord.Embed(
            title=f"Wetter für {ort}",
            description=beschreibung,
            color=farbe
        )
        embed.add_field(name="🌡️ Temperatur", value=f"{temp} °C", inline=True)
        embed.add_field(name="💨 Wind", value=f"{wind} km/h", inline=True)
        embed.set_footer(text="Quelle: Open-Meteo & OpenStreetMap")
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/869/869869.png")

        await ctx.send(embed=embed)

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
