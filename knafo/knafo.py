import tweepy
import random
import os
import sys
import json
import time
from pathlib import Path

# Chemins et constantes
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUALITIES_FILE = os.path.join(BASE_DIR, 'liste.txt')
INDEX_FILE = os.path.join(BASE_DIR, 'last_index.json')

def init_twitter_client():
    """Initialise le client Twitter avec les secrets spécifiques."""
    client = tweepy.Client(
        consumer_key=os.environ["KNAFO_CONSUMER_KEY"],
        consumer_secret=os.environ["KNAFO_CONSUMER_SECRET"],
        access_token=os.environ["KNAFO_ACCESS_TOKEN"],
        access_token_secret=os.environ["KNAFO_ACCESS_TOKEN_SECRET"]
    )
    return client

def read_qualities(qualities_file):
    """Lit les qualités depuis le fichier texte."""
    try:
        with open(qualities_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        print(f"Erreur lecture fichier : {e}")
        return []

def load_index(index_file):
    [span_0](start_span)"""Charge l'index des qualités déjà tweetées[span_0](end_span)."""
    try:
        if Path(index_file).exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"used": []}
    except Exception as e:
        return {"used": []}

def save_index(index_file, index_data):
    [span_1](start_span)"""Sauvegarde l'index des qualités tweetées[span_1](end_span)."""
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f)

def get_next_quality(qualities, index_data):
    [span_2](start_span)"""Récupère la prochaine qualité à tweeter[span_2](end_span)."""
    # [span_3](start_span)Si toutes les qualités ont été utilisées, on réinitialise[span_3](end_span)
    if len(index_data["used"]) >= len(qualities):
        index_data["used"] = []

    # [span_4](start_span)Sélection parmi les qualités non encore utilisées[span_4](end_span)
    remaining = [q for q in qualities if q.lower() not in [u.lower() for u in index_data["used"]]]
    selected = random.choice(remaining)
    index_data["used"].append(selected)

    return selected, index_data

def run_bot():
    try:
        # --- PAUSE ALÉATOIRE (0 à 120 minutes) ---
        wait_minutes = random.randint(0, 120)
        print(f"Attente : {wait_minutes} min...")
        time.sleep(wait_minutes * 60)

        # Initialisation
        qualities = read_qualities(QUALITIES_FILE)
        if not qualities:
            sys.exit(1)
            
        index_data = load_index(INDEX_FILE)
        selected_quality, updated_index = get_next_quality(qualities, index_data)
        
        # Publication
        client = init_twitter_client()
        tweet_text = f"Sarah #Knafo est {selected_quality}."
        client.create_tweet(text=tweet_text)
        
        # Sauvegarde
        save_index(INDEX_FILE, updated_index)
        print(f"Tweet publié : {tweet_text}")

    except Exception as e:
        print(f"Erreur : {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_bot()
  
