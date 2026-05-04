import tweepy
import os
import sys
import random
import json
from datetime import datetime
import pytz

# Récupérer les variables d'environnement (GitHub Secrets)
CONSUMER_KEY = os.getenv('THeure_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('THeure_CONSUMER_SECRET')
ACCESS_KEY = os.getenv('THeure_ACCESS_KEY')
ACCESS_SECRET = os.getenv('THeure_ACCESS_SECRET')

# Vérification des credentials
if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]):
    print("❌ Missing Twitter API credentials")
    sys.exit(1)

# Créer un client Tweepy
client = tweepy.Client(
    access_token=ACCESS_KEY,
    access_token_secret=ACCESS_SECRET,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET
)

print('🚀 Lancement du bot TwittHeure')

# Fuseau horaire France
france_tz = pytz.timezone('Europe/Paris')

def get_france_time():
    return datetime.now(france_tz)

def generate_random_hour_tweet():
    """Génère un tweet d'heure aléatoire avec Tracery"""
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

def get_tweeted_fixed():
    if os.path.exists('tweeted_fixed.txt'):
        with open('tweeted_fixed.txt', 'r', encoding='utf-8') as f:
            return set(f.read().splitlines())
    return set()

def get_tweeted_random_count():
    if os.path.exists('tweeted_random.txt'):
        with open('tweeted_random.txt', 'r', encoding='utf-8') as f:
            return len(f.read().splitlines())
    return 0

def save_tweeted_fixed(hour_str):
    with open('tweeted_fixed.txt', 'a', encoding='utf-8') as f:
        f.write(hour_str + '\n')

def save_tweeted_random():
    with open('tweeted_random.txt', 'a', encoding='utf-8') as f:
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M') + '\n')

def reset_files():
    if os.path.exists('tweeted_fixed.txt'):
        os.remove('tweeted_fixed.txt')
    if os.path.exists('tweeted_random.txt'):
        os.remove('tweeted_random.txt')

def check_and_reset_day():
    current_day = get_france_time().strftime('%Y-%m-%d')
    last_day_file = 'last_day.txt'
    
    if os.path.exists(last_day_file):
        with open(last_day_file, 'r', encoding='utf-8') as f:
            last_day = f.read().strip()
        if last_day != current_day:
            print(f"📅 Nouveau jour ({current_day}), réinitialisation...")
            reset_files()
            with open(last_day_file, 'w', encoding='utf-8') as f:
                f.write(current_day)
    else:
        with open(last_day_file, 'w', encoding='utf-8') as f:
            f.write(current_day)

def main():
    current_time = get_france_time()
    current_hour = current_time.hour
    current_minute = current_time.minute
    
    print(f"🕐 Heure actuelle (France): {current_time.strftime('%H:%M:%S')}")
    
    check_and_reset_day()
    tweeted_fixed = get_tweeted_fixed()
    
    # === TWEETS FIXES (prioritaires) ===
    
    # 00h00
    if current_hour == 0 and current_minute == 0:
        if "00:00" not in tweeted_fixed:
            post_tweet("00:00")
            save_tweeted_fixed("00:00")
            print("✅ Tweet 00:00 posté")
        return
    
    # 11h11
    if current_hour == 11 and current_minute == 11:
        if "11:11" not in tweeted_fixed:
            post_tweet("11:11")
            save_tweeted_fixed("11:11")
            print("✅ Tweet 11:11 posté")
        return
    
    # 22h22
    if current_hour == 22 and current_minute == 22:
        if "22:22" not in tweeted_fixed:
            post_tweet("22:22")
            save_tweeted_fixed("22:22")
            print("✅ Tweet 22:22 posté")
        return
    
    # === TWEETS ALÉATOIRES (max 3 par jour, entre 6h et 22h) ===
    
    # Vérifier si on est dans la plage 6h-22h
    if not (6 <= current_hour <= 21):
        print("🌙 En dehors de la plage 6h-22h, pas de tweet aléatoire")
        return
    
    # Compter combien de tweets aléatoires déjà faits aujourd'hui
    random_count = get_tweeted_random_count()
    
    if random_count >= 3:
        print(f"✅ Déjà {random_count}/3 tweets aléatoires aujourd'hui")
        return
    
    # Probabilité de tweeter à cette exécution
    # On veut en moyenne 3 tweets sur une plage de 16h (6h-22h) = 960 minutes
    # On exécute toutes les 5 minutes = 192 exécutions possibles
    # 3 / 192 = 1.56% de chance à chaque exécution (un peu plus pour être sûr)
    chance = 0.03  # 3% de chance = environ 5-6 tweets par jour, puis filtré par le compteur
    
    if random.random() < chance:
        tweet_text = generate_random_hour_tweet()
        if post_tweet(tweet_text):
            save_tweeted_random()
            print(f"✅ Heure aléatoire tweetée ({random_count + 1}/3): {tweet_text}")
    else:
        print(f"⏭️ Pas de tweet aléatoire cette fois (chance: {chance*100}%)")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

print("🏁 Opération terminée")
