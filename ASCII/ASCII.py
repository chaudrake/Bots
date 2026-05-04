# Créer les images ASCII sur https://www.text-image.com/
# Adapté pour GitHub Actions
import tweepy
import os
import sys
import requests
import random
from urllib.parse import unquote, urlparse

# Récupérer les variables d'environnement (GitHub Secrets)
CONSUMER_KEY = os.getenv('ASCII_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('ASCII_CONSUMER_SECRET')
ACCESS_KEY = os.getenv('ASCII_ACCESS_KEY')
ACCESS_SECRET = os.getenv('ASCII_ACCESS_SECRET')
BEARER_TOKEN = os.getenv('ASCII_BEARER_TOKEN')

# Vérification des credentials
if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]):
    print("❌ Missing Twitter API credentials")
    sys.exit(1)

# URL de base de votre dépôt GitHub (à adapter)
GITHUB_BASE_URL = "https://raw.githubusercontent.com/chaudrake/ASCII/main/"

def download_image_from_url(url, local_path):
    """Télécharge une image depuis une URL"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with open(local_path, 'wb') as f:
            f.write(response.content)

        print(f"✅ Image téléchargée: {local_path}")
        return True
    except Exception as e:
        print(f"❌ Erreur de téléchargement: {e}")
        return False

def get_image_urls():
    """Retourne la liste de toutes les URLs d'images depuis le fichier"""
    image_list_file = "image_list.txt"
    image_urls = []

    if not os.path.exists(image_list_file):
        print(f"❌ Fichier {image_list_file} non trouvé!")
        return []

    try:
        with open(image_list_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    image_urls.append(GITHUB_BASE_URL + line)

        print(f"📋 {len(image_urls)} images chargées depuis {image_list_file}")
        return image_urls

    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier {image_list_file}: {e}")
        return []

def get_tweeted_urls():
    """Lit la liste des URLs déjà tweetées"""
    index_file = "tweeted_urls.txt"
    if not os.path.exists(index_file):
        return set()

    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    except:
        return set()

def save_tweeted_url(url):
    """Ajoute une URL à la liste des images tweetées"""
    index_file = "tweeted_urls.txt"
    with open(index_file, 'a', encoding='utf-8') as f:
        f.write(f"{url}\n")

def reset_index_if_needed(image_urls, tweeted_urls):
    """Réinitialise l'index si toutes les images ont été tweetées"""
    if len(tweeted_urls) >= len(image_urls) and image_urls:
        print("🔄 Toutes les images ont été tweetées ! Réinitialisation...")
        if os.path.exists("tweeted_urls.txt"):
            os.remove("tweeted_urls.txt")
        return set()
    return tweeted_urls

def get_next_image(directory="img"):
    """Choisit une image non tweetée au hasard"""
    if not os.path.exists(directory):
        os.makedirs(directory)

    image_urls = get_image_urls()
    tweeted_urls = get_tweeted_urls()
    tweeted_urls = reset_index_if_needed(image_urls, tweeted_urls)

    if not image_urls:
        print("❌ Aucune image disponible")
        return None

    available_urls = [url for url in image_urls if url not in tweeted_urls]

    if not available_urls:
        print("❌ Aucune image non tweetée disponible")
        return None

    chosen_url = random.choice(available_urls)
    image_filename = os.path.basename(chosen_url)
    image_path = os.path.join(directory, image_filename)

    if download_image_from_url(chosen_url, image_path):
        save_tweeted_url(chosen_url)
        print(f"📌 Image ajoutée à l'index: {image_filename}")
        return image_path

    return None

def manage_storage(directory="img", max_local_files=3):
    """Garde seulement les max_local_files fichiers les plus récents"""
    try:
        if not os.path.exists(directory):
            return
            
        images = [f for f in os.listdir(directory)
                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

        if len(images) > max_local_files:
            images.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)))
            for old_image in images[:-max_local_files]:
                os.remove(os.path.join(directory, old_image))
                print(f"🗑️ Fichier supprimé: {old_image}")
    except Exception as e:
        print(f"⚠️ Erreur lors du nettoyage: {e}")

def tweet_image(image_path, message=""):
    """Fonction pour tweeter une image"""
    auth = tweepy.OAuth1UserHandler(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_KEY,
        access_token_secret=ACCESS_SECRET
    )
    api_v1 = tweepy.API(auth)

    client = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_KEY,
        access_token_secret=ACCESS_SECRET
    )

    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image non trouvée: {image_path}")

    try:
        media = api_v1.media_upload(image_path)
        response = client.create_tweet(
            text=message[:280],
            media_ids=[media.media_id]
        )
        print(f"✅ Tweet posté! ID: {response.data['id']}")
        return True
    except tweepy.TweepyException as e:
        print(f"❌ Erreur Tweepy: {e}")
        return False

def main():
    print("🚀 Lancement du bot ASCII")
    
    image_path = get_next_image("img")

    if image_path:
        print(f"📸 Publication de l'image: {os.path.basename(image_path)}")
        message = "#ASCII #Art"
        success = tweet_image(image_path, message)

        if success:
            print("✅ Publication réussie!")
        else:
            print("❌ Échec de la publication")

        manage_storage("img", max_local_files=3)
    else:
        print("❌ Aucune image à publier.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

print("🏁 Opération terminée")
