import tweepy
import json
import time
import os
from tqdm import tqdm
from datetime import datetime
from dotenv import load_dotenv

# Configuration
LOG_FILE = 'deleted_tweets.log'  # Fichier pour suivre les suppressions

def load_api_keys():
    """Charge les clés d'API depuis le fichier .env"""
    load_dotenv('/home/pyth1on/.env')

    return {
        'consumer_key': os.getenv('NOEUD_CONSUMER_KEY'),
        'consumer_secret': os.getenv('NOEUD_CONSUMER_SECRET'),
        'access_token': os.getenv('NOEUD_ACCESS_KEY'),
        'access_token_secret': os.getenv('NOEUD_ACCESS_SECRET')
    }

def parse_date(date_str, format='%Y-%m-%d'):
    """Convertit une chaîne de date en objet datetime"""
    if not date_str:
        return None

    try:
        return datetime.strptime(date_str, format)
    except ValueError:
        print(f"Format de date invalide. Utilisez {format}")
        return None

def load_tweet_ids(start_date=None, end_date=None):
    """Charge les IDs depuis tweets.js et exclut ceux déjà supprimés"""
    try:
        # Convertir les dates en objets datetime si fournies
        start_dt = parse_date(start_date)
        end_dt = parse_date(end_date)

        # Charger les tweets de l'archive
        with open('tweets.js', 'r', encoding='utf-8') as f:
            content = f.read()[25:]  # Supprime le préfixe pour obtenir du JSON valide
            tweets_data = json.loads(content)

            all_ids = []
            for tweet in tweets_data:
                tweet_info = tweet['tweet']
                tweet_id = tweet_info['id_str']
                created_at = datetime.strptime(tweet_info['created_at'], '%a %b %d %H:%M:%S %z %Y')

                # Filtrer par date si les paramètres sont fournis
                if start_dt and created_at.replace(tzinfo=None) < start_dt:
                    continue
                if end_dt and created_at.replace(tzinfo=None) > end_dt:
                    continue

                all_ids.append(tweet_id)

        # Charger les IDs déjà supprimés
        deleted_ids = set()
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                deleted_ids = set(f.read().splitlines())

        # Filtrer les IDs restants
        remaining_ids = [id for id in all_ids if id not in deleted_ids]
        return remaining_ids, len(all_ids)

    except Exception as e:
        print(f"Erreur lecture des données: {e}")
        return None, 0

def log_deleted_tweet(tweet_id):
    """Enregistre les IDs supprimés"""
    with open(LOG_FILE, 'a') as f:
        f.write(f"{tweet_id}\n")

def delete_tweets(api, tweet_ids, total_count):
    """Gère la suppression avec suivi"""
    remaining_count = len(tweet_ids)
    if remaining_count == 0:
        print(f"Tous les {total_count} tweets ont déjà été supprimés.")
        return

    print(f"Progression: {total_count - remaining_count}/{total_count} déjà supprimés")
    print(f"Restants: {remaining_count} tweets")

    confirm = input("Voulez-vous continuer la suppression? (o/n): ").lower()
    if confirm != 'o':
        print("Annulation.")
        return

    deleted = 0
    errors = 0

    for tweet_id in tqdm(tweet_ids, desc="Suppression"):
        try:
            api.destroy_status(tweet_id)
            log_deleted_tweet(tweet_id)
            deleted += 1
            time.sleep(1.2)
        except tweepy.TweepyException as e:
            if "No status found with that ID" in str(e):
                # Le tweet est déjà supprimé
                log_deleted_tweet(tweet_id)
                deleted += 1
            else:
                errors += 1
                print(f"\nErreur avec {tweet_id}: {e}")
                time.sleep(10)  # Pause réduite pour erreurs connues

    print(f"\nRésultat: {deleted} nouveaux supprimés, {errors} erreurs")

def initialize_api():
    """Initialise et retourne l'API Twitter"""
    try:
        keys = load_api_keys()
        auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
        auth.set_access_token(keys['access_token'], keys['access_token_secret'])
        api = tweepy.API(auth, wait_on_rate_limit=True)
        api.verify_credentials()
        return api
    except Exception as e:
        print(f"Erreur initialisation API: {e}")
        return None

def main():
    try:
        # Initialisation API
        api = initialize_api()
        if not api:
            return

        # Demander les dates de filtrage
        print("\nFiltrage par date (laisser vide pour ignorer)")
        start_date = input("Date de début (AAAA-MM-JJ): ").strip()
        end_date = input("Date de fin (AAAA-MM-JJ): ").strip()

        # Chargement des tweets avec filtrage par date
        tweet_ids, total_count = load_tweet_ids(start_date, end_date)
        if tweet_ids is not None:
            delete_tweets(api, tweet_ids, total_count)

    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    main()