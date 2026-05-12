# Script pour tweeter le décompte jusqu'à Noël
import os
import sys
import logging
from datetime import datetime
import tweepy

# Configuration des chemins pour GitHub Actions
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'compte_noel.log')

# Configuration Twitter API (via secrets GitHub)
ACCESS_KEY = os.getenv('NOEL_ACCESS_KEY')
ACCESS_SECRET = os.getenv('NOEL_ACCESS_SECRET')
CONSUMER_KEY = os.getenv('NOEL_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('NOEL_CONSUMER_SECRET')

# Configuration du logging
logging.basicConfig(filename=LOG_FILE,
                   level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

def log_and_print(message):
    print(message)
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

def calculate_days_until_christmas():
    now = datetime.now()
    current_year = now.year
    if now.month == 12 and now.day > 25:
        christmas_date = datetime(current_year + 1, 12, 25)
    else:
        christmas_date = datetime(current_year, 12, 25)
    days_until = (christmas_date - now).days
    return max(0, days_until)

def generate_christmas_tweet(days_until):
    now = datetime.now()
    is_christmas_eve = (now.month == 12 and now.day == 24)
    is_christmas_day = (now.month == 12 and now.day == 25)

    if is_christmas_day or (days_until == 0 and not is_christmas_eve):
        return "🎅 Joyeux #Noël à tous ! 🎄🎁\n\n #JoyeuxNoël"
    elif is_christmas_eve:
        return "🎅 C'est CETTE NUIT que le Père #Noël passe ! 🎄\n\nN'oubliez pas les cookies et le lait !\n\n#Noël #Réveillon"
    else:
        dodos = "dodo" if days_until == 1 else "dodos"
        return f"🎄 Plus que {days_until} {dodos} avant l'arrivée du Père #Noël ! 🎅\n\n À demain !\n\n#Noël #CompteÀRebours"

def post_tweet(api):
    try:
        days_until = calculate_days_until_christmas()
        tweet_text = generate_christmas_tweet(days_until)
        log_and_print(f"Jours jusqu'à Noël: {days_until}")
        api.create_tweet(text=tweet_text)
        log_and_print(f"Tweet envoyé:\n{tweet_text}")
        return True
    except Exception as e:
        log_and_print(f"Erreur envoi tweet: {e}")
        return False

def main():
    log_and_print("Démarrage du script Noël")
    api = create_twitter_client()
    if api:
        post_tweet(api)
    else:
        log_and_print("Échec de la connexion à Twitter")
    sys.exit(0)

if __name__ == "__main__":
    main()
  
