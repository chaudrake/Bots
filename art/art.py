# Tweete une oeuvre par jour
# Si une image bloque, ça tweete la suivante
import os
import tweepy
import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import warnings

# Récupérer les clés d'API Twitter depuis les variables d'environnement GitHub
CONSUMER_KEY = os.getenv('2LART_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('2LART_CONSUMER_SECRET')
ACCESS_KEY = os.getenv('2LART_ACCESS_KEY')
ACCESS_SECRET = os.getenv('2LART_ACCESS_SECRET')

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

# Chemins des fichiers (dans le dossier courant, pas de chemins absolus)
oeuvres_file_path = 'oeuvres.txt'
index_file_path = 'index.txt'

def read_oeuvres(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return [line.strip().split('|') for line in lines if line.strip()]

def read_index(file_path):
    if not os.path.exists(file_path):
        return 0
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            return int(file.read().strip())
        except ValueError:
            return 0

def write_index(file_path, index):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(str(index))

def resize_image(image, max_size=(1200, 1200)):
    """Redimensionne l'image si elle dépasse max_size."""
    if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
        # Remplacer Image.ANTIALIAS (déprécié) par Image.LANCZOS
        image.thumbnail(max_size, Image.LANCZOS)
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
                # Enregistrer avec le format original ou JPEG en fallback
                img_format = img.format if img.format else 'JPEG'
                img.save(output, format=img_format)
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
warnings.filterwarnings("ignore", category=UserWarning)

print(f"📋 {len(oeuvres)} œuvres chargées")
print(f"📍 Index actuel: {index}")

# Vérifier que l'index est valide
if index < len(oeuvres):
    description, image_path = oeuvres[index]
    temp_image_path = None
    success = False

    # Créer le dossier temp au besoin
    os.makedirs('temp', exist_ok=True)

    try:
        # Vérifier si l'image est une URL ou un chemin local
        if image_path.startswith("http"):
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; TwitterBot/1.0)"
            }
            try:
                print(f"📥 Téléchargement: {image_path}")
                response = requests.get(image_path, headers=headers, timeout=30)
                response.raise_for_status()

                image_content = resize_image_if_needed(response.content)

                if image_content is None:
                    print(f"❌ Erreur : L'image à l'URL {image_path} ne peut pas être traitée")
                else:
                    img = Image.open(BytesIO(image_content))
                    # Déterminer l'extension
                    ext = '.jpg'
                    if img.format and img.format.lower() in ['png', 'gif', 'webp']:
                        ext = f'.{img.format.lower()}'
                    temp_image_path = os.path.join('temp', f'temp_{index}{ext}')
                    img.save(temp_image_path)
                    image_path = temp_image_path
                    success = True
                    print(f"✅ Image téléchargée et redimensionnée")
            except requests.exceptions.RequestException as e:
                print(f"❌ Erreur récupération URL: {e}")
            except Exception as e:
                print(f"❌ Erreur traitement image: {e}")
        else:
            # Chemin local relatif
            if os.path.exists(image_path):
                success = True
                print(f"✅ Image locale trouvée: {image_path}")
            else:
                print(f"❌ Image non trouvée: {image_path}")

        if success:
            # Téléchargement de l'image sur Twitter
            print(f"📤 Upload de l'image vers Twitter...")
            media = api.media_upload(image_path)
            
            # Tweet avec l'image et le texte (tronqué à 280 caractères)
            tweet_text = description[:280]
            client.create_tweet(text=tweet_text, media_ids=[media.media_id])
            print(f"✅ Tweet envoyé: {description[:100]}...")

        # Mettre à jour l'index (même en cas d'erreur, on passe à l'œuvre suivante)
        index = index + 1
        if index >= len(oeuvres):
            index = 0
            print("🔄 Toutes les œuvres ont été tweetées, retour à la première")
        write_index(index_file_path, index)

        # Supprimer le fichier temporaire si utilisé
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)

    except UnidentifiedImageError as e:
        print(f"❌ Erreur lecture image: {e}")
        index = index + 1
        if index >= len(oeuvres):
            index = 0
        write_index(index_file_path, index)
    except tweepy.TweepyException as e:
        if '403' in str(e):
            print("❌ Erreur 403: Vérifiez les permissions de l'application Twitter")
        else:
            print(f"❌ Erreur Twitter: {e}")
        index = index + 1
        if index >= len(oeuvres):
            index = 0
        write_index(index_file_path, index)
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        index = index + 1
        if index >= len(oeuvres):
            index = 0
        write_index(index_file_path, index)
else:
    # Réinitialiser l'index si nécessaire
    index = 0
    write_index(index_file_path, index)
    print("🔄 Index réinitialisé à zéro")

print("🏁 Opération terminée.")
