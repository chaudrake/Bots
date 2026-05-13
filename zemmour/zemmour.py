import os
import json
import tweepy
import time
import random

# Configuration des chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "index.json")
DATA_FILE = os.path.join(BASE_DIR, "bot.json")

def init_twitter_client():
    client = tweepy.Client(
        consumer_key=os.environ["ZEMMOUR_CONSUMER_KEY"],
        consumer_secret=os.environ["ZEMMOUR_CONSUMER_SECRET"],
        access_token=os.environ["ZEMMOUR_ACCESS_TOKEN"],
        access_token_secret=os.environ["ZEMMOUR_ACCESS_TOKEN_SECRET"]
    )
    return client

def get_next_qualifier():
    # Chargement de tous les qualificatifs
    with open(DATA_FILE, 'r', encoding="utf-8") as f:
        data = json.load(f)
        all_qualifiers = data["qualif"]

    # Chargement de l'index des déjà utilisés
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r', encoding="utf-8") as f:
            index_data = json.load(f)
    else:
        index_data = {"used": []}

    # Filtrer pour ne garder que ceux qui n'ont pas été utilisés
    available = [q for q in all_qualifiers if q not in index_data["used"]]

    # Si tout a été utilisé, on réinitialise
    if not available:
        print("Tous les qualificatifs ont été utilisés. Réinitialisation...")
        available = all_qualifiers
        index_data["used"] = []

    # Choix aléatoire parmi les disponibles
    qualifier = random.choice(available)
    
    # Mise à jour de l'index
    index_data["used"].append(qualifier)
    with open(INDEX_FILE, 'w', encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False)
    
    return qualifier

def run_bot():
    try:
        # Pause aléatoire (0 à 10 minutes)
        wait_minutes = random.randint(0, 10)
        print(f"Attente : {wait_minutes} min...")
        time.sleep(wait_minutes * 60)

        client = init_twitter_client()
        qualifier = get_next_qualifier()
        
        tweet_text = f"Éric #Zemmour est {qualifier}."
        
        client.create_tweet(text=tweet_text)
        print(f"Succès : {tweet_text}")
        
    except Exception as e:
        print(f"Erreur : {e}")
        exit(1)

if __name__ == "__main__":
    run_bot()
    
