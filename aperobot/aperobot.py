import os
import sys
import time
import tweepy
from datetime import datetime
import pytz

CONSUMER_KEY = os.getenv('APEROBOT_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('APEROBOT_CONSUMER_SECRET')
ACCESS_KEY = os.getenv('APEROBOT_ACCESS_KEY')
ACCESS_SECRET = os.getenv('APEROBOT_ACCESS_SECRET')

if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]):
    print("❌ Missing Twitter API credentials")
    sys.exit(1)

api = tweepy.Client(
    access_token=ACCESS_KEY,
    access_token_secret=ACCESS_SECRET,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET
)

print("🚀 Lancement de l'Apéro Bot")

france_tz = pytz.timezone('Europe/Paris')

def is_winter_time():
    now = datetime.now(france_tz)
    offset_hours = now.utcoffset().total_seconds() / 3600
    return offset_hours == 1  # UTC+1 = hiver

tweet_schedule = {
    7: "7h, ce n'est pas l'heure ! ❌ #Apéro",
    8: "8h, ce n'est pas l'heure ! ❌ #Apéro",
    9: "9h, ce n'est pas l'heure ! ❌ #Apéro",
    10: "10h, ce n'est pas l'heure ! ❌ #Apéro",
    11: "11h, c'est la bonne heure ! 🍾🎉 #Apéro",
    12: "Midi ! C'est maintenant ou jamais pour l'apéritif ! 🎉🍾 #Apéro",
    13: "13h ! Dernière chance ! Après, ce ne sera plus l'heure ! 🍾🎉 #Apéro",
    14: "14h, ce n'est pas l'heure ! ❌ #Apéro",
    15: "15h, ce n'est pas l'heure ! ❌ #Apéro",
    16: "16h, ce n'est pas l'heure ! ❌ #Apéro",
    17: "17h, ce n'est pas l'heure ! ❌ #Apéro",
    18: "18h ! C'est l'heure de sortir les bouteilles ! 🍾🎉 #Apéro",
    19: "19h : Gooooo à l'#apéro ! 🎉🍾",
    20: "20h, allez ! Un petit dernier... 🍾🎉 #Apéro",
    21: "21h, ce n'est plus l'heure ! ❌ #Apéro",
    22: "22h, ce n'est plus l'heure ! ❌ \n\nÀ demain ! #Apéro",
}

def main():
    # En hiver, attendre 1 heure
    if is_winter_time():
        print("❄️ Heure d'hiver - attente de 1 heure")
        time.sleep(3600)
    else:
        print("☀️ Heure d'été - exécution immédiate")
    
    now = datetime.now(france_tz)
    print(f"🕐 Heure française: {now.strftime('%H:%M:%S')}")
    
    hour = now.hour
    if 7 <= hour <= 22:
        message = tweet_schedule.get(hour)
        if message:
            api.create_tweet(text=message[:280])
            print(f"✅ Tweet posté à {hour}h")
        else:
            print(f"⚠️ Pas de message pour {hour}h")
    else:
        print(f"⏭️ Heure {hour}h hors plage 7h-22h")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)
