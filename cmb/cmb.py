import tweepy
import random
import logging
import os
import sys
import json
from time import sleep
from pathlib import Path

# Définition dynamique du dossier de travail
WORKING_DIR = Path(__file__).parent.absolute()

# Chemins des fichiers
LOG_FILE = os.path.join(WORKING_DIR, 'log_bot_qualites.log')
QUALITIES_FILE = os.path.join(WORKING_DIR, 'liste.txt')
INDEX_FILE = os.path.join(WORKING_DIR, 'last_index.json')

# Configuration du logging
logging.basicConfig(
    filename=LOG_FILE, 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_and_print(message):
    print(message)
    logging.info(message)

def limit_log_file(file_path, max_lines=100):
    """Limite le fichier de log aux 100 dernières lignes."""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r+') as file:
                lines = file.readlines()
                if len(lines) > max_lines:
                    file.seek(0)
                    file.writelines(lines[-max_lines:])
                    file.truncate()
    except Exception as e:
        logging.error(f"Erreur lors de la limitation du fichier : {e}")

def should_execute_script():
    """10% de chance de s'exécuter."""
    if random.random() < 0.99: 
        log_and_print("Le script CMB s'exécute maintenant")
    else:
        log_and_print("Le script CMB ne s'exécute pas cette fois (tirage aléatoire)")
        sys.exit()

def read_qualities(qualities_file):
    """Lit les qualités depuis le fichier texte."""
    try:
        with open(qualities_file, 'r', encoding='utf-8') as f:
            qualities = []
            for line in f.readlines():
                clean_line = line.strip()
                # On ignore les lignes vides et les sources
                if clean_line and not clean_line.startswith('['):
                    qualities.append(clean_line)
            return qualities
    except Exception as e:
        log_and_print(f"Erreur lecture fichier : {e}")
        return []

def load_index(index_file):
    """Charge l'index des qualités déjà tweetées."""
    try:
        if Path(index_file).exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"used": []}
    except Exception as e:
        log_and_print(f"Erreur chargement index : {e}")
        return {"used": []}

def save_index(index_file, index_data):
    """Sauvegarde l'index des qualités tweetées."""
    try:
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f)
    except Exception as e:
        log_and_print(f"Erreur sauvegarde index : {e}")

def get_next_quality(qualities, index_data):
    """Récupère la prochaine qualité à tweeter."""
    used_lower = [u.lower() for u in index_data["used"]]
    remaining = [q for q in qualities if q.lower() not in used_lower]

    if not remaining:
        log_and_print("Toutes les qualités ont été utilisées. Réinitialisation.")
        index_data["used"] = []
        remaining = qualities

    selected = random.choice(remaining)
    index_data["used"].append(selected)

    return selected, index_data

def capitalize_first_letter(text):
    if not text:
        return text
    return text[0].upper() + text[1:]

# --- EXÉCUTION ---

limit_log_file(LOG_FILE)
should_execute_script()

ACCESS_KEY = os.getenv('CMB_ACCESS_KEY')
ACCESS_SECRET = os.getenv('CMB_ACCESS_SECRET')
CONSUMER_KEY = os.getenv('CMB_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CMB_CONSUMER_SECRET')

api = tweepy.Client(
    access_token=ACCESS_KEY,
    access_token_secret=ACCESS_SECRET,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET
)

qualities = read_qualities(QUALITIES_FILE)

if not qualities:
    log_and_print("Aucune qualité trouvée")
    sys.exit()

index_data = load_index(INDEX_FILE)
selected_quality, updated_index = get_next_quality(qualities, index_data)
formatted_quality = capitalize_first_letter(selected_quality)

tweet_text = f"{formatted_quality} comme ma bite. #cmb"

try:
    response = api.create_tweet(text=tweet_text)
    log_and_print(f"Tweet publié : {tweet_text}")
    save_index(INDEX_FILE, updated_index)
except Exception as e:
    log_and_print(f"Erreur lors de la publication : {e}")
    
