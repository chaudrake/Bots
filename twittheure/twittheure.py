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

# Fuseau horaire France (gère automatiquement été/hiver)
france_tz = pytz.timezone('Europe/Paris')

def get_france_time():
    """Retourne l'heure actuelle en France (été/hiver automatique)"""
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
    """Publie un tweet"""
    try:
        client.create_tweet(text=text[:280])
        print(f"✅ Tweet publié: {text}")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

# Gestion des heures déjà tweetées aujourd'hui
def get_tweeted_fixed():
    """Récupère les heures fixes déjà tweetées aujourd'hui"""
    if os.path.exists('tweeted_fixed.txt'):
        with open('tweeted_fixed.txt', 'r', encoding='utf-8') as f:
            return set(f.read().splitlines())
    return set()

def get_tweeted_random_count():
    """Récupère le nombre d'heures aléatoires déjà tweetées aujourd'hui"""
    if os.path.exists('tweeted_random.txt'):
        with open('tweeted_random.txt', 'r', encoding='utf-8') as f:
            return len(f.read().splitlines())
    return 0

def save_tweeted_fixed(hour_str):
    """Sauvegarde une heure fixe tweetée"""
    with open('tweeted_fixed.txt', 'a', encoding='utf-8') as f:
        f.write(hour_str + '\n')

def save_tweeted_random():
    """Sauvegarde qu'un tweet aléatoire a été fait"""
    with open('tweeted_random.txt', 'a', encoding='utf-8') as f:
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M') + '\n')

def reset_files():
    """Réinitialise les fichiers"""
    if os.path.exists('tweeted_fixed.txt'):
        os.remove('tweeted_fixed.txt')
    if os.path.exists('tweeted_random.txt'):
        os.remove('tweeted_random.txt')

def check_and_reset_day():
    """Vérifie si on a changé de jour et réinitialise si nécessaire"""
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
    current_time_str = current_time.strftime('%H:%M')
    
    print(f"🕐 Heure actuelle (France): {current_time.strftime('%H:%M:%S')}")
    
    check_and_reset_day()
    tweeted_fixed = get_tweeted_fixed()
    
    # === TWEETS FIXES (00h00, 11h11, 22h22) ===
    
    if current_time_str == "00:00":
        if "00:00" not in tweeted_fixed:
            post_tweet("00:00")
            save_tweeted_fixed("00:00")
            print("✅ Tweet 00:00 posté")
        return
    
    if current_time_str == "11:11":
        if "11:11" not in tweeted_fixed:
            post_tweet("11:11")
            save_tweeted_fixed("11:11")
            print("✅ Tweet 11:11 posté")
        return
    
    if current_time_str == "22:22":
        if "22:22" not in tweeted_fixed:
            post_tweet("22:22")
            save_tweeted_fixed("22:22")
            print("✅ Tweet 22:22 posté")
        return
    
    # === TWEETS ALÉATOIRES (max 3 par jour, entre 6h et 22h) ===
    
    # Vérifier plage horaire 6h-22h
    if not (6 <= current_hour <= 21):
        print("🌙 En dehors de la plage 6h-22h, pas de tweet aléatoire")
        return
    
    random_count = get_tweeted_random_count()
    
    if random_count >= 3:
        print(f"✅ Déjà {random_count}/3 tweets aléatoires aujourd'hui")
        return
    
    # On tweete à chaque passage du cron (toutes les 10 min)
    # Mais limité par le compteur à 3 par jour
    tweet_text = generate_random_hour_tweet()
    if post_tweet(tweet_text):
        save_tweeted_random()
        print(f"✅ Heure aléatoire tweetée ({random_count + 1}/3): {tweet_text}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

print("🏁 Opération terminée")
