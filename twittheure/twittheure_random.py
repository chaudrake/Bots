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

def is_winter_time():
    """Détecte l'heure d'hiver (UTC+1)"""
    now = datetime.now(france_tz)
    return now.dst().total_seconds() == 0

def wait_for_winter_adjustment():
    """En hiver, attend 1 heure pour caler l'heure française"""
    if is_winter_time():
        print("❄️ Heure d'hiver - attente de 1 heure")
        time.sleep(3600)
        print("✅ Reprise après attente")
    else:
        print("☀️ Heure d'été - exécution immédiate")

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
    wait_for_winter_adjustment()
    
    now = datetime.now(france_tz)
    hour = now.hour
    print(f"🕐 Heure française: {now.strftime('%H:%M:%S')}")

    # Plage 6h-22h (Heure Française)
    if 6 <= hour <= 22:
        # Probabilité : ~3 tweets sur 64 lancements quotidiens (toutes les 15 min)
        # 3 / 64 = 0.046
        if random.random() < 0.046:
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
