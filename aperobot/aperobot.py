import os
import sys
import time
import tweepy
from datetime import datetime
import pytz

# Récupérer les variables d'environnement (GitHub Secrets)
CONSUMER_KEY = os.getenv('APEROBOT_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('APEROBOT_CONSUMER_SECRET')
ACCESS_KEY = os.getenv('APEROBOT_ACCESS_KEY')
ACCESS_SECRET = os.getenv('APEROBOT_ACCESS_SECRET')

# Vérification des credentials
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

paris_tz = pytz.timezone('Europe/Paris')

tweet_schedule = {
    7: ("7h, ce n'est pas l'heure ! ❌ #Apéro"),
    8: ("8h, ce n'est pas l'heure ! ❌ #Apéro"),
    9: ("9h, ce n'est pas l'heure ! ❌ #Apéro"),
    10: ("10h, ce n'est pas l'heure ! ❌ #Apéro"),
    11: ("11h, c'est la bonne heure ! 🍾🎉 #Apéro"),
    12: ("Midi ! C'est maintenant ou jamais pour l'apéritif ! 🎉🍾 #Apéro"),
    13: ("13h ! Dernière chance ! Après, ce ne sera plus l'heure ! 🍾🎉 #Apéro"),
    14: ("14h, ce n'est pas l'heure ! ❌ #Apéro"),
    15: ("15h, ce n'est pas l'heure ! ❌ #Apéro"),
    16: ("16h, ce n'est pas l'heure ! ❌ #Apéro"),
    17: ("17h, ce n'est pas l'heure ! ❌ #Apéro"),
    18: ("18h ! C'est l'heure de sortir les bouteilles ! 🍾🎉 #Apéro"),
    19: ("19h : Gooooo à l'#apéro ! 🎉🍾"),
    20: ("20h, allez ! Un petit dernier... 🍾🎉 #Apéro"),
    21: ("21h, ce n'est plus l'heure ! ❌ #Apéro"),
    22: ("22h, ce n'est plus l'heure ! ❌ \n\nÀ demain ! #Apéro"),
}

def get_target_message(current_time):
    current_hour = current_time.hour
    current_minute = current_time.minute
    
    # Vérifier si on est à la minute exacte (plage -0/+0)
    if current_minute == 0:
        if current_hour in tweet_schedule:
            return tweet_schedule[current_hour]
    
    # Pour 12h00 spécial
    if current_hour == 12 and current_minute == 0:
        return tweet_schedule[12]
    
    return None

def main():
    now = datetime.now(paris_tz)
    print(f"🕐 Heure française: {now.strftime('%H:%M:%S')}")
    
    message = get_target_message(now)
    
    if message is None:
        print(f"⏭️ Aucun tweet prévu à {now.strftime('%H:%M')}")
        return
    
    try:
        api.create_tweet(text=message[:280])
        print(f"✅ Tweet posté à {now.strftime('%H:%M')}: {message[:50]}...")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

print("🏁 Opération terminée")
