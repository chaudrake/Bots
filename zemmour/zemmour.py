import os
import json
import tweepy

# Configuration des chemins relative au script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "index.txt")
DATA_FILE = os.path.join(BASE_DIR, "bot.json")

def init_twitter_client():
    """Initialise le client Twitter avec les secrets GitHub."""
    # Les tokens ne sont plus en dur
    client = tweepy.Client(
        consumer_key=os.environ["TWITTER_CONSUMER_KEY"],
        consumer_secret=os.environ["TWITTER_CONSUMER_SECRET"],
        access_token=os.environ["TWITTER_ACCESS_TOKEN"],
        access_token_secret=os.environ["TWITTER_ACCESS_TOKEN_SECRET"]
    )
    return client

def get_next_qualifier():
    """Récupère le prochain qualificatif dans l'ordre de la liste."""
    with open(DATA_FILE, 'r', encoding="utf-8") as f:
        data = json.load(f)
        [span_0](start_span)qualifiers = data["qualif"] # Utilise la liste de qualificatifs du JSON[span_0](end_span)

    # Gestion de l'index pour le suivi de progression
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r') as f:
            index = int(f.read().strip())
    else:
        index = 0

    # Boucle si on dépasse la taille de la liste
    if index >= len(qualifiers):
        index = 0

    qualifier = qualifiers[index]
    
    # Mise à jour de l'index
    with open(INDEX_FILE, 'w') as f:
        f.write(str(index + 1))
    
    return qualifier

def run_bot():
    try:
        client = init_twitter_client()
        qualifier = get_next_qualifier()
        
        # [span_1](start_span)Reconstruction de la phrase d'origine[span_1](end_span)
        tweet_text = f"Éric #Zemmour est {qualifier}."
        
        client.create_tweet(text=tweet_text)
        print(f"Tweet envoyé : {tweet_text}")
        
    except Exception as e:
        print(f"Erreur lors de l'exécution : {e}")
        exit(1)

if __name__ == "__main__":
    run_bot()
  
