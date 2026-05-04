import tweepy
import os
import sys
import random
from datetime import datetime, time as dt_time
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

def post_tweet(text):
    """Publie un tweet"""
    try:
        tweet = client.create_tweet(text=text[:280])
        print(f"✅ Tweet publié: {text}")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def should_tweet_at_11h11(current_time):
    """Vérifie s'il est 11h11"""
    return current_time.hour == 11 and current_time.minute == 11

def should_tweet_at_22h22(current_time):
    """Vérifie s'il est 22h22"""
    return current_time.hour == 22 and current_time.minute == 22

# Gestion des heures aléatoires déjà tweetées aujourd'hui
def get_tweeted_random_hours():
    """Récupère la liste des heures aléatoires déjà tweetées aujourd'hui"""
    if os.path.exists('random_hours.txt'):
        with open('random_hours.txt', 'r', encoding='utf-8') as f:
            return set(f.read().splitlines())
    return set()

def save_tweeted_random_hour(hour_str):
    """Sauvegarde une heure aléatoire tweetée"""
    with open('random_hours.txt', 'a', encoding='utf-8') as f:
        f.write(hour_str + '\n')

def reset_random_hours():
    """Réinitialise le fichier des heures aléatoires (nouveau jour)"""
    if os.path.exists('random_hours.txt'):
        os.remove('random_hours.txt')

def get_tweeted_hours_today():
    """Récupère toutes les heures déjà tweetées aujourd'hui"""
    if os.path.exists('tweeted_hours.txt'):
        with open('tweeted_hours.txt', 'r', encoding='utf-8') as f:
            return set(f.read().splitlines())
    return set()

def save_tweeted_hour(hour_str):
    """Sauvegarde une heure tweetée"""
    with open('tweeted_hours.txt', 'a', encoding='utf-8') as f:
        f.write(hour_str + '\n')

def reset_tweeted_hours():
    """Réinitialise le fichier des heures tweetées (nouveau jour)"""
    if os.path.exists('tweeted_hours.txt'):
        os.remove('tweeted_hours.txt')

# Gestion du jour
def get_current_day():
    """Retourne le jour actuel (YYYY-MM-DD) pour savoir si on a déjà tweeté aujourd'hui"""
    return get_france_time().strftime('%Y-%m-%d')

def check_and_reset_day():
    """Vérifie si on a changé de jour et réinitialise si nécessaire"""
    current_day = get_current_day()
    last_day_file = 'last_day.txt'
    
    if os.path.exists(last_day_file):
        with open(last_day_file, 'r', encoding='utf-8') as f:
            last_day = f.read().strip()
        if last_day != current_day:
            print(f"📅 Nouveau jour ({current_day}), réinitialisation...")
            reset_random_hours()
            reset_tweeted_hours()
            with open(last_day_file, 'w', encoding='utf-8') as f:
                f.write(current_day)
    else:
        with open(last_day_file, 'w', encoding='utf-8') as f:
            f.write(current_day)

def generate_random_tweet_time():
    """Génère une heure aléatoire entre 6h et 22h (heures pleines uniquement)"""
    # Plage horaire : 6h à 21h (car 22h est déjà utilisé pour le tweet fixe)
    random_hour = random.randint(6, 21)
    random_minute = random.choice([0, 15, 30, 45])  # Quart d'heure
    return random_hour, random_minute

def main():
    current_time = get_france_time()
    current_hour = current_time.hour
    current_minute = current_time.minute
    current_day = current_time.strftime('%Y-%m-%d')
    
    print(f"🕐 Heure actuelle (France): {current_time.strftime('%H:%M:%S')}")
    
    # Vérifier et réinitialiser au début du nouveau jour
    check_and_reset_day()
    
    tweeted_hours = get_tweeted_hours_today()
    tweeted_random = get_tweeted_random_hours()
    
    # === TWEET FIXE 11h11 ===
    if should_tweet_at_11h11(current_time):
        if "11:11" not in tweeted_hours:
            tweet_text = f"11:11"
            if post_tweet(tweet_text):
                save_tweeted_hour("11:11")
                print("✅ Tweet 11:11 posté")
        else:
            print("⚠️ 11:11 déjà tweeté aujourd'hui")
    
    # === TWEET FIXE 22h22 ===
    elif should_tweet_at_22h22(current_time):
        if "22:22" not in tweeted_hours:
            tweet_text = f"22:22"
            if post_tweet(tweet_text):
                save_tweeted_hour("22:22")
                print("✅ Tweet 22:22 posté")
        else:
            print("⚠️ 22:22 déjà tweeté aujourd'hui")
    
    # === TWEETS HEURES ALÉATOIRES (max 3 par jour) ===
    else:
        # Vérifier si on a déjà tweeté 3 heures aléatoires aujourd'hui
        if len(tweeted_random) >= 3:
            print(f"✅ Déjà {len(tweeted_random)} heures aléatoires tweetées aujourd'hui, aucun tweet supplémentaire")
        else:
            # Vérifier si on est dans la plage horaire 6h-22h
            if 6 <= current_hour <= 21:
                # Génération de la cible (quart d'heure le plus proche)
                # On tweete aux heures fixes : xx:00, xx:15, xx:30, xx:45
                target_minute = (current_minute // 15) * 15
                tweet_hour = current_hour
                tweet_minute = target_minute
                
                # Formater l'heure cible
                time_str = f"{tweet_hour:02d}:{tweet_minute:02d}"
                random_id = f"{current_day}_{time_str}"
                
                # Vérifier si cette heure n'a pas déjà été tweetée aujourd'hui
                if random_id not in tweeted_random:
                    tweet_text = f"Il n'est pas {time_str}"
                    if post_tweet(tweet_text):
                        save_tweeted_random_hour(random_id)
                        print(f"✅ Heure aléatoire tweetée: {time_str}")
                else:
                    print(f"⚠️ Heure {time_str} déjà tweetée aujourd'hui")
            else:
                print("🌙 En dehors de la plage 6h-22h, pas de tweet aléatoire")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

print("🏁 Opération terminée")
