import os
import sys
import time
import logging
from datetime import datetime
import pytz
import tweepy

# Configuration des secrets
CONSUMER_KEY = os.getenv('APEROBOT_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('APEROBOT_CONSUMER_SECRET')
ACCESS_KEY = os.getenv('APEROBOT_ACCESS_KEY')
ACCESS_SECRET = os.getenv('APEROBOT_ACCESS_SECRET')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_aperobot_text():
    """Génère le texte du tweet en fonction de l'heure de Paris"""
    tz_paris = pytz.timezone('Europe/Paris')
    now_paris = datetime.now(tz_paris)
    heure = now_paris.strftime("%H:%M")
    
    # Votre logique de texte habituelle (exemple à adapter selon votre script original)
    return f"📢 Il est {heure} ! C'est l'heure de l'apéro quelque part... ou bientôt ici ! 🍹 #Aperobot"

def post_tweet():
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_KEY,
        access_token_secret=ACCESS_SECRET
    )

    max_retries = 2
    retry_delay = 60 

    for attempt in range(max_retries + 1):
        try:
            # On génère le texte à chaque tentative pour avoir l'heure exacte
            tweet_text = get_aperobot_text()
            
            logging.info(f"Tentative {attempt + 1} : Envoi du tweet de {datetime.now().strftime('%H:%M:%S')}")
            client.create_tweet(text=tweet_text)
            logging.info("Tweet envoyé avec succès !")
            return True
        except Exception as e:
            if "403" in str(e) and attempt < max_retries:
                logging.warning(f"Erreur 403 détectée. Nouvel essai dans {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                logging.error(f"Échec de l'envoi : {e}")
                return False

if __name__ == "__main__":
    if not post_tweet():
        sys.exit(1)
