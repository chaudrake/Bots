# Le script envoie 1 tweet par exécution avec persistance via Git
import os
import sys
import logging
import time
import pandas as pd
from dotenv import load_dotenv
import tweepy

# Charger les variables d'environnement
load_dotenv()

# Configuration - Chemins relatifs au dossier courant
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(WORKING_DIR, 'log.log')
EXCEL_FILE = os.path.join(WORKING_DIR, 'elus-maires-mai-corrige.csv')
TWEETED_MAIRES_FILE = os.path.join(WORKING_DIR, 'tweeted_maires.txt')

# API Twitter
ACCESS_KEY = os.getenv('QUIESTLEMAIRE_ACCESS_KEY')
ACCESS_SECRET = os.getenv('QUIESTLEMAIRE_ACCESS_SECRET')
CONSUMER_KEY = os.getenv('QUIESTLEMAIRE_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('QUIESTLEMAIRE_CONSUMER_SECRET')

# Logging
logging.basicConfig(filename=LOG_FILE,
                   level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

def log_and_print(message):
    print(message)
    logging.info(message)

def read_excel_data():
    try:
        df = pd.read_csv(EXCEL_FILE, sep=';')
        required_columns = ["Libellé de la commune", "Libellé du département",
                          "Prénom de l'élu", "Nom de l'élu", "Code sexe", "Code de la commune"]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Colonnes manquantes: {missing}")
        return df
    except Exception as e:
        log_and_print(f"Erreur lecture CSV: {e}")
        return None

def create_twitter_client():
    try:
        return tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_KEY,
            access_token_secret=ACCESS_SECRET
        )
    except Exception as e:
        log_and_print(f"Erreur création client Twitter: {e}")
        return None

def generate_tweet_text(row):
    """Génère le texte du tweet selon le genre - Version originale"""
    commune = row['Libellé de la commune']
    departement = row['Libellé du département']
    prenom = row["Prénom de l'élu"]
    nom = row["Nom de l'élu"]
    sexe = row["Code sexe"]

    age_text = ""
    if 'Date de naissance' in row and not pd.isna(row['Date de naissance']):
        try:
            birth_date = pd.to_datetime(row['Date de naissance'], dayfirst=True)
            today = pd.to_datetime('today')
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            age_text = f" ({age} ans)"
        except:
            pass

    if sexe == "F":
        return f"🏛 La #maire de {commune} ({departement}) est {prenom} {nom}{age_text} #MairesdeFrance 🇫🇷"
    else:
        return f"🏛 Le #maire de {commune} ({departement}) est {prenom} {nom}{age_text} #MairesdeFrance 🇫🇷"

def load_tweeted_maires():
    tweeted = {}
    try:
        if os.path.exists(TWEETED_MAIRES_FILE):
            with open(TWEETED_MAIRES_FILE, 'r') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) == 3:
                        date, code, name = parts
                        tweeted[code] = (date, name)
            log_and_print(f"Historique chargé: {len(tweeted)} maires déjà tweetés")
        else:
            log_and_print("Fichier historique inexistant, départ à zéro")
    except Exception as e:
        log_and_print(f"Erreur chargement historique: {e}")
    return tweeted

def save_tweeted_maire(code, name):
    try:
        with open(TWEETED_MAIRES_FILE, 'a') as f:
            f.write(f"{time.strftime('%Y-%m-%d')}|{code}|{name}\n")
        log_and_print(f"Sauvegarde effectuée: {code} - {name}")
    except Exception as e:
        log_and_print(f"Erreur sauvegarde: {e}")

def reset_tweeted_maires():
    try:
        open(TWEETED_MAIRES_FILE, 'w').close()
        log_and_print("⚠️ RÉINITIALISATION DE L'HISTORIQUE")
    except Exception as e:
        log_and_print(f"Erreur réinitialisation: {e}")

def get_maire_to_tweet(df, tweeted_maires):
    today = pd.to_datetime('today').normalize()

    if 'Date de début du mandat' in df.columns:
        df['Date_debut'] = pd.to_datetime(df['Date de début du mandat'], dayfirst=True)
        df_active = df[df['Date_debut'] <= today]
    else:
        df_active = df.copy()

    if 'Date_debut' in df_active.columns:
        df_active = df_active.sort_values('Date_debut', ascending=False)
    df_active = df_active.drop_duplicates(subset=['Code de la commune'], keep='first')
    df_active['Code_normalise'] = df_active['Code de la commune'].astype(str).str.zfill(5)

    log_and_print(f"Nombre de maires actifs uniques: {len(df_active)}")
    log_and_print(f"Nombre de maires déjà tweetés: {len(tweeted_maires)}")

    for _ in range(len(df_active)):
        row = df_active.sample(n=1).iloc[0]
        code = row['Code_normalise']
        prenom_elu = row["Prénom de l'élu"]
        nom_elu = row["Nom de l'élu"]
        name = f"{prenom_elu} {nom_elu}"

        norm_tweeted = {str(k).zfill(5): v for k, v in tweeted_maires.items()}

        if code not in norm_tweeted:
            log_and_print(f"Sélectionné: {code} - {name} (nouveau maire)")
            return row

        old_date, old_name = norm_tweeted[code]
        if old_name != name:
            log_and_print(f"Changement détecté: {code} ({old_name} → {name})")
            return row

    log_and_print("Tous les maires tweetés → réinitialisation")
    reset_tweeted_maires()
    row = df_active.sample(n=1).iloc[0]
    log_and_print(f"Nouveau cycle: sélection de {row['Code_normalise']}")
    return row

def post_random_tweet(api):
    try:
        df = read_excel_data()
        if df is None or df.empty:
            return False

        tweeted = load_tweeted_maires()
        row = get_maire_to_tweet(df, tweeted)
        tweet_text = generate_tweet_text(row)

        log_and_print(f"Tweet: {tweet_text}")
        response = api.create_tweet(text=tweet_text)
        
        prenom_elu = row["Prénom de l'élu"]
        nom_elu = row["Nom de l'élu"]
        code_commune = str(row['Code de la commune']).zfill(5)
        save_tweeted_maire(code_commune, f"{prenom_elu} {nom_elu}")
        
        log_and_print(f"Succès: {response}")
        return True
    except Exception as e:
        log_and_print(f"Erreur: {e}")
        return False

def clean_log_file():
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
        if len(lines) > 100:
            with open(LOG_FILE, 'w') as f:
                f.writelines(lines[-100:])
    except:
        pass

def main():
    log_and_print("=== Démarrage Maires ===")
    log_and_print(f"WORKING_DIR: {WORKING_DIR}")
    log_and_print(f"Fichier historique: {TWEETED_MAIRES_FILE}")
    
    clean_log_file()
    api = create_twitter_client()
    if api:
        post_random_tweet(api)
    else:
        log_and_print("Échec connexion Twitter")
    log_and_print("=== Fin ===")
    sys.exit(0)

if __name__ == "__main__":
    main()
