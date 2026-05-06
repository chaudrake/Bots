import tweepy
import datetime
import pytz
import logging
import os

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Configuration du fuseau horaire (comme dans fuseaux.py)
PARIS_TZ = pytz.timezone("Europe/Paris")

def create_api():
    """
    Initialise la connexion à l'API Twitter en utilisant les variables d'environnement.
    On garde la structure initiale d'aperobot.
    """
    auth = tweepy.OAuthHandler(os.getenv("CONSUMER_KEY"), os.getenv("CONSUMER_SECRET"))
    auth.set_access_token(os.getenv("ACCESS_TOKEN"), os.getenv("ACCESS_TOKEN_SECRET"))
    api = tweepy.API(auth, wait_on_rate_limit=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Erreur lors de la création de l'API", exc_info=True)
        raise e
    logger.info("API créée avec succès")
    return api

def get_precise_time_tweet():
    """
    Génère le texte du tweet en récupérant l'heure exacte.
    Inspiré de la logique fuseaux : "HHhMM, ce n'est plus l'heure"
    """
    now = datetime.datetime.now(PARIS_TZ)
    # Formatage de l'heure exacte (ex: 22h04)
    heure_exacte = now.strftime("%Hh%M")
    return f"{heure_exacte}, ce n'est plus l'heure"

def main():
    # 1. Connexion à l'API
    api = create_api()

    # 2. Préparation du message avec l'heure exacte
    tweet_text = get_precise_time_tweet()

    # 3. Envoi du tweet (Fonctionnalité principale conservée)
    try:
        api.update_status(tweet_text)
        logger.info(f"Tweet envoyé : {tweet_text}")
    except Exception as e:
        logger.error("Erreur lors de l'envoi du tweet", exc_info=True)

if __name__ == "__main__":
    main()
    
