import pandas as pd
import os
from steam_api_utils import fetch_reviews_from_api

def translate_reviews(reviews: list) -> list:
    from translator import translate_text

    results = []
    for i, review in enumerate(reviews, 1):
        text = review.get("review", "")
        translated, skipped = translate_text(text, index=i)

        if translated is None:
            if skipped:
                translated_text = text  # Deutsch → Original behalten
            else:
                continue  # Überspringen bei Fehler
        else:
            translated_text = translated

        results.append({
            "Recommended": review.get("voted_up"),
            "PlayTime": review.get("author", {}).get("playtime_forever", 0),
            "Timestamp": review.get("timestamp_created", 0),
            "Übersetzung": translated_text
        })

    return results


def export_reviews(reviews: list, appid: str) -> str:
    os.makedirs("translations", exist_ok=True)
    df = pd.DataFrame(reviews)
    file_path = f"translations/{appid}_translated.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


def run_review_pipeline(appid: str, translate: bool = True, save: bool = True) -> str:
    reviews = fetch_reviews_from_api(appid)

    if not reviews:
        raise Exception("Keine Reviews gefunden.")

    if translate:
        reviews = translate_reviews(reviews)

    if save:
        return export_reviews(reviews, appid)

    return None