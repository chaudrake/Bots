import tweepy
import os
import sys
import random
import json
from datetime import datetime
import pytz

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

print('🚀 Lancement du bot TwittHeure (heures aléatoires)')

france_tz = pytz.timezone('Europe/Paris')

def generate_random_hour_tweet():
    try:
        with open("bot.json", 'r', encoding="utf-8") as f:
            grammar_data = json.load(f)
        random_hour = random.choice(grammar_data["heures"])
        random_minute = random.choice(grammar_data["minutes"])
        return f"Il n'est pas {random_hour}h{random_minute}"
    except Exception as e:
        print(f"❌ Erreur Tracery: {e}")
        return "Il n'est pas midi"

def post_tweet(text):
    try:
        client.create_tweet(text=text[:280])
        print(f"✅ Tweet publié: {text}")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def get_tweeted_random_count():
    if os.path.exists('tweeted_random.txt'):
        with open('tweeted_random.txt', 'r', encoding='utf-8') as f:
            return len(f.read().splitlines())
    return 0

def save_tweeted_random():
    with open('tweeted_random.txt', 'a', encoding='utf-8') as f:
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M') + '\n')

def reset_random():
    if os.path.exists('tweeted_random.txt'):
        os.remove('tweeted_random.txt')

def check_and_reset_day():
    current_day = datetime.now(france_tz).strftime('%Y-%m-%d')
    last_day_file = 'last_day_random.txt'
    
    if os.path.exists(last_day_file):
        with open(last_day_file, 'r', encoding='utf-8') as f:
            last_day = f.read().strip()
        if last_day != current_day:
            print(f"📅 Nouveau jour ({current_day}), réinitialisation...")
            reset_random()
            with open(last_day_file, 'w', encoding='utf-8') as f:
                f.write(current_day)
    else:
        with open(last_day_file, 'w', encoding='utf-8') as f:
            f.write(current_day)

def main():
    current_time = datetime.now(france_tz)
    current_hour = current_time.hour
    
    print(f"🕐 Heure actuelle (France): {current_time.strftime('%H:%M:%S')}")
    
    check_and_reset_day()
    
    # Plage 6h-22h
    if not (6 <= current_hour <= 21):
        print("🌙 En dehors de la plage 6h-22h")
        return
    
    random_count = get_tweeted_random_count()
    
    if random_count >= 3:
        print(f"✅ Déjà {random_count}/3 tweets aléatoires aujourd'hui")
        return
    
    # Probabilité : 3 tweets sur ~90 exécutions (toutes les 10 min sur 16h = 96 exécutions)
    # 3/96 = 3.1%
    if random.random() < 0.03:
        tweet_text = generate_random_hour_tweet()
        if post_tweet(tweet_text):
            save_tweeted_random()
            print(f"✅ Heure aléatoire tweetée ({random_count + 1}/3)")
    else:
        print("⏭️ Pas de tweet aléatoire cette fois")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

print("🏁 Terminé")
