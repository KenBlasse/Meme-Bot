import pandas as pd
import os
from .steam_api_utils import fetch_reviews_from_api
from .translator import translate_text

def translate_reviews(reviews: list) -> list:
    
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


def run_review_pipeline(appid: str, translate: bool = True, save: bool = True):
    reviews = fetch_reviews_from_api(appid)

    if not reviews:
        raise Exception("Keine Reviews gefunden.")

    translated_count = 0
    skipped_count = 0
    error_count = 0

    if translate:
        translated_reviews = []
        for i, review in enumerate(reviews, 1):
            text = review.get("review", "")
            translated, skipped = translate_text(text, index=i)

            if translated is None:
                if skipped:
                    skipped_count += 1
                    translated_text = text
                else:
                    error_count += 1
                    continue
            else:
                translated_count += 1
                translated_text = translated

            translated_reviews.append({
                "Recommended": review.get("voted_up"),
                "PlayTime": review.get("author", {}).get("playtime_forever", 0),
                "Timestamp": review.get("timestamp_created", 0),
                "Übersetzung": translated_text
            })

        reviews = translated_reviews

    if save:
        file_path = export_reviews(reviews, appid)
    else:
        file_path = None

    return file_path, len(reviews), translated_count, skipped_count, error_count
