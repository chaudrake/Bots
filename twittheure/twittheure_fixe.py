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

if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]):
    print("❌ Missing Twitter API credentials")
    sys.exit(1)

client = tweepy.Client(
    access_token=ACCESS_KEY,
    access_token_secret=ACCESS_SECRET,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET
)

print("🚀 Lancement du bot TwittHeure (avec synchronisation précise)")

france_tz = pytz.timezone('Europe/Paris')

def wait_until_target(target_hour, target_minute):
    """Attend précisément jusqu'à l'heure cible (heure française)"""
    now = datetime.now(france_tz)
    target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    # Si l'heure cible est déjà passée, on ne fait rien (le cron est trop tard)
    if target <= now:
        print(f"⚠️ Heure cible {target_hour:02d}:{target_minute:02d} déjà passée (il est {now.strftime('%H:%M:%S')})")
        print("🛑 Annulation du job - le prochain cron s'en chargera demain")
        sys.exit(0)  # Sortie propre, pas d'erreur
    
    wait_seconds = (target - now).total_seconds()
    
    print(f"🕐 Heure courante (FR): {now.strftime('%H:%M:%S')}")
    print(f"🎯 Heure cible: {target_hour:02d}:{target_minute:02d}")
    print(f"⏳ Attente de {wait_seconds:.0f} secondes...")
    
    # GitHub Actions timeout à 6h minimum, on vérifie qu'on attend pas trop longtemps
    if wait_seconds > 21600:  # 6 heures
        print("❌ Attente trop longue (>6h), abandon pour éviter timeout GitHub")
        sys.exit(1)
    
    time.sleep(wait_seconds)
    
    print(f"✅ Il est maintenant {target_hour:02d}:{target_minute:02d} !")
    
def main():
    # Déterminer l'heure cible en fonction du cron qui a été déclenché
    # On reçoit l'heure cible via variable d'environnement
    target_hour = int(os.getenv('TARGET_HOUR', '0'))
    target_minute = int(os.getenv('TARGET_MINUTE', '0'))
    
    print(f"📌 Mode: tweeter à {target_hour:02d}:{target_minute:02d} (heure française)")
    
    # Attendre précisément l'heure cible
    wait_until_target(target_hour, target_minute)
    
    # Tweeter
    now = datetime.now(france_tz)
    current_time_str = now.strftime('%H:%M')
    
    print(f"🕐 Heure française: {current_time_str}")
    
    try:
        client.create_tweet(text=current_time_str)
        print(f"✅ Tweet envoyé : {current_time_str}")
    except Exception as e:
        print(f"❌ Erreur lors du tweet : {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

print("🏁 Opération terminée")
