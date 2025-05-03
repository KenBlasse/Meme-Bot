
# 🤖 MemeBot – Discord-Bot für IT-Memes, Würfel und News

**MemeBot** ist ein einfacher, modularer Discord-Bot, der automatisch IT-Memes und aktuelle Hacker-News postet, würfelt, und auf Chatbefehle reagiert. Perfekt für Klassengruppen, Bot-Testserver und Tech-Communities.

---

## ⚙️ Features

- 🖼️ **Automatische IT-Memes** alle 5 Minuten (`r/ProgrammerHumor`, `r/linuxmemes`, …)
- 💬 `!meme` – manuelles Meme-Posting
- 📰 `!news` – aktuelle Hacker-News (via Hacker News API)
- 🕐 **Auto-News** alle 2 Stunden
- 🎲 `!roll 1d6` – Würfelfunktion für z. B. 2d10, 1d20 usw.
- 🔒 Kanalbeschränkung pro Befehl
- ☁️ Läuft 24/7 auf [Render](https://render.com) (kostenloser Plan mit Ping)
- 🌐 Mini-Webserver (`keep_alive.py`) für Port-Bindung

---

## 🚀 Beispielbefehle

```text
!meme               # Postet ein zufälliges IT-Meme
!roll 2d10          # Würfelt 2 zehnseitige Würfel
!news               # Zeigt die 5 aktuellsten Tech-News
```

---

## 🧪 Voraussetzungen

- Python 3.10+
- `discord.py`
- `aiohttp`
- `flask` (nur für Render)
- optional: `.env` mit `DISCORD_TOKEN`

```bash
pip install -r requirements.txt
```

---

## 🛠️ Deployment

### 🧑‍💻 Lokal oder auf Zimablade
```bash
python main.py
```

### ☁️ Deployment auf Render
1. GitHub-Repo mit diesem Bot verbinden
2. `keep_alive.py` sorgt für Portbindung (Render erwartet Port 8080)
3. `DISCORD_TOKEN` als Environment Variable setzen
4. Optional: UptimeRobot pingen für Dauerbetrieb

---

## 🌐 UptimeRobot für Dauerbetrieb (Render Free Plan)

Damit dein Bot auf Render **nicht automatisch „einschläft“**, kannst du einen kostenlosen Uptime-Ping einrichten:

### ✅ Anleitung:

1. Besuche [https://uptimerobot.com](https://uptimerobot.com)
2. Erstelle ein kostenloses Konto
3. Klicke auf **„+ Add Monitor“**
4. Wähle:
   - **Monitor Type:** `HTTP(s)`
   - **Friendly Name:** `MemeBot Render`
   - **URL:** Deine Render-URL (z. B. `https://meme-bot-xyz.onrender.com`)
   - **Monitoring Interval:** alle 5 Minuten
5. Speichern und aktivieren

Der Bot bleibt so dauerhaft wach, da Render durch den Port-Zugriff aktiv bleibt.

---

## 📁 Projektstruktur

```text
├── main.py            # Hauptlogik: Befehle, Loops, Setup
├── keep_alive.py      # Mini-Flask-Server für Render
├── requirements.txt   # Abhängigkeiten
└── README.md          # Du liest sie gerade
```

---

## ✏️ To-Do / Ideen

- [ ] Themenbasierte News-Suche (`!news ai`)
- [ ] GIFs, Insults oder Komplimente

---

## 📜 Lizenz

MIT License – kostenlos nutzbar, gerne erweitern oder forken!

---

> Erstellt von Alex als Testumgebung für Discord-Bots 🎓
