import os
import tweepy
import requests
from PIL import Image, UnidentifiedImageError, ImageFile
from io import BytesIO
from dotenv import load_dotenv
import warnings

# Charger les variables d'environnement depuis le fichier .env
load_dotenv('/home/pyth1on/.env')

# Récupérer les clés d'API Twitter depuis les variables d'environnement
CONSUMER_KEY = os.getenv('TEST_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('TEST_CONSUMER_SECRET')
ACCESS_KEY = os.getenv('TEST_ACCESS_KEY')
ACCESS_SECRET = os.getenv('TEST_ACCESS_SECRET')

# Authentification avec l'API Twitter
auth = tweepy.OAuth1UserHandler(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_KEY,
    access_token_secret=ACCESS_SECRET
)
api = tweepy.API(auth)
client = tweepy.Client(
    access_token=ACCESS_KEY,
    access_token_secret=ACCESS_SECRET,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET
)

# Chemin des fichiers
oeuvres_file_path = '/home/pyth1on/art/testoeuvres.txt'
index_file_path = '/home/pyth1on/art/testindex.txt'

def read_oeuvres(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return [line.strip().split('|') for line in lines if line.strip()]

def read_index(file_path):
    if not os.path.exists(file_path):
        return 0
    with open(file_path, 'r', encoding='utf-8') as file:
        return int(file.read().strip())

def write_index(file_path, index):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(str(index))

def resize_image(image, max_size=(1200, 1200)):
    """Redimensionne l'image si elle dépasse max_size."""
    if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
        image.thumbnail(max_size, Image.ANTIALIAS)
    return image

def resize_image_if_needed(content, max_pixels=307913940, max_size=(1200, 1200)):
    """Redimensionne l'image si sa taille dépasse la limite."""
    image_file = BytesIO(content)
    try:
        with Image.open(image_file) as img:
            img_size = img.size[0] * img.size[1]
            if img_size > max_pixels:
                img = resize_image(img, max_size)
                output = BytesIO()
                img.save(output, format=img.format)
                return output.getvalue()
            else:
                return content
    except UnidentifiedImageError:
        return None

# Augmenter la limite de taille d'image autorisée
Image.MAX_IMAGE_PIXELS = 407913940

# Lire la liste des œuvres et l'index actuel
oeuvres = read_oeuvres(oeuvres_file_path)
index = read_index(index_file_path)

# Désactiver les avertissements de décompression de bombes
warnings.filterwarnings("ignore", category=Image.DecompressionBombWarning)

# Vérifier que l'index est valide
if index < len(oeuvres):
    description, image_path = oeuvres[index]

    # Vérifier si l'image est une URL ou un chemin local
    if image_path.startswith("http"):
        headers = {
            "User-Agent": "YourCustomUserAgent/1.0 (your email or contact info)"
        }
        try:
            response = requests.get(image_path, headers=headers)
            response.raise_for_status()

            image_content = resize_image_if_needed(response.content)

            if image_content is None:
                print(f"Erreur : L'image à l'URL {image_path} ne peut pas être traitée car elle dépasse la limite de taille.")
                image_path = None
            else:
                img = Image.open(BytesIO(image_content))
                temp_image_path = 'temp' + os.path.splitext(image_path)[-1]
                img.save(temp_image_path)
                image_path = temp_image_path
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la récupération de l'image depuis l'URL : {e}")
            image_path = None
        except Exception as e:
            print(f"Erreur : {e}")
            image_path = None
    else:
        if not os.path.exists(image_path):
            print(f"Image non trouvée: {image_path}")
            image_path = None

    if image_path:
        try:
            # Téléchargement de l'image sur Twitter
            media = api.media_upload(image_path)

            # Tweet avec l'image et le texte
            client.create_tweet(text=description, media_ids=[media.media_id])

            print(f"Tweet envoyé pour l'œuvre : {description}")

            # Mettre à jour l'index
            index = index + 1
            if index >= len(oeuvres):
                index = 0
            write_index(index_file_path, index)

            # Supprimer le fichier temporaire si utilisé
            if image_path.startswith('temp'):
                os.remove(image_path)
        except UnidentifiedImageError as e:
            print(f"Erreur lors de la lecture de l'image : {e}")
        except tweepy.TweepyException as e:
            if '403' in str(e):
                print("Erreur 403 : Vous n'avez pas les permissions nécessaires pour effectuer cette action.")
                print("Vérifiez les permissions de votre application dans le Twitter Developer Portal.")
            else:
                print(f'Erreur lors de la publication du tweet: {e}')
        except Exception as e:
            print(f'Erreur inattendue: {e}')
else:
    # Réinitialiser l'index si nécessaire
    index = 0
    write_index(index_file_path, index)
    print("L'index actuel dépasse le nombre d'œuvres disponibles. Réinitialisation à zéro.")

print("Opération terminée.")
