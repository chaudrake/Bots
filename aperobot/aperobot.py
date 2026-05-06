import os
import sys
import time
import tweepy
from datetime import datetime
import pytz

# On conserve tes identifiants exacts
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

print("🚀 Lancement de l'Apéro Bot (Mode Heure Précise)")

france_tz = pytz.timezone('Europe/Paris')

def is_winter_time():
    now = datetime.now(france_tz)
    offset_hours = now.utcoffset().total_seconds() / 3600
    return offset_hours == 1  # UTC+1 = hiver

# On garde ton dictionnaire pour la fin des phrases
tweet_schedule = {
    7: "ce n'est pas l'heure ! ❌ #Apéro",
    8: "ce n'est pas l'heure ! ❌ #Apéro",
    9: "ce n'est pas l'heure ! ❌ #Apéro",
    10: "ce n'est pas l'heure ! ❌ #Apéro",
    11: "c'est la bonne heure ! 🍾🎉 #Apéro",
    12: "C'est maintenant ou jamais pour l'apéritif ! 🎉🍾 #Apéro", # "Midi" sera remplacé par 12h00
    13: "Dernière chance ! Après, ce ne sera plus l'heure ! 🍾🎉 #Apéro",
    14: "ce n'est pas l'heure ! ❌ #Apéro",
    15: "ce n'est pas l'heure ! ❌ #Apéro",
    16: "ce n'est pas l'heure ! ❌ #Apéro",
    17: "ce n'est pas l'heure ! ❌ #Apéro",
    18: "C'est l'heure de sortir les bouteilles ! 🍾🎉 #Apéro",
    19: "Gooooo à l'#apéro ! 🎉🍾",
    20: "allez ! Un petit dernier... 🍾🎉 #Apéro",
    21: "ce n'est plus l'heure ! ❌ #Apéro",
    22: "ce n'est plus l'heure ! ❌ \n\nÀ demain ! #Apéro",
}

def main():
    # Conservation de ta logique de délai hiver/été
    if is_winter_time():
        print("❄️ Heure d'hiver - attente de 1 heure")
        time.sleep(3600)
    else:
        print("☀️ Heure d'été - exécution immédiate")
    
    now = datetime.now(france_tz)
    # On récupère l'heure précise comme dans fuseaux (ex: 22h04)
    heure_exacte = now.strftime("%Hh%M")
    hour = now.hour
    
    print(f"🕐 Heure française précise: {heure_exacte}")
    
    if 7 <= hour <= 22:
        suffixe = tweet_schedule.get(hour)
        if suffixe:
            # Construction du tweet final : "HeurePrécise, texte"
            # Exemple : "22h04, ce n'est plus l'heure ! ❌..."
            message = f"{heure_exacte}, {suffixe}"
            
            api.create_tweet(text=message[:280])
            print(f"✅ Tweet posté : {message}")
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
        
