# 1 tweet par lancement.
# sleep de 0 à 2h avant déclenchement du tweet
import os
import json
import tweepy
import time
import random

# Configuration des chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "index.txt")
DATA_FILE = os.path.join(BASE_DIR, "bot.json")

def init_twitter_client():
    """Initialise le client Twitter avec les secrets spécifiques."""
    client = tweepy.Client(
        consumer_key=os.environ["ZEMMOUR_CONSUMER_KEY"],
        consumer_secret=os.environ["ZEMMOUR_CONSUMER_SECRET"],
        access_token=os.environ["ZEMMOUR_ACCESS_TOKEN"],
        access_token_secret=os.environ["ZEMMOUR_ACCESS_TOKEN_SECRET"]
    )
    return client

def get_next_qualifier():
    """Récupère le prochain qualificatif et met à jour l'index."""
    with open(DATA_FILE, 'r', encoding="utf-8") as f:
        data = json.load(f)
        qualifiers = data["qualif"]

    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r') as f:
            try:
                index = int(f.read().strip())
            except ValueError:
                index = 0
    else:
        index = 0

    if index >= len(qualifiers):
        index = 0

    qualifier = qualifiers[index]
    
    with open(INDEX_FILE, 'w') as f:
        f.write(str(index + 1))
    
    return qualifier

def run_bot():
    try:
        # --- PAUSE ALÉATOIRE (0 à 120 minutes) ---
        wait_minutes = random.randint(0, 120)
        print(f"Attente aléatoire : {wait_minutes} minutes avant postage...")
        time.sleep(wait_minutes * 60)
        # -----------------------------------------

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
    
