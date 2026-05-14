import os
import tweepy
import requests
import random
from io import BytesIO
from PIL import Image
from time import sleep
import sys

# 1. Tirage aléatoire : 1 chance sur 3 environ
if random.random() > 0.933:
    print("Le tirage n'a pas été retenu. Sunbot passe son tour.")
    sys.exit(0)

# 2. Pause aléatoire entre 10 secondes et 10 minutes (600s)
# Cela permet de décaler le tweet par rapport à l'heure du cron
wait_time = random.randint(10, 600)
print(f"Sunbot s'exécute. Pause de {wait_time} secondes avant le tweet...")
sleep(wait_time)

# --- Configuration et Tweet ---

CONSUMER_KEY = os.getenv('SUNBOT_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('SUNBOT_CONSUMER_SECRET')
ACCESS_KEY = os.getenv('SUNBOT_ACCESS_KEY')
ACCESS_SECRET = os.getenv('SUNBOT_ACCESS_SECRET')
UNSPLASH_ACCESS_KEY = os.getenv('SUNBOT_UNSPLASH_ACCESS_KEY')

client = tweepy.Client(
    access_token=ACCESS_KEY,
    access_token_secret=ACCESS_SECRET,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET
)

auth = tweepy.OAuth1UserHandler(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_KEY,
    access_token_secret=ACCESS_SECRET
)
api = tweepy.API(auth)

def get_photo_from_unsplash():
    try:
        query = random.choice(["sun", "soleil"])
        url = f'https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_ACCESS_KEY}&w=1200&h=1200'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['urls']['regular']
    except Exception as e:
        print(f'Erreur Unsplash: {e}')
        return None

def tweet_photo(text):
    try:
        photo_url = get_photo_from_unsplash()
        if photo_url:
            response = requests.get(photo_url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            img_path = 'temp.jpg'
            img.save(img_path)

            media = api.media_upload(img_path)
            client.create_tweet(text=text, media_ids=[media.media_id])
            
            if os.path.exists(img_path):
                os.remove(img_path)
            print(f"Photo postée : {text}")
        else:
            print("Pas d'image disponible.")
    except Exception as e:
        print(f'Erreur : {e}')

if __name__ == "__main__":
    tweet_photo("#Sun #Sunset #Soleil")
