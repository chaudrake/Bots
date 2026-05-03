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

# Charger les variables d'environnement depuis le fichier .env
load_dotenv('/home/pyth1on/.env')

# Chemins et constantes
WORKING_DIR = '/home/pyth1on/ortograf'
LOG_FILE = os.path.join(WORKING_DIR, 'log.log')
LIST_FILE = os.path.join(WORKING_DIR, 'liste.txt')
INDEX_FILE = os.path.join(WORKING_DIR, 'index.txt')

# Mise à jour du répertoire de travail pour que cron job marche
os.chdir(WORKING_DIR)

# Configuration du logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_and_print(message):
    print(message, flush=True)  # flush=True force l'affichage immédiat
    logging.info(message)

def limit_log_file(file_path, max_lines=100):
    """Limite le fichier de log aux 100 dernières lignes."""
    try:
        with open(file_path, 'r+') as file:
            lines = file.readlines()
            if len(lines) > max_lines:
                file.seek(0)
                file.writelines(lines[-max_lines:])
                file.truncate()
    except Exception as e:
        logging.error(f"Erreur lors de la limitation du fichier de log : {e}")

# Limiter le fichier log au début du script
limit_log_file(LOG_FILE)

def should_execute_script():
    """Détermine aléatoirement si le script doit s'exécuter aujourd'hui."""
    if random.random() < 0.7:
        log_and_print("Le script Ortograf ne s'exécute pas aujourd'hui")
        sys.exit()
    else:
        log_and_print("Le script Ortograf s'exécute aujourd'hui")

def random_sleep():
    """Pause aléatoire entre 10 secondes et 7 heures.(25000 sec)"""
    wait_time = randint(10, 25000)
    log_and_print(f"Pause pendant {wait_time} secondes")
    sys.stdout.flush()  # <--- FLUSH EXPLICITE POUR ÊTRE SÛR
    sleep(wait_time)

def get_post_content(block_number):
    """Récupère le contenu du tweet à partir du fichier liste.txt."""
    try:
        with open(LIST_FILE, 'r') as file:
            content = file.read()
            blocks = content.split('\n\n')
            return blocks[int(block_number)].strip()
    except Exception as e:
        logging.error(f"Erreur lors de la récupération du contenu du tweet : {e}")
        return None

def post_tweets(api):
    """Publie les tweets en utilisant l'API Twitter."""
    try:
        # Lire l'index du fichier (ou initialiser à 0 si non trouvé)
        if os.path.exists(INDEX_FILE):
            with open(INDEX_FILE, 'r') as index_file:
                block_number = int(index_file.read().strip())
        else:
            block_number = 0

        # Récupérer le contenu du tweet
        content = get_post_content(block_number)
        if content is None:
            return False

        log_and_print(f"Contenu du tweet: {content}")

        # Publier le tweet
        tweet = api.create_tweet(text=content)
        log_and_print(f"Tweet publié: {tweet}")

        if tweet:
            # Incrémenter le numéro de bloc, et réinitialiser à zéro si on a atteint la fin de la liste
            block_number += 1
            with open(LIST_FILE, 'r') as file:
                total_blocks = len(file.read().split('\n\n'))
            if block_number >= total_blocks:
                block_number = 0

            with open(INDEX_FILE, 'w') as index_file:
                index_file.write(str(block_number))

            log_and_print(f'Tweet No {block_number} successfully posted')
            return True
    except Exception as e:
        logging.error(f'Erreur lors de la publication du tweet: {e}')
        return False

def main():
    # Limiter la taille du fichier log
    limit_log_file(LOG_FILE)

    # Déterminer si le script doit s'exécuter aujourd'hui
    should_execute_script()

    # Pause aléatoire avant l'exécution
    random_sleep()

    # Définir vos informations d'identification Twitter API via des variables d'environnement
    ACCESS_KEY = os.getenv('ORTOGRAF_ACCESS_KEY')
    ACCESS_SECRET = os.getenv('ORTOGRAF_ACCESS_SECRET')
    CONSUMER_KEY = os.getenv('ORTOGRAF_CONSUMER_KEY')
    CONSUMER_SECRET = os.getenv('ORTOGRAF_CONSUMER_SECRET')

    # Créer un client Tweepy
    api = tweepy.Client(
        access_token=ACCESS_KEY,
        access_token_secret=ACCESS_SECRET,
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET
    )

    # Publier le tweet
    if post_tweets(api):
        logging.info('Tweet posté. Attente relance dans 24h par task')
    else:
        logging.error('Erreur lors de la publication du tweet.')

if __name__ == "__main__":
    main()
