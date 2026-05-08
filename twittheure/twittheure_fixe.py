# le bot tweete à 11h11, 21h22 et 00h00
# lancements par cron
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

france_tz = pytz.timezone('Europe/Paris')

def wait_until_target(target_hour, target_minute):
    """Attend précisément jusqu'à l'heure cible (heure française)
    Retourne True si on a attendu et qu'on peut tweeter, False si trop long"""
    now = datetime.now(france_tz)
    target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    if target <= now:
        print(f"⚠️ Heure cible {target_hour:02d}:{target_minute:02d} déjà passée")
        return False
    
    wait_seconds = (target - now).total_seconds()
    
    print(f"🕐 Heure courante (FR): {now.strftime('%H:%M:%S')}")
    print(f"🎯 Heure cible: {target_hour:02d}:{target_minute:02d}")
    print(f"⏳ Attente de {wait_seconds:.0f} secondes...")
    
    # Si attente trop longue, on abandonne sans faire échouer le workflow
    if wait_seconds > 21600:  # 6 heures
        print("⚠️ Attente trop longue (>6h), abandon sans erreur pour éviter timeout GitHub")
        return False
    
    time.sleep(wait_seconds)
    print(f"✅ Il est maintenant {target_hour:02d}:{target_minute:02d} !")
    return True

def post_tweet():
    """Poste l'heure actuelle"""
    now = datetime.now(france_tz)
    current_time_str = now.strftime('%H:%M')
    
    try:
        client.create_tweet(text=current_time_str)
        print(f"✅ Tweet envoyé : {current_time_str}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du tweet : {e}")
        return False

def main():
    target_times_str = os.getenv('TARGET_TIMES', '')
    if not target_times_str:
        print("❌ Variable TARGET_TIMES manquante")
        sys.exit(1)
    
    # Parse les horaires cibles (format "22:22,00:00" ou "11:11")
    target_times = []
    for part in target_times_str.split(','):
        part = part.strip()
        if ':' in part:
            h, m = part.split(':')
            target_times.append((int(h), int(m)))
    
    print(f"📌 Horaires cibles: {target_times}")
    
    for hour, minute in target_times:
        print(f"\n--- Préparation du tweet pour {hour:02d}:{minute:02d} ---")
        
        if wait_until_target(hour, minute):
            if not post_tweet():
                print(f"⚠️ Échec du tweet pour {hour:02d}:{minute:02d}")
        else:
            print(f"⏭️ Ignoré l'horaire {hour:02d}:{minute:02d}")
    
    print("🏁 Opération terminée")
    sys.exit(0)  # Sortie toujours en succès

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(0)  # ← Même erreur inattendue = sortie 0, pas d'email
