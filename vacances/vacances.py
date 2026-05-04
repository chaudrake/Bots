# Script pour tweeter les décomptes des vacances scolaires - pour GitHub Actions
import os
import sys
import logging
from datetime import datetime
import pandas as pd
import tweepy
from collections import defaultdict

# Récupérer les variables d'environnement (GitHub Secrets)
ACCESS_KEY = os.getenv('VACANCES_ACCESS_KEY')
ACCESS_SECRET = os.getenv('VACANCES_ACCESS_SECRET')
CONSUMER_KEY = os.getenv('VACANCES_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('VACANCES_CONSUMER_SECRET')

# Vérification des credentials
if not all([ACCESS_KEY, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET]):
    print("❌ Missing Twitter API credentials")
    sys.exit(1)

# Configuration du logging (version simplifiée pour GitHub)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_and_print(message):
    """Log et affiche un message"""
    print(message)
    logging.info(message)

def read_vacances_data():
    """Lit les données de vacances depuis le fichier Excel"""
    try:
        df = pd.read_excel('vacances.xlsx', sheet_name='Feuil1')
        # Convertir les dates en datetime
        for col in df.columns[1:]:
            df[col] = pd.to_datetime(df[col])
        return df
    except Exception as e:
        log_and_print(f"❌ Erreur lecture fichier vacances: {e}")
        return None

def create_twitter_client():
    """Crée et retourne le client Twitter"""
    try:
        return tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_KEY,
            access_token_secret=ACCESS_SECRET
        )
    except Exception as e:
        log_and_print(f"❌ Erreur création client Twitter: {e}")
        return None

def get_vacation_info(row, today):
    """Retourne les informations de vacances pour une zone"""
    zone = row['zone']
    info = {
        'zone': zone,
        'is_vacation': False,
        'is_tomorrow': False,
        'days_left': None,
        'end_date': None,
        'start_date': None
    }

    # Vérifier d'abord si c'est le jour J-1 (veille des vacances)
    for i in range(1, len(row), 2):
        start_date = row[i]
        if (start_date - today).days == 1:  # Demain = premier jour des vacances
            info.update({
                'is_tomorrow': True,
                'start_date': start_date
            })
            return info

    # Vérifier si en vacances actuellement
    for i in range(1, len(row), 2):
        start_date = row[i]
        end_date = row[i+1] if i+1 < len(row) else None

        if end_date and start_date <= today < end_date:
            days_left = (end_date - today).days
            info.update({
                'is_vacation': True,
                'days_left': days_left,
                'end_date': end_date,
                'start_date': start_date
            })
            return info

    # Prochaines vacances (hors cas J-1 déjà traité)
    for i in range(1, len(row), 2):
        start_date = row[i]
        if start_date > today:
            days_left = (start_date - today).days
            if days_left > 1:  # Éviter les doublons avec le cas J-1
                info.update({
                    'days_left': days_left,
                    'start_date': start_date
                })
                return info

    return info

def group_zones_by_status(vacances_df, today):
    """Regroupe les zones par statut de vacances"""
    tomorrow_zones = []
    vacation_zones = defaultdict(list)  # clé: jours restants
    upcoming_zones = defaultdict(list)  # clé: jours avant vacances
    
    for _, row in vacances_df.iterrows():
        info = get_vacation_info(row, today)
        
        if info['is_tomorrow']:
            tomorrow_zones.append(info['zone'])
        elif info['is_vacation']:
            key = (info['days_left'], info['end_date'])
            vacation_zones[key].append(info['zone'])
        elif info['days_left'] is not None:
            key = (info['days_left'], info['start_date'])
            upcoming_zones[key].append(info['zone'])
    
    return tomorrow_zones, vacation_zones, upcoming_zones

def format_zone_list(zones):
    """Formate une liste de zones en texte lisible"""
    if len(zones) == 1:
        return f"La zone {zones[0]}"
    elif len(zones) == 2:
        return f"Les zones {zones[0]} et {zones[1]}"
    else:
        return f"Les zones {', '.join(zones[:-1])} et {zones[-1]}"

def generate_tweet_text(vacances_df):
    """Génère le tweet avec regroupement des zones"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_zones, vacation_zones, upcoming_zones = group_zones_by_status(vacances_df, today)
    
    lines = []
    
    # Traitement des zones qui commencent demain
    if tomorrow_zones:
        zones_text = format_zone_list(tomorrow_zones)
        verb = "sera" if len(tomorrow_zones) == 1 else "seront"
        lines.append(f"{zones_text} {verb} en vacances dès demain !")
    
    # Traitement des zones actuellement en vacances
    for (days_left, _), zones in sorted(vacation_zones.items()):
        zones_text = format_zone_list(zones)
        plural = 's' if days_left > 1 else ''
        verb = "est" if len(zones) == 1 else "sont"
        lines.append(f"{zones_text} {verb} en vacances (encore {days_left} jour{plural})")
    
    # Traitement des zones avec vacances à venir
    grouped_by_days = defaultdict(list)
    for (days_left, start_date), zones in upcoming_zones.items():
        grouped_by_days[days_left].extend(zones)
    
    for days_left in sorted(grouped_by_days.keys()):
        zones = grouped_by_days[days_left]
        zones_text = format_zone_list(zones)
        verb = "sera" if len(zones) == 1 else "seront"
        lines.append(f"{zones_text} {verb} en vacances dans {days_left} jours.")
    
    if not lines:
        lines.append("Aucune zone ne sera en vacances prochainement.")
    
    # S'assurer que le tweet ne dépasse pas 280 caractères
    tweet = "\n".join(lines) + "\n#VacancesScolaires #Vacances"
    if len(tweet) > 280:
        # Si trop long, on tronque intelligemment
        tweet = tweet[:277] + "..."
    
    return tweet

def post_tweet(api):
    """Poste le tweet des vacances"""
    try:
        vacances_df = read_vacances_data()
        if vacances_df is None or vacances_df.empty:
            log_and_print("❌ Aucune donnée de vacances valide trouvée")
            return False

        tweet_text = generate_tweet_text(vacances_df)
        log_and_print(f"📝 Tweet préparé: {tweet_text[:100]}...")

        response = api.create_tweet(text=tweet_text)
        log_and_print(f"✅ Tweet envoyé avec succès")
        return True

    except Exception as e:
        log_and_print(f"❌ Erreur envoi tweet: {e}")
        return False

def main():
    """Fonction principale"""
    log_and_print("🚀 Démarrage du script vacances")

    api = create_twitter_client()
    if api is None:
        log_and_print("❌ Échec de la connexion à Twitter")
        sys.exit(1)

    if post_tweet(api):
        log_and_print("✅ Tweet envoyé avec succès")
    else:
        log_and_print("❌ Échec de l'envoi du tweet")
        sys.exit(1)

    log_and_print("🏁 Script terminé")

if __name__ == "__main__":
    main()
