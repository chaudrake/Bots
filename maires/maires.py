# Le script envoie 1 tweet par exécution (GitHub Actions gère la fréquence)
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

def format_departement(nom_departement):
    """Formate le nom du département avec la bonne préposition"""
    if pd.isna(nom_departement):
        return ""

    nom = str(nom_departement).strip().title()
    nom = ' '.join(nom.split())
    nom = nom.replace(' - ', '-').replace(' / ', '/')

    special_cases = {
        "Ain": "de l'Ain", "Aisne": "de l'Aisne", "Allier": "de l'Allier",
        "Alpes-De-Haute-Provence": "des Alpes-de-Haute-Provence",
        "Alpes-Maritimes": "des Alpes-Maritimes", "Ardèche": "de l'Ardèche",
        "Ardennes": "des Ardennes", "Ariège": "de l'Ariège", "Aube": "de l'Aube",
        "Aude": "de l'Aude", "Aveyron": "de l'Aveyron",
        "Bouches-Du-Rhône": "des Bouches-du-Rhône", "Calvados": "du Calvados",
        "Cantal": "du Cantal", "Charente": "de la Charente",
        "Charente-Maritime": "de la Charente-Maritime", "Cher": "du Cher",
        "Corrèze": "de la Corrèze", "Corse-Du-Sud": "de la Corse-du-Sud",
        "Haute-Corse": "de la Haute-Corse", "Côte-D'Or": "de la Côte-d'Or",
        "Côtes-D'Armor": "des Côtes-d'Armor", "Creuse": "de la Creuse",
        "Dordogne": "de la Dordogne", "Doubs": "du Doubs", "Drôme": "de la Drôme",
        "Eure": "de l'Eure", "Eure-Et-Loir": "d'Eure-et-Loir",
        "Finistère": "du Finistère", "Gard": "du Gard",
        "Haute-Garonne": "de la Haute-Garonne", "Gers": "du Gers",
        "Gironde": "de la Gironde", "Hérault": "de l'Hérault",
        "Ille-Et-Vilaine": "d'Ille-et-Vilaine", "Indre": "de l'Indre",
        "Indre-Et-Loire": "d'Indre-et-Loire", "Isère": "de l'Isère",
        "Jura": "du Jura", "Landes": "des Landes", "Loir-Et-Cher": "du Loir-et-Cher",
        "Loire": "de la Loire", "Haute-Loire": "de Haute-Loire",
        "Loire-Atlantique": "de la Loire-Atlantique", "Loiret": "du Loiret",
        "Lot": "du Lot", "Lot-Et-Garonne": "du Lot-et-Garonne",
        "Lozère": "de la Lozère", "Maine-Et-Loire": "du Maine-et-Loire",
        "Manche": "de la Manche", "Marne": "de la Marne",
        "Haute-Marne": "de la Haute-Marne", "Mayenne": "de la Mayenne",
        "Meurthe-Et-Moselle": "de la Meurthe-et-Moselle", "Meuse": "de la Meuse",
        "Morbihan": "du Morbihan", "Moselle": "de la Moselle",
        "Nièvre": "de la Nièvre", "Nord": "du Nord", "Oise": "de l'Oise",
        "Orne": "de l'Orne", "Pas-De-Calais": "du Pas-de-Calais",
        "Puy-De-Dôme": "du Puy-de-Dôme", "Pyrénées-Atlantiques": "des Pyrénées-Atlantiques",
        "Hautes-Pyrénées": "des Hautes-Pyrénées",
        "Pyrénées-Orientales": "des Pyrénées-Orientales", "Bas-Rhin": "du Bas-Rhin",
        "Haut-Rhin": "du Haut-Rhin", "Rhône": "du Rhône",
        "Haute-Saône": "de Haute-Saône", "Saône-Et-Loire": "de Saône-et-Loire",
        "Sarthe": "de la Sarthe", "Savoie": "de la Savoie",
        "Haute-Savoie": "de Haute-Savoie", "Paris": "de Paris",
        "Seine-Maritime": "de Seine-Maritime", "Seine-Et-Marne": "de Seine-et-Marne",
        "Yvelines": "des Yvelines", "Deux-Sèvres": "des Deux-Sèvres",
        "Somme": "de la Somme", "Tarn": "du Tarn",
        "Tarn-Et-Garonne": "du Tarn-et-Garonne", "Var": "du Var",
        "Vaucluse": "du Vaucluse", "Vendée": "de la Vendée",
        "Vienne": "de la Vienne", "Haute-Vienne": "de la Haute-Vienne",
        "Vosges": "des Vosges", "Yonne": "de l'Yonne",
        "Territoire De Belfort": "du Territoire de Belfort", "Essonne": "de l'Essonne",
        "Hauts-De-Seine": "des Hauts-de-Seine", "Seine-Saint-Denis": "de Seine-Saint-Denis",
        "Val-De-Marne": "du Val-de-Marne", "Val-D'Oise": "du Val-d'Oise",
        "Guadeloupe": "de Guadeloupe", "Martinique": "de Martinique",
        "Guyane": "de Guyane", "La Réunion": "de la Réunion", "Mayotte": "de Mayotte"
    }

    for key, value in special_cases.items():
        if key.lower() == nom.lower():
            return value

    return f"de {nom}"

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
    commune = row['Libellé de la commune']
    departement = format_departement(row['Libellé du département'])
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
        return f"🏛 La #maire de {commune} {departement} est {prenom} {nom}{age_text} #MairesdeFrance 🇫🇷"
    else:
        return f"🏛 Le #maire de {commune} {departement} est {prenom} {nom}{age_text} #MairesdeFrance 🇫🇷"

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
    except Exception as e:
        log_and_print(f"Erreur chargement historique: {e}")
    return tweeted

def save_tweeted_maire(code, name):
    try:
        with open(TWEETED_MAIRES_FILE, 'a') as f:
            f.write(f"{time.strftime('%Y-%m-%d')}|{code}|{name}\n")
    except Exception as e:
        log_and_print(f"Erreur sauvegarde: {e}")

def reset_tweeted_maires():
    try:
        open(TWEETED_MAIRES_FILE, 'w').close()
        log_and_print("Historique réinitialisé")
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

    for _ in range(len(df_active)):
        row = df_active.sample(n=1).iloc[0]
        code = row['Code_normalise']
        prenom = row["Prénom de l'élu"]
        nom = row["Nom de l'élu"]
        name = f"{prenom} {nom}"

        norm_tweeted = {str(k).zfill(5): v for k, v in tweeted_maires.items()}

        if code not in norm_tweeted:
            return row

        old_date, old_name = norm_tweeted[code]
        if old_name != name:
            log_and_print(f"Changement: {code} ({old_name} → {name})")
            return row

    log_and_print("Tous les maires tweetés → réinitialisation")
    reset_tweeted_maires()
    return df_active.sample(n=1).iloc[0]

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
        
        prenom = row["Prénom de l'élu"]
        nom = row["Nom de l'élu"]
        save_tweeted_maire(str(row['Code de la commune']).zfill(5), f"{prenom} {nom}")
        
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
