# Le script envoie 1 tweet par exécution
import os
import sys
import logging
import time
import re
import pandas as pd
from dotenv import load_dotenv
import tweepy
from datetime import datetime

# Configuration - le script se trouve déjà dans le bon dossier
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(WORKING_DIR, 'log.log')
EXCEL_FILE = os.path.join(WORKING_DIR, 'elus-deputes-depCorrige.csv')
TWEETED_DEPUTES_FILE = os.path.join(WORKING_DIR, 'tweeted_deputes.txt')

# API Twitter
ACCESS_KEY = os.getenv('DEPUTE_ACCESS_KEY')
ACCESS_SECRET = os.getenv('DEPUTE_ACCESS_SECRET')
CONSUMER_KEY = os.getenv('DEPUTE_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('DEPUTE_CONSUMER_SECRET')

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
        "Français Établis Hors De France": "des Français établis hors de France",
        "Ain": "de l'Ain",
        "Aisne": "de l'Aisne",
        "Allier": "de l'Allier",
        "Alpes-De-Haute-Provence": "des Alpes-de-Haute-Provence",
        "Alpes-Maritimes": "des Alpes-Maritimes",
        "Ardèche": "de l'Ardèche",
        "Ardennes": "des Ardennes",
        "Ariège": "de l'Ariège",
        "Aube": "de l'Aube",
        "Aude": "de l'Aude",
        "Aveyron": "de l'Aveyron",
        "Bouches-Du-Rhône": "des Bouches-du-Rhône",
        "Calvados": "du Calvados",
        "Cantal": "du Cantal",
        "Charente": "de la Charente",
        "Charente-Maritime": "de la Charente-Maritime",
        "Cher": "du Cher",
        "Corrèze": "de la Corrèze",
        "Corse-Du-Sud": "de la Corse-du-Sud",
        "Haute-Corse": "de la Haute-Corse",
        "Côte-D'Or": "de la Côte-d'Or",
        "Côtes-D'Armor": "des Côtes-d'Armor",
        "Creuse": "de la Creuse",
        "Dordogne": "de la Dordogne",
        "Doubs": "du Doubs",
        "Drôme": "de la Drôme",
        "Eure": "de l'Eure",
        "Eure-Et-Loir": "d'Eure-et-Loir",
        "Finistère": "du Finistère",
        "Gard": "du Gard",
        "Haute-Garonne": "de la Haute-Garonne",
        "Gers": "du Gers",
        "Gironde": "de la Gironde",
        "Hérault": "de l'Hérault",
        "Ille-Et-Vilaine": "d'Ille-et-Vilaine",
        "Indre": "de l'Indre",
        "Indre-Et-Loire": "d'Indre-et-Loire",
        "Isère": "de l'Isère",
        "Jura": "du Jura",
        "Landes": "des Landes",
        "Loir-Et-Cher": "du Loir-et-Cher",
        "Loire": "de la Loire",
        "Haute-Loire": "de Haute-Loire",
        "Loire-Atlantique": "de la Loire-Atlantique",
        "Loiret": "du Loiret",
        "Lot": "du Lot",
        "Lot-Et-Garonne": "du Lot-et-Garonne",
        "Lozère": "de la Lozère",
        "Maine-Et-Loire": "du Maine-et-Loire",
        "Manche": "de la Manche",
        "Marne": "de la Marne",
        "Haute-Marne": "de la Haute-Marne",
        "Mayenne": "de la Mayenne",
        "Meurthe-Et-Moselle": "de la Meurthe-et-Moselle",
        "Meuse": "de la Meuse",
        "Morbihan": "du Morbihan",
        "Moselle": "de la Moselle",
        "Nièvre": "de la Nièvre",
        "Nord": "du Nord",
        "Oise": "de l'Oise",
        "Orne": "de l'Orne",
        "Pas-De-Calais": "du Pas-de-Calais",
        "Puy-De-Dôme": "du Puy-de-Dôme",
        "Pyrénées-Atlantiques": "des Pyrénées-Atlantiques",
        "Hautes-Pyrénées": "des Hautes-Pyrénées",
        "Pyrénées-Orientales": "des Pyrénées-Orientales",
        "Bas-Rhin": "du Bas-Rhin",
        "Haut-Rhin": "du Haut-Rhin",
        "Rhône": "du Rhône",
        "Haute-Saône": "de Haute-Saône",
        "Saône-Et-Loire": "de Saône-et-Loire",
        "Sarthe": "de la Sarthe",
        "Savoie": "de la Savoie",
        "Haute-Savoie": "de Haute-Savoie",
        "Paris": "de Paris",
        "Seine-Maritime": "de Seine-Maritime",
        "Seine-Et-Marne": "de Seine-et-Marne",
        "Yvelines": "des Yvelines",
        "Deux-Sèvres": "des Deux-Sèvres",
        "Somme": "de la Somme",
        "Tarn": "du Tarn",
        "Tarn-Et-Garonne": "du Tarn-et-Garonne",
        "Var": "du Var",
        "Vaucluse": "du Vaucluse",
        "Vendée": "de la Vendée",
        "Vienne": "de la Vienne",
        "Haute-Vienne": "de la Haute-Vienne",
        "Vosges": "des Vosges",
        "Yonne": "de l'Yonne",
        "Territoire De Belfort": "du Territoire de Belfort",
        "Essonne": "de l'Essonne",
        "Hauts-De-Seine": "des Hauts-de-Seine",
        "Seine-Saint-Denis": "de Seine-Saint-Denis",
        "Val-De-Marne": "du Val-de-Marne",
        "Val-D'Oise": "du Val-d'Oise",
        "Guadeloupe": "de Guadeloupe",
        "Martinique": "de Martinique",
        "Guyane": "de Guyane",
        "La Réunion": "de la Réunion",
        "Mayotte": "de Mayotte",
        "Saint-Pierre-Et-Miquelon": "de Saint-Pierre-et-Miquelon",
        "Wallis Et Futuna": "de Wallis et Futuna",
        "Polynésie Française": "de Polynésie française",
        "Nouvelle-Calédonie": "de Nouvelle-Calédonie",
        "Saint-Martin / Saint-Barthélémy": "de Saint-Martin / Saint-Barthélémy"
    }

    for key, value in special_cases.items():
        if key.lower() == nom.lower():
            return value

    return f"de {nom}"

def read_excel_data():
    try:
        df = pd.read_csv(EXCEL_FILE, sep=';')
        required_columns = ["Code de la circonscription législative",
                          "Libellé de la circonscription législative",
                          "Libellé du département", "Prenom", "Nom",
                          "Code sexe", "Date de naissance", "Date de début du mandat"]
        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
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
    """Génère le texte du tweet selon le genre"""
    circo_text = row['Libellé de la circonscription législative']

    if pd.isna(circo_text):
        circo_text = ""

    match = re.search(r'(\d+)(?:ère|ème|e)?\s*circonscription', str(circo_text), re.IGNORECASE)
    if match:
        numero = match.group(1)
        suffixe = 'ère' if numero == '1' else 'e'
        circo = f"{numero}{suffixe} circonscription"
    else:
        circo = ""

    département = format_departement(row['Libellé du département'])
    prénom = row["Prenom"]
    nom = row["Nom"]
    sexe = row["Code sexe"]

    age_text = ""
    if not pd.isna(row['Date de naissance']):
        try:
            birth_date = pd.to_datetime(row['Date de naissance'], dayfirst=True)
            today = pd.to_datetime('today')
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            age_text = f" ({age} ans)"
        except:
            pass

    if circo:
        if sexe == "F":
            return f"🏛 La #députée de la {circo} {département} est {prénom} {nom}{age_text} #Députés #AssembléeNationale 🇫🇷"
        else:
            return f"🏛 Le #député de la {circo} {département} est {prénom} {nom}{age_text} #Députés #AssembléeNationale 🇫🇷"
    else:
        if sexe == "F":
            return f"🏛 La #députée {département} est {prénom} {nom}{age_text} #Députés #AssembléeNationale 🇫🇷"
        else:
            return f"🏛 Le #député {département} est {prénom} {nom}{age_text} #Députés #AssembléeNationale 🇫🇷"

def load_tweeted_deputes():
    """Charge l'historique des tweets : {code_circo: (date, nom_complet)}"""
    tweeted = {}
    try:
        if os.path.exists(TWEETED_DEPUTES_FILE):
            with open(TWEETED_DEPUTES_FILE, 'r') as f:
                for line in f.readlines():
                    parts = line.strip().split('|')
                    if len(parts) >= 3:
                        date, circo_code, name = parts[0], parts[1], '|'.join(parts[2:])
                        tweeted[circo_code] = (date, name)
        return tweeted
    except Exception as e:
        log_and_print(f"Erreur chargement historique: {e}")
        return {}

def save_tweeted_depute(circo_code, name):
    try:
        with open(TWEETED_DEPUTES_FILE, 'a') as f:
            f.write(f"{time.strftime('%Y-%m-%d')}|{circo_code}|{name}\n")
    except Exception as e:
        log_and_print(f"Erreur sauvegarde historique: {e}")

def reset_tweeted_deputes():
    try:
        open(TWEETED_DEPUTES_FILE, 'w').close()
        log_and_print("Réinitialisation de l'historique des tweets.")
    except Exception as e:
        log_and_print(f"Erreur réinitialisation historique: {e}")

def get_depute_to_tweet(df, tweeted_deputes):
    """Trouve un député à tweeter selon les règles"""
    today = pd.to_datetime('today').normalize()
    df['Date_debut'] = pd.to_datetime(df['Date de début du mandat'], dayfirst=True)
    df_active = df[df['Date_debut'] <= today]

    df_active = df_active.sort_values('Date_debut', ascending=False)
    df_active = df_active.drop_duplicates(
        subset=['Code de la circonscription législative'],
        keep='first')

    df_active['Code_normalise'] = df_active['Code de la circonscription législative'].astype(str).str.zfill(4)

    for _ in range(len(df_active)):
        random_row = df_active.sample(n=1).iloc[0]
        circo_code = random_row['Code_normalise']
        current_name = f"{random_row['Prenom']} {random_row['Nom']}"

        norm_tweeted = {str(k).zfill(4): v for k, v in tweeted_deputes.items()}

        if circo_code not in norm_tweeted:
            return random_row

        old_date, old_name = norm_tweeted[circo_code]
        if old_name != current_name:
            log_and_print(f"Changement de député: {circo_code} ({old_name} → {current_name})")
            return random_row

    log_and_print("Tous les députés actuels tweetés. Réinitialisation...")
    reset_tweeted_deputes()
    return df_active.sample(n=1).iloc[0]

def main():
    log_and_print("Démarrage du script Députés")
    
    # Nettoyage du log si trop gros
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()
            if len(lines) > 100:
                with open(LOG_FILE, 'w') as f:
                    f.writelines(lines[-100:])
    except:
        pass
    
    api = create_twitter_client()
    if not api:
        log_and_print("Échec connexion Twitter")
        sys.exit(1)
    
    df = read_excel_data()
    if df is None or df.empty:
        log_and_print("Aucune donnée valide")
        sys.exit(1)
    
    tweeted_deputes = load_tweeted_deputes()
    random_row = get_depute_to_tweet(df, tweeted_deputes)
    
    tweet_text = generate_tweet_text(random_row)
    circo_code = random_row['Code de la circonscription législative']
    name = f"{random_row['Prenom']} {random_row['Nom']}"
    
    log_and_print(f"Tweet: {tweet_text}")
    
    response = api.create_tweet(text=tweet_text)
    save_tweeted_depute(circo_code, name)
    log_and_print(f"Succès! Tweet envoyé: {response}")
    
    log_and_print("Script terminé")

if __name__ == "__main__":
    main()
