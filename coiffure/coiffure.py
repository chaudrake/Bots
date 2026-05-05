# Script pour tweeter un salon de coiffure par jour
# Adapté pour GitHub Actions
import tweepy
import os
import sys
import time
import random
from datetime import datetime
import pytz

# Récupérer les variables d'environnement (GitHub Secrets)
CONSUMER_KEY = os.getenv('COIFFURE_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('COIFFURE_CONSUMER_SECRET')
ACCESS_KEY = os.getenv('COIFFURE_ACCESS_KEY')
ACCESS_SECRET = os.getenv('COIFFURE_ACCESS_SECRET')

# Vérification des credentials
if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]):
    print("❌ Missing Twitter API credentials")
    sys.exit(1)

print("🚀 Lancement du bot Coiffure")

france_tz = pytz.timezone('Europe/Paris')

def is_summer_time():
    """Détecte l'heure d'été (UTC+2)"""
    now = datetime.now(france_tz)
    return now.utcoffset() == pytz.FixedOffset(120)

def wait_for_winter_adjustment():
    """Si on est en hiver, attend 1 heure pour caler l'heure française"""
    if not is_summer_time():
        print("❄️ Heure d'hiver détectée - attente de 1 heure")
        time.sleep(3600)
        print("✅ Reprise après attente")
    else:
        print("☀️ Heure d'été - exécution immédiate")

def get_post_content(block_number):
    """Récupère le contenu du tweet à partir du fichier liste.txt"""
    with open('liste.txt', 'r', encoding='utf-8') as file:
        blocks = file.read().split('\n\n')
        if block_number >= len(blocks):
            block_number = 0
        return f"Le salon de coiffure du jour :\n\n{blocks[block_number].strip()}\n\n#SalonDeCoiffure #Coiffure"

def create_twitter_client():
    """Crée et retourne le client Twitter"""
    try:
        return tweepy.Client(
            access_token=ACCESS_KEY,
            access_token_secret=ACCESS_SECRET,
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET
        )
    except Exception as e:
        print(f"❌ Erreur lors de la création du client Twitter : {e}")
        return None

def read_block_number():
    """Lit l'index depuis le fichier"""
    if os.path.exists('index.txt'):
        with open('index.txt', 'r', encoding='utf-8') as index_file:
            try:
                return int(index_file.read().strip())
            except ValueError:
                return 0
    return 0

def update_block_number(block_number):
    """Met à jour l'index après un tweet réussi"""
    block_number += 1
    with open('liste.txt', 'r', encoding='utf-8') as file:
        total_blocks = len(file.read().split('\n\n'))
    if block_number >= total_blocks:
        block_number = 0
        print("🔄 Tous les salons ont été tweetés, retour au début")
    with open('index.txt', 'w', encoding='utf-8') as index_file:
        index_file.write(str(block_number))
    return block_number

def post_tweet(api, content):
    """Publie le tweet"""
    try:
        tweet = api.create_tweet(text=content[:280])
        print(f"✅ Tweet posté : ID={tweet.data['id']}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la publication : {e}")
        return False

def main():
    # Ajustement pour l'heure d'hiver
    wait_for_winter_adjustment()
    
    now_fr = datetime.now(france_tz)
    print(f"🕐 Heure française: {now_fr.strftime('%H:%M:%S')}")
    
    api = create_twitter_client()
    if not api:
        print("❌ Impossible de créer le client Twitter")
        sys.exit(1)
    
    block_number = read_block_number()
    print(f"📌 Index actuel: {block_number}")
    
    content = get_post_content(block_number)
    print(f"📝 Contenu: {content[:100]}...")
    
    if post_tweet(api, content):
        new_index = update_block_number(block_number)
        print(f"✅ Tweet posté avec succès - Nouvel index: {new_index}")
    else:
        print("❌ Échec de la publication")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

print("🏁 Opération terminée")
