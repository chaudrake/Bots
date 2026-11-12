import tweepy
import os
import sys
import time
import random
import json
import pytz
from datetime import datetime

# Configuration Twitter
CONSUMER_KEY = os.getenv('THeure_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('THeure_CONSUMER_SECRET')
ACCESS_KEY = os.getenv('THeure_ACCESS_KEY')
ACCESS_SECRET = os.getenv('THeure_ACCESS_SECRET')

if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]):
    print("❌ Missing Twitter API credentials")
    sys.exit(1)

client = tweepy.Client(
    access_token=ACCESS_KEY,
    access_token_secret=ACCESS_SECRET,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET
)

print("🚀 Lancement du bot TwittHeure (heures aléatoires)")

france_tz = pytz.timezone('Europe/Paris')

def generate_random_hour_tweet():
    try:
        with open("bot.json", 'r', encoding="utf-8") as f:
            grammar_data = json.load(f)
        h = random.choice(grammar_data["heures"])
        m = random.choice(grammar_data["minutes"])
        return f"Il n'est pas {h}h{m}"
    except Exception as e:
        print(f"❌ Erreur lecture bot.json: {e}")
        return None

def main():
    now = datetime.now(france_tz)
    hour = now.hour
    print(f"🕐 Heure française: {now.strftime('%H:%M:%S')}")

    # Plage 6h-22h (Heure Française)
    if 6 <= hour <= 22:
        if random.random() < 0.5:
            # Attente aléatoire entre 5 minutes (300s) et 2 heures (7200s)
            wait_seconds = random.randint(300, 7200)
            wait_minutes = round(wait_seconds / 60, 1)
            print(f"⏳ Tirage validé ! Attente aléatoire de {wait_minutes} minutes ({wait_seconds}s) avant publication...")
            time.sleep(wait_seconds)

            tweet_text = generate_random_hour_tweet()
            if tweet_text:
                try:
                    client.create_tweet(text=tweet_text[:280])
                    print(f"✅ Tweet aléatoire publié : {tweet_text}")
                except Exception as e:
                    print(f"❌ Erreur API Twitter : {e}")
                    sys.exit(1)
            else:
                print("❌ Impossible de générer le tweet")
        else:
            print("🎲 Le tirage n'a pas retenu de tweet pour cette fois.")
    else:
        print(f"🌙 {hour}h : En dehors de la plage horaire (6h-22h)")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

print("🏁 Opération terminée")
