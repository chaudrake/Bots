import tweepy
import os
import pytz
from datetime import datetime

# Configuration Twitter
client = tweepy.Client(
    access_token=os.getenv('THeure_ACCESS_KEY'),
    access_token_secret=os.getenv('THeure_ACCESS_SECRET'),
    consumer_key=os.getenv('THeure_CONSUMER_KEY'),
    consumer_secret=os.getenv('THeure_CONSUMER_SECRET')
)

def main():
    # Fuseau horaire français
    france_tz = pytz.timezone('Europe/Paris')
    now = datetime.now(france_tz)
    current_time_str = now.strftime('%H:%M')
    
    # Heures cibles
    targets = ["00:00", "11:11", "22:22"]
    
    print(f"Heure actuelle à Paris : {current_time_str}")
    
    if current_time_str in targets:
        try:
            client.create_tweet(text=current_time_str)
            print(f"✅ Tweet envoyé : {current_time_str}")
        except Exception as e:
            print(f"❌ Erreur lors du tweet : {e}")
    else:
        # Comme GitHub Actions peut avoir 1 ou 2 min de décalage,
        # on peut élargir la vérification si besoin, mais le cron est généralement précis à la minute.
        print("Ce n'est pas l'heure de tweeter.")

if __name__ == "__main__":
    main()
    
