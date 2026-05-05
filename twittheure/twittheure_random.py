import tweepy
import os
import random
import json
import pytz
from datetime import datetime

# Configuration Twitter
client = tweepy.Client(
    access_token=os.getenv('THeure_ACCESS_KEY'),
    access_token_secret=os.getenv('THeure_ACCESS_SECRET'),
    consumer_key=os.getenv('THeure_CONSUMER_KEY'),
    consumer_secret=os.getenv('THeure_CONSUMER_SECRET')
)

def generate_random_hour_tweet():
    try:
        # On s'assure de lire le fichier bot.json dans le bon dossier
        with open("bot.json", 'r', encoding="utf-8") as f:
            grammar_data = json.load(f)
        h = random.choice(grammar_data["heures"])
        m = random.choice(grammar_data["minutes"])
        return f"Il n'est pas {h}h{m}"
    except Exception as e:
        print(f"❌ Erreur lecture bot.json: {e}")
        return None

def main():
    france_tz = pytz.timezone('Europe/Paris')
    now = datetime.now(france_tz)
    hour = now.hour

    # On vérifie la plage 6h-22h (Heure Française)
    if 6 <= hour <= 22:
        # Probabilité : ~3 tweets sur 64 lancements quotidiens (toutes les 15 min)
        # 3 / 64 = 0.046
        if random.random() < 0.046:
            tweet_text = generate_random_hour_tweet()
            if tweet_text:
                try:
                    client.create_tweet(text=tweet_text)
                    print(f"✅ Tweet aléatoire publié : {tweet_text}")
                except Exception as e:
                    print(f"❌ Erreur API Twitter : {e}")
        else:
            print("🎲 Le tirage n'a pas retenu de tweet pour cette fois.")
    else:
        print(f"🌙 {hour}h : En dehors de la plage horaire (6h-22h).")

if __name__ == "__main__":
    main()
    
