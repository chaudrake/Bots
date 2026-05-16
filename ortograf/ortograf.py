import tweepy
from random import randint
from time import sleep
import os
import random
import sys

print('🚀 Lancement du bot Ortograf')

# ==========================================
# 1. LOGIQUE D'EXÉCUTION ET TIMING 🎲
# ==========================================

# Détermine aléatoirement si le script doit s'exécuter aujourd'hui (70% de chance de NE PAS s'exécuter)
if random.random() < 0.7:
    print("📅 Le script Ortograf ne s'exécute pas aujourd'hui (70% de chance)")
    sys.exit(0)
else:
    print("📅 Le script Ortograf s'exécute aujourd'hui (30% de chance)")

# Pause aléatoire entre 10 secondes et 6 heures (21000 sec)
# Placé ici pour ne pas consommer de temps de calcul GitHub Actions si on ne tweete pas.
wait_time = randint(10, 21000)
print(f"⏳ Pause pendant {wait_time} secondes...")
sleep(wait_time)

# ==========================================
# 2. CONFIGURATION ET CONNEXION X (TWITTER) 🔑
# ==========================================

# Récupérer les variables d'environnement (GitHub Secrets)
ACCESS_KEY = os.getenv('ORTOGRAF_ACCESS_KEY')
ACCESS_SECRET = os.getenv('ORTOGRAF_ACCESS_SECRET')
CONSUMER_KEY = os.getenv('ORTOGRAF_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('ORTOGRAF_CONSUMER_SECRET')

# Vérification des credentials
if not all([ACCESS_KEY, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET]):
    print("❌ Missing Twitter API credentials")
    sys.exit(1)

# Créer un client Tweepy (Ne consomme pas de crédit d'API à l'initialisation)
api = tweepy.Client(
    access_token=ACCESS_KEY,
    access_token_secret=ACCESS_SECRET,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET
)

# ==========================================
# 3. FONCTIONS DE GESTION DES TWEETS 📝
# ==========================================

def get_post_content(block_number):
    """Récupère le contenu du tweet à partir du fichier liste.txt."""
    try:
        with open('liste.txt', 'r', encoding='utf-8') as file:
            content = file.read()
            blocks = content.split('\n\n')
            return blocks[int(block_number)].strip()
    except Exception as e:
        print(f"❌ Erreur lors de la récupération du contenu: {e}")
        return None

def post_tweets(api):
    """Publie le tweet en utilisant l'API Twitter."""
    try:
        # Lire l'index du fichier (ou initialiser à 0 si non trouvé)
        if os.path.exists('index.txt'):
            with open('index.txt', 'r', encoding='utf-8') as index_file:
                block_number = int(index_file.read().strip())
        else:
            block_number = 0

        print(f"📌 Index actuel: {block_number}")

        # Compter le nombre total de blocs
        with open('liste.txt', 'r', encoding='utf-8') as file:
            total_blocks = len(file.read().split('\n\n'))

        # S'assurer que l'index est valide
        if block_number >= total_blocks:
            block_number = 0
            print("🔄 Réinitialisation de l'index (fin de la liste)")

        # Récupérer le contenu du tweet
        content = get_post_content(block_number)
        if content is None:
            return False

        print(f"📝 Contenu du tweet: {content[:100]}...")

        # Publier le tweet (tronqué à 280 caractères) - C'est CETTE ligne qui consomme 1 crédit
        tweet_text = content[:280]
        tweet = api.create_tweet(text=tweet_text)
        print(f"✅ Tweet publié: {tweet}")

        # Incrémenter le numéro de bloc
        block_number += 1
        if block_number >= total_blocks:
            block_number = 0
            print("🔄 Retour au début de la liste")

        # Sauvegarder l'index
        with open('index.txt', 'w', encoding='utf-8') as index_file:
            index_file.write(str(block_number))

        print(f"📌 Nouvel index sauvegardé: {block_number}")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de la publication du tweet: {e}")
        return False

# ==========================================
# 4. POINT D'ENTRÉE PRINCIPAL 🏁
# ==========================================

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
