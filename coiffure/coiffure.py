# Script pour tweeter un salon de coiffure par jour
# Adapté pour GitHub Actions - version simple
import tweepy
import os
import sys
from datetime import datetime
import pytz

# Récupérer les variables d'environnement (GitHub Secrets)
CONSUMER_KEY = os.getenv('COIFFURE_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('COIFFURE_CONSUMER_SECRET')
ACCESS_KEY = os.getenv('COIFFURE_ACCESS_KEY')
ACCESS_SECRET = os.getenv('COIFFURE_ACCESS_SECRET')

if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]):
    print("❌ Missing Twitter API credentials")
    sys.exit(1)

print("🚀 Lancement du bot Coiffure")

france_tz = pytz.timezone('Europe/Paris')

def get_post_content(block_number):
    with open('liste.txt', 'r', encoding='utf-8') as file:
        blocks = file.read().split('\n\n')
        if block_number >= len(blocks):
            block_number = 0
        return f"Le salon de coiffure du jour :\n\n{blocks[block_number].strip()}\n\n#SalonDeCoiffure #Coiffure"

def create_twitter_client():
    return tweepy.Client(
        access_token=ACCESS_KEY,
        access_token_secret=ACCESS_SECRET,
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET
    )

def read_block_number():
    if os.path.exists('index.txt'):
        with open('index.txt', 'r', encoding='utf-8') as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return 0
    return 0

def update_block_number(block_number):
    block_number += 1
    with open('liste.txt', 'r', encoding='utf-8') as f:
        total_blocks = len(f.read().split('\n\n'))
    if block_number >= total_blocks:
        block_number = 0
        print("🔄 Tous les salons ont été tweetés, retour au début")
    with open('index.txt', 'w', encoding='utf-8') as f:
        f.write(str(block_number))
    return block_number

def main():
    now = datetime.now(france_tz)
    print(f"🕐 Heure française: {now.strftime('%H:%M:%S')}")
    
    api = create_twitter_client()
    block_number = read_block_number()
    print(f"📌 Index actuel: {block_number}")
    
    content = get_post_content(block_number)
    print(f"📝 Contenu: {content[:100]}...")
    
    try:
        tweet = api.create_tweet(text=content[:280])
        print(f"✅ Tweet posté : ID={tweet.data['id']}")
        new_index = update_block_number(block_number)
        print(f"✅ Nouvel index: {new_index}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

print("🏁 Opération terminée")
