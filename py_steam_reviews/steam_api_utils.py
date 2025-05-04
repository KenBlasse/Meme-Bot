import requests
import time
import logging

logger = logging.getLogger(__name__)

def fetch_reviews_from_api(app_id, max_reviews=None):
    logger.info(f"🔎 Starte Review-Abruf für App-ID {app_id}")
    
    cursor = "*"
    all_reviews = []
    page = 1

    while True:
        url = (
            f"https://store.steampowered.com/appreviews/{app_id}"
            f"?json=1&num_per_page=100&cursor={cursor}&language=all&filter=all"
        )
        
        response = requests.get(url)
        if not response.ok:
            logger.error(f"❌ Fehler beim Abruf der API: {response.status_code}")
            break

        data = response.json()
        new_reviews = data.get("reviews", [])
        if not new_reviews:
            logger.warning("ℹ️ Keine neuen Reviews mehr erhalten.")
            break

        all_reviews.extend(new_reviews)
        logger.info(f"📄 Seite {page}: {len(new_reviews)} Reviews geladen. Total: {len(all_reviews)}")

        if max_reviews and len(all_reviews) >= max_reviews:
            logger.info(f"🔺 Limit erreicht: {len(all_reviews)} / {max_reviews}")
            all_reviews = all_reviews[:max_reviews]
            break

        new_cursor = data.get("cursor")
        logger.info(f"📌 Cursor nach Seite {page}: {new_cursor}")

        if not new_cursor or new_cursor == cursor:
            logger.warning("⚠️ Kein gültiger neuer Cursor erhalten – breche ab.")
            break

        cursor = new_cursor
        page += 1
        time.sleep(1.1)

    logger.info(f"✅ Insgesamt {len(all_reviews)} Reviews geladen.")
    return all_reviews
