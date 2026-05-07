import tweepy
from random import randint
from time import sleep
import os
import random
import sys

# Récupérer les variables d'environnement (GitHub Secrets)
ACCESS_KEY = os.getenv('MOTSRARES_ACCESS_KEY')
ACCESS_SECRET = os.getenv('MOTSRARES_ACCESS_SECRET')
CONSUMER_KEY = os.getenv('MOTSRARES_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('MOTSRARES_CONSUMER_SECRET')

# Vérification des credentials
if not all([ACCESS_KEY, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET]):
    print("❌ Missing Twitter API credentials")
    sys.exit(1)

# Créer un client Tweepy
api = tweepy.Client(
    access_token=ACCESS_KEY,
    access_token_secret=ACCESS_SECRET,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET
)

print('🚀 Lancement du bot Les Mots Rares')

# Génère un nombre aléatoire entre 0 et 1 pour tweeter un jour sur 2 environ.
if random.random() < 0.5:
    print('📅 Le script ne s\'exécute pas aujourd\'hui (1 jour sur 2)')
    sys.exit(0)
else:
    print('📅 Le script s\'exécute aujourd\'hui')

# Pause aléatoire de 10 sec à 2.5 heures (pour éviter les patterns trop réguliers)
wait_time = randint(10, 10000)
print(f"⏳ Pause pendant {wait_time} secondes...")
sleep(wait_time)

def get_post_content(block_number):
    """Récupère le contenu du tweet à partir du fichier motsrares.txt."""
    with open("motsrares.txt", "r", encoding="utf-8") as file:
        content = file.read()
        blocks = content.split('\n\n')
        return blocks[int(block_number)].strip()

def post_tweets(api):
    """Publie le tweet en utilisant l'API Twitter."""
    try:
        # Lire l'index du fichier (ou initialiser à 0 si non trouvé)
        if os.path.exists('indexmotsrares.txt'):
            with open('indexmotsrares.txt', 'r', encoding="utf-8") as index_file:
                block_number = int(index_file.read().strip())
        else:
            block_number = 0

        print(f"📌 Index actuel: {block_number}")

        # Récupérer le contenu du tweet
        content = get_post_content(block_number)
        print(f"📝 Contenu du tweet: {content[:100]}...")

        # Compter le nombre total de blocs
        with open("motsrares.txt", "r", encoding="utf-8") as file:
            total_blocks = len(file.read().split('\n\n'))

        # S'assurer que l'index est valide
        if block_number >= total_blocks:
            block_number = 0
            print("🔄 Réinitialisation de l'index (fin de la liste)")

        # Récupérer à nouveau le contenu avec l'index corrigé
        content = get_post_content(block_number)

        # Publier le tweet (tronqué à 280 caractères)
        tweet_text = content[:280]
        tweet = api.create_tweet(text=tweet_text)
        print(f"✅ Tweet publié: {tweet}")

        # Incrémenter le numéro de bloc
        block_number += 1
        if block_number >= total_blocks:
            block_number = 0
            print("🔄 Retour au début de la liste")

        # Sauvegarder l'index
        with open('indexmotsrares.txt', 'w', encoding="utf-8") as index_file:
            index_file.write(str(block_number))

        print(f"📌 Nouvel index sauvegardé: {block_number}")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de la publication du tweet: {e}")
        return False

if __name__ == "__main__":
    try:
        if post_tweets(api):
            print('✅ Tweet posté avec succès')
        else:
            print('❌ Erreur lors de la publication du tweet')
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

print("🏁 Opération terminée")
