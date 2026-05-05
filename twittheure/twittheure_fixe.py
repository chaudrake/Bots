import tweepy
import os
import sys
import time
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

print("🚀 Lancement du bot TwittHeure (heures fixes)")

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

def main():
    wait_for_winter_adjustment()
    
    now = datetime.now(france_tz)
    current_time_str = now.strftime('%H:%M')
    
    print(f"🕐 Heure française: {current_time_str}")
    
    # Heures cibles
    targets = ["00:00", "11:11", "22:22"]
    
    if current_time_str in targets:
        try:
            client.create_tweet(text=current_time_str)
            print(f"✅ Tweet envoyé : {current_time_str}")
        except Exception as e:
            print(f"❌ Erreur lors du tweet : {e}")
            sys.exit(1)
    else:
        print(f"⏭️ Ce n'est pas l'heure de tweeter ({current_time_str})")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

print("🏁 Opération terminée")
