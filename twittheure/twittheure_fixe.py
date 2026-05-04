import tweepy
import os
import sys
from datetime import datetime
import pytz

# Récupérer les variables d'environnement
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

print('🚀 Lancement du bot TwittHeure (heures fixes)')

france_tz = pytz.timezone('Europe/Paris')

def post_tweet(text):
    try:
        client.create_tweet(text=text[:280])
        print(f"✅ Tweet publié: {text}")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def get_tweeted_fixed():
    if os.path.exists('tweeted_fixed.txt'):
        with open('tweeted_fixed.txt', 'r', encoding='utf-8') as f:
            return set(f.read().splitlines())
    return set()

def save_tweeted_fixed(hour_str):
    with open('tweeted_fixed.txt', 'a', encoding='utf-8') as f:
        f.write(hour_str + '\n')

def reset_fixed():
    if os.path.exists('tweeted_fixed.txt'):
        os.remove('tweeted_fixed.txt')

def check_and_reset_day():
    current_day = datetime.now(france_tz).strftime('%Y-%m-%d')
    last_day_file = 'last_day_fixed.txt'
    
    if os.path.exists(last_day_file):
        with open(last_day_file, 'r', encoding='utf-8') as f:
            last_day = f.read().strip()
        if last_day != current_day:
            print(f"📅 Nouveau jour ({current_day}), réinitialisation...")
            reset_fixed()
            with open(last_day_file, 'w', encoding='utf-8') as f:
                f.write(current_day)
    else:
        with open(last_day_file, 'w', encoding='utf-8') as f:
            f.write(current_day)

def main():
    current_time = datetime.now(france_tz)
    current_time_str = current_time.strftime('%H:%M')
    
    print(f"🕐 Heure actuelle (France): {current_time.strftime('%H:%M:%S')}")
    
    check_and_reset_day()
    tweeted_fixed = get_tweeted_fixed()
    
    if current_time_str == "00:00":
        if "00:00" not in tweeted_fixed:
            post_tweet("00:00")
            save_tweeted_fixed("00:00")
        return
    
    if current_time_str == "11:11":
        if "11:11" not in tweeted_fixed:
            post_tweet("11:11")
            save_tweeted_fixed("11:11")
        return
    
    if current_time_str == "22:22":
        if "22:22" not in tweeted_fixed:
            post_tweet("22:22")
            save_tweeted_fixed("22:22")
        return

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)
