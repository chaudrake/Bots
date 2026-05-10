import tweepy
import random
import logging
import os
import sys
import json
from time import sleep
from pathlib import Path

# Définition dynamique du dossier de travail (le dossier où se trouve ce script)
WORKING_DIR = Path(__file__).parent.absolute()

# Chemins des fichiers basés sur WORKING_DIR
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
        logging.error(f"Erreur lors de la limitation du fichier de log : {e}")

def should_execute_script():
    """
    Détermine aléatoirement si le script doit s'exécuter.
    Actuellement réglé sur 10% de chances de succès (random < 0.10).
    """
    if random.random() < 0.10: 
        log_and_print("Le script CMB s'exécute maintenant")
    else:
        log_and_print("Le script CMB ne s'exécute pas cette fois (tirage aléatoire)")
        sys.exit()

def read_qualities(qualities_file):
    [span_0](start_span)"""Lit les qualités depuis le fichier texte[span_0](end_span)."""
    try:
        with open(qualities_file, 'r', encoding='utf-8') as f:
            # Nettoie les lignes et ignore les tags comme ou les lignes vides
            qualities = []
            for line in f.readlines():
                clean_line = line.strip()
                if clean_line and not clean_line.startswith('['):
                    qualities.append(clean_line)
            return qualities
    except Exception as e:
        log_and_print(f"Erreur lors de la lecture du fichier des qualités : {e}")
        return []

def load_index(index_file):
    """Charge l'index des qualités déjà tweetées."""
    try:
        if Path(index_file).exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"used": []}
    except Exception as e:
        log_and_print(f"Erreur lors du chargement de l'index : {e}")
        return {"used": []}

def save_index(index_file, index_data):
    """Sauvegarde l'index des qualités tweetées."""
    try:
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f)
    except Exception as e:
        log_and_print(f"Erreur lors de la sauvegarde de l'index : {e}")

def get_next_quality(qualities, index_data):
    """Récupère la prochaine qualité à tweeter."""
    # Normalisation pour la comparaison (minuscules)
    used_lower = [u.lower() for u in index_data["used"]]
    remaining = [q for q in qualities if q.lower() not in used_lower]

    # Si toutes les qualités ont été utilisées, on réinitialise
    if not remaining:
        log_and_print("Toutes les qualités ont été tweetées. Réinitialisation.")
        index_data["used"] = []
        remaining = qualities

    selected = random.choice(remaining)
    index_data["used"].append(selected)

    return selected, index_data

def capitalize_first_letter(text):
    """Met une majuscule à la première lettre du texte."""
    if not text:
        return text
    return text[0].upper() + text[1:]

# --- EXÉCUTION ---

# 1. Nettoyage logs
limit_log_file(LOG_FILE)

# 2. Check aléatoire (si tu veux que le bot ne tweet pas à chaque fois que le cron tourne)
should_execute_script()

# 3. Récupération des variables d'environnement (Secrets GitHub)
ACCESS_KEY = os.getenv('CMB_ACCESS_KEY')
ACCESS_SECRET = os.getenv('CMB_ACCESS_SECRET')
CONSUMER_KEY = os.getenv('CMB_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CMB_CONSUMER_SECRET')

# 4. Initialisation Tweepy
api = tweepy.Client(
    access_token=ACCESS_KEY,
    access_token_secret=ACCESS_SECRET,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET
)

# 5. Lecture et sélection
qualities = read_qualities(QUALITIES_FILE)

if not qualities:
    log_and_print("Aucune qualité trouvée dans le fichier")
    sys.exit()

index_data = load_index(INDEX_FILE)
selected_quality, updated_index = get_next_quality(qualities, index_data)
formatted_quality = capitalize_first_letter(selected_quality)

# 6. Publication
tweet_text = f"{formatted_quality} comme ma bite. #cmb"

try:
    response = api.create_tweet(text=tweet_text)
    log_and_print(f"Tweet publié : {tweet_text}")
    # Sauvegarde uniquement si le tweet est réussi
    save_index(INDEX_FILE, updated_index)
    log_and_print(f"Progression : {len(updated_index['used'])}/{len(qualities)}")
except Exception as e:
    log_and_print(f"Erreur lors de la publication : {e}")
               
