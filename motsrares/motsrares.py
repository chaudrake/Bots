import schedule
import time
import tweepy
from random import randint
from time import sleep
import os
import random
import sys
import logging
from dotenv import load_dotenv

# Chemin absolu du fichier .env à la racine du serveur
dotenv_path = os.path.join('/home/lesmotsrares', '.env')
# Charger les variables d'environnement depuis le fichier .env
load_dotenv(dotenv_path)

# Mise à jour du répertoire de travail pour que cron job marche
os.chdir('/home/lesmotsrares')

# Configuration du logging
LOG_FILE = '/home/lesmotsrares/taskmotsrares.log'
logging.basicConfig(filename=LOG_FILE,
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
def log_and_print(message):
    print(message, flush=True)  # flush=True force l'affichage immédiat
    logging.info(message)

def limit_log_file(file_path, max_lines=100):
    """Limite le fichier de log aux 100 dernières max_lines."""
    try:
        with open(file_path, 'r+') as file:
            lines = file.readlines()
            if len(lines) > max_lines:
                file.seek(0)
                file.writelines(lines[-max_lines:])
                file.truncate()
    except Exception as e:
        logging.error(f"Erreur lors de la limitation du fichier de log : {e}")

limit_log_file(LOG_FILE)

log_and_print('Lancement Les Mots rares')

# Génère un nombre aléatoire entre 0 et 1 pour tweeter un jour sur 2 environ.
if random.random() < 0.5:
    log_and_print('Le script Les mots rares ne s execute pas aujourd hui')
    sys.exit()
else:
    log_and_print('Le script Les mots rares s execute aujourd hui')

# Pause aléatoire de 10 sec à 7 heures
wait_time = randint(10, 25000)
log_and_print(f"Pause pendant {wait_time} secondes")
sys.stdout.flush()  # <--- FLUSH EXPLICITE POUR ÊTRE SÛR
sleep(wait_time)

def get_post_content(block_number):
    """Récupère le contenu du tweet à partir du fichier motsrares.txt."""
    with open("motsrares.txt", "r") as file:
        content = file.read()
        blocks = content.split('\n\n')
        return blocks[int(block_number)].strip()

def post_tweets(api):
    """Publie les tweets en utilisant l'API Twitter."""
    try:
        # Lire l'index du fichier (ou initialiser à 0 si non trouvé)
        if os.path.exists('indexmotsrares.txt'):
            with open('indexmotsrares.txt', 'r') as index_file:
                block_number = int(index_file.read().strip())
        else:
            block_number = 0

        # Récupérer le contenu du tweet
        content = get_post_content(block_number)
        log_and_print(f"Contenu du tweet: {content}")

        # Publier le tweet
        tweet = api.create_tweet(text=content)
        log_and_print(f"Tweet publié: {tweet}")
        if tweet:
            # Incrémenter le numéro de bloc, et réinitialiser à zéro si on a atteint la fin de la liste
            block_number += 1
            with open("motsrares.txt", "r") as file:
                total_blocks = len(file.read().split('\n\n'))
            if block_number >= total_blocks:
                block_number = 0
            with open('indexmotsrares.txt', 'w') as index_file:
                index_file.write(str(block_number))
            log_and_print(f'Tweet No {block_number} successfully posted')
            return True
    except Exception as e:
        logging.error(f'Erreur lors de la publication du tweet: {e}')
        return False

if __name__ == "__main__":
    # Définir vos informations d'identification Twitter API via des variables d'environnement
    ACCESS_KEY = os.getenv('LESMOTSRARES_ACCESS_KEY')
    ACCESS_SECRET = os.getenv('LESMOTSRARES_ACCESS_SECRET')
    CONSUMER_KEY = os.getenv('LESMOTSRARES_CONSUMER_KEY')
    CONSUMER_SECRET = os.getenv('LESMOTSRARES_CONSUMER_SECRET')

    # Créer un client Tweepy
    api = tweepy.Client(
        access_token=ACCESS_KEY,
        access_token_secret=ACCESS_SECRET,
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET
    )

    if post_tweets(api):
        logging.info('Tweet posté. Attente relance dans 24h par task')
    else:
        logging.error('Erreur lors de la publication du tweet.')

    # Boucle infinie pour exécuter le planificateur

    #while True:
    #    schedule.run_pending()
     #   time.sleep(1)  # Pause pour éviter une utilisation élevée du CPU
