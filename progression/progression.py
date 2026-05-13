import os
import sys
import logging
from datetime import datetime
import tweepy

# Configuration des chemins pour GitHub Actions
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
PROGRESS_BARS_DIR = os.path.join(WORKING_DIR, 'barres')

# Configuration Twitter API via les Secrets GitHub
ACCESS_KEY = os.environ.get('TWITTER_ACCESS_KEY')
ACCESS_SECRET = os.environ.get('TWITTER_ACCESS_SECRET')
CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET')

# Configuration du logging (sortie standard pour GitHub Actions)
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
        log_and_print(f"Erreur création client Twitter: {e}")
        return None

def calculate_year_progress():
    now = datetime.now()
    year_start = datetime(now.year, 1, 1)
    year_end = datetime(now.year + 1, 1, 1)
    year_duration = (year_end - year_start).total_seconds()
    elapsed = (now - year_start).total_seconds()
    progress = (elapsed / year_duration) * 100
    return progress

def get_progress_image_path(progress):
    progress_rounded = int(round(progress))
    progress_rounded = max(0, min(100, progress_rounded))
    image_name = f"progress_{progress_rounded}.png"
    return os.path.join(PROGRESS_BARS_DIR, image_name)

def is_new_year():
    now = datetime.now()
    return now.month == 1 and now.day == 1

def get_day_of_year_suffix():
    now = datetime.now()
    day = now.timetuple().tm_yday
    return "er" if day == 1 else "e"

def generate_new_year_tweet():
    year = datetime.now().year
    return f"Bonne année à tous.\n\nQue {year} vous apporte bonheur et réussite ! 🎉🥂\n\n #{year}"

def generate_progress_tweet():
    now = datetime.now()
    today = now.strftime("%d/%m/%Y")
    week_number = now.isocalendar().week
    day_of_year = now.timetuple().tm_yday
    day_suffix = get_day_of_year_suffix()
    progress = calculate_year_progress()
    progress_text = f"{progress:.2f}".replace('.', ',')

    return (f"🗓️ Aujourd'hui nous sommes le {today}.\n\n"
            f"🗓️ Semaine No {week_number}.\n\n"
            f"🗓️ {day_of_year}{day_suffix} jour de l'année.\n\n"
            f"⏳ L'année est écoulée à {progress_text}%\n\n"
            "#Progression")

def post_tweet(api):
    try:
        if is_new_year():
            tweet_text = generate_new_year_tweet()
            media_ids = None
        else:
            tweet_text = generate_progress_tweet()
            progress = calculate_year_progress()
            image_path = get_progress_image_path(progress)

            auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
            api_v1 = tweepy.API(auth)
            media = api_v1.media_upload(image_path)
            media_ids = [media.media_id]

        log_and_print(f"Préparation tweet:\n{tweet_text}")
        api.create_tweet(text=tweet_text, media_ids=media_ids)
        return True
    except Exception as e:
        log_and_print(f"Erreur envoi tweet: {e}")
        return False

def main():
    log_and_print("Démarrage du script")
    api = create_twitter_client()
    if api and post_tweet(api):
        log_and_print("Succès")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
