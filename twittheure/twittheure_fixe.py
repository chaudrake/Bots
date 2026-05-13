# le bot tweete à 11h11, 22h22 et 00h00
# lancements par cron - corrigé pour gérer le passage à minuit

import tweepy
import os
import sys
import time
import pytz
from datetime import datetime, timedelta

# Configuration Twitter
CONSUMER_KEY = os.getenv('THeure_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('THeure_CONSUMER_SECRET')
ACCESS_KEY = os.getenv('THeure_ACCESS_KEY')
ACCESS_SECRET = os.getenv('THeure_ACCESS_SECRET')

france_tz = pytz.timezone('Europe/Paris')

def get_twitter_client():
    return tweepy.Client(
        access_token=ACCESS_KEY,
        access_token_secret=ACCESS_SECRET,
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET
    )

def wait_until_target(target_hour, target_minute):
    now = datetime.now(france_tz)
    target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    # Si la cible est minuit et qu'il est tard le soir, c'est pour le lendemain
    if target_hour == 0 and now.hour >= 22:
        target += timedelta(days=1)
    
    # Si l'heure est déjà passée de plus d'une minute, on ne traite pas
    if target < (now - timedelta(minutes=1)):
        return False

    wait_seconds = (target - now).total_seconds()
    
    if wait_seconds < 0: # On est dans la minute même
        wait_seconds = 0

    print(f"🕐 Heure actuelle : {now.strftime('%H:%M:%S')}")
    print(f"🎯 Cible détectée : {target_hour:02d}:{target_minute:02d}")
    
    if wait_seconds > 7200: # Sécurité : n'attend pas plus de 2h
        print("⚠️ Cible trop lointaine, le script s'arrête pour économiser les ressources.")
        return False
    
    print(f"⏳ Attente de {wait_seconds:.0f} secondes...")
    time.sleep(wait_seconds)
    return True

def post_tweet():
    now = datetime.now(france_tz)
    current_time_str = now.strftime('%H:%M')
    try:
        client = get_twitter_client()
        client.create_tweet(text=current_time_str)
        print(f"✅ Tweet envoyé : {current_time_str}")
        return True
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False

def main():
    if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]):
        print("❌ Credentials manquants")
        sys.exit(1)

    # Définition des paliers
    paliers = [(11, 11), (22, 22), (0, 0)]
    now = datetime.now(france_tz)
    
    cible_retenue = None
    
    for h, m in paliers:
        target_dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if h == 0 and now.hour >= 22:
            target_dt += timedelta(days=1)
            
        # On prend le premier palier qui n'est pas encore passé
        if now < (target_dt + timedelta(seconds=10)):
            cible_retenue = (h, m)
            break

    if cible_retenue:
        h, m = cible_retenue
        if wait_until_target(h, m):
            post_tweet()
    else:
        print("Commutation : Aucune cible proche trouvée.")

if __name__ == "__main__":
    main()
    
