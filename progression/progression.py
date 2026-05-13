import os
import sys
import logging
from datetime import datetime
import tweepy

# Configuration des chemins relatifs
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
PROGRESS_BARS_DIR = os.path.join(WORKING_DIR, 'barres')

# Récupération des tokens via Secrets GitHub
ACCESS_KEY = os.getenv('PROGRESSION_ACCESS_KEY')
ACCESS_SECRET = os.getenv('PROGRESSION_ACCESS_SECRET')
CONSUMER_KEY = os.getenv('PROGRESSION_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('PROGRESSION_CONSUMER_SECRET')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_and_print(message):
    logging.info(message)

def create_twitter_client():
    try:
        return tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_KEY,
            access_token_secret=ACCESS_SECRET
        )
    except Exception as e:
        log_and_print(f"Erreur client Twitter: {e}")
        return None

def calculate_year_progress():
    now = datetime.now()
    year_start = datetime(now.year, 1, 1)
    year_end = datetime(now.year + 1, 1, 1)
    year_duration = (year_end - year_start).total_seconds()
    elapsed = (now - year_start).total_seconds()
    return (elapsed / year_duration) * 100

def get_progress_image_path(progress):
    """Retourne le chemin vers le fichier .gif correspondant"""
    progress_rounded = max(0, min(100, int(round(progress))))
    # [span_0](start_span)Mise à jour de l'extension en .gif[span_0](end_span)
    image_name = f"progress_{progress_rounded}.gif"
    return os.path.join(PROGRESS_BARS_DIR, image_name)

def generate_progress_tweet():
    now = datetime.now()
    today = now.strftime("%d/%m/%Y")
    week_number = now.isocalendar().week
    day_of_year = now.timetuple().tm_yday
    day_suffix = "er" if day_of_year == 1 else "e"
    progress = calculate_year_progress()
    progress_text = f"{progress:.2f}".replace('.', ',')

    return (f"🗓️ Aujourd'hui nous sommes le {today}.\n\n"
            f"🗓️ Semaine No {week_number}.\n\n"
            f"🗓️ {day_of_year}{day_suffix} jour de l'année.\n\n"
            f"⏳ L'année est écoulée à {progress_text}%\n\n"
            "#Progression")

def post_tweet(api):
    try:
        tweet_text = generate_progress_tweet()
        progress = calculate_year_progress()
        image_path = get_progress_image_path(progress)

        # Auth v1.1 pour l'upload média
        auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
        api_v1 = tweepy.API(auth)
        
        log_and_print(f"Upload de l'image: {image_path}")
        media = api_v1.media_upload(image_path)
        
        # Envoi via API v2
        api.create_tweet(text=tweet_text, media_ids=[media.media_id])
        return True
    except Exception as e:
        log_and_print(f"Erreur lors de l'envoi: {e}")
        return False

def main():
    log_and_print("Démarrage du script année écoulée")
    api = create_twitter_client()
    if api and post_tweet(api):
        log_and_print("Tweet envoyé avec succès")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
