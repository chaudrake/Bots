import os
import sys
import time
import logging
import tweepy

# Configuration des secrets
# Ces noms correspondent exactement à votre fichier aperobot.yml
CONSUMER_KEY = os.getenv('APEROBOT_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('APEROBOT_CONSUMER_SECRET')
ACCESS_KEY = os.getenv('APEROBOT_ACCESS_KEY')
ACCESS_SECRET = os.getenv('APEROBOT_ACCESS_SECRET')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def post_tweet():
    # Initialisation du client Twitter (API v2)
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_KEY,
        access_token_secret=ACCESS_SECRET
    )

    max_retries = 2
    retry_delay = 60  # Délai d'attente de 60 secondes

    # Texte du tweet
    tweet_text = "C'est l'heure de l'apéro ! 🍹 #Aperobot"

    for attempt in range(max_retries + 1):
        try:
            logging.info(f"Tentative {attempt + 1} d'envoi du tweet...")
            client.create_tweet(text=tweet_text)
            logging.info("Tweet envoyé avec succès !")
            return True
        except Exception as e:
            # Gestion de l'erreur 403 avec retry
            if "403" in str(e) and attempt < max_retries:
                logging.warning(f"Erreur 403 détectée. Nouvel essai dans {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                logging.error(f"Échec définitif de l'envoi : {e}")
                return False

if __name__ == "__main__":
    # On exécute la fonction et on quitte avec un code erreur si ça échoue
    if not post_tweet():
        sys.exit(1)
