# Bot Twitter des fuseaux horaires français
# Envoie l'heure à Paris + 1 territoire aléatoire avec un lien Google Maps
# Adapté pour GitHub Actions
import os
import sys
import time
import random
import logging
from datetime import datetime, timezone, timedelta
import pytz
import tweepy

# ================= CONFIGURATION =================
# Récupérer les variables d'environnement (GitHub Secrets)
CONSUMER_KEY = os.getenv('HORAIRES_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('HORAIRES_CONSUMER_SECRET')
ACCESS_KEY = os.getenv('HORAIRES_ACCESS_KEY')
ACCESS_SECRET = os.getenv('HORAIRES_ACCESS_SECRET')

# Vérification des credentials
if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]):
    print("❌ Missing Twitter API credentials")
    sys.exit(1)

# Fichiers
TWEETED_TERRITORIES_FILE = "tweeted_territories.txt"

# Paramètres
TWEET_COUNT = 1

print("🚀 Lancement du bot Fuseaux")

france_tz = pytz.timezone('Europe/Paris')

def is_winter_time():
    """Détecte l'heure d'hiver (UTC+1)"""
    now = datetime.now(france_tz)
    return now.dst().total_seconds() == 0

def wait_for_winter_adjustment():
    """En hiver, attend 1 heure pour caler l'heure française"""
    if is_winter_time():
        print("❄️ Heure d'hiver - attente de 1 heure")
        time.sleep(3600)
        print("✅ Reprise après attente")
    else:
        print("☀️ Heure d'été - exécution immédiate")

def create_twitter_clients():
    """Initialise les clients Twitter v1.1 et v2"""
    try:
        auth = tweepy.OAuth1UserHandler(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_KEY,
            access_token_secret=ACCESS_SECRET
        )
        api_v1 = tweepy.API(auth)

        client_v2 = tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_KEY,
            access_token_secret=ACCESS_SECRET
        )
        return api_v1, client_v2
    except Exception as e:
        print(f"❌ Erreur API Twitter: {e}")
        return None, None

def get_local_time(timezone_str):
    """Récupère l'heure locale pour un fuseau donné"""
    try:
        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
    except Exception:
        if timezone_str.startswith("Etc/GMT"):
            offset_str = timezone_str.replace("Etc/GMT", "")
            offset_hours = int(offset_str) if offset_str else 0
            tz = timezone(timedelta(hours=-offset_hours))
            now = datetime.now(tz)
        else:
            raise ValueError(f"Fuseau horaire inconnu : {timezone_str}")

    return now.strftime("%Hh%M"), now.strftime("%d/%m/%Y")

# Liste complète des territoires
TERRITORIES = {
    "Paris": "Europe/Paris",
    "#Guadeloupe": "America/Guadeloupe",
    "#Martinique": "America/Martinique",
    "rocher du Diamant (#Martinique)": "America/Martinique",
    "#Guyane": "America/Cayenne",
    "île Saint-Joseph (#Guyane)": "America/Cayenne",
    "île Royale (#Guyane)": "America/Cayenne",
    "île du Diable (#Guyane)": "America/Cayenne",
    "La Réunion": "Indian/Reunion",
    "#Mayotte": "Indian/Mayotte",
    "îles Choazil (#Mayotte)": "Indian/Mayotte",
    "Petite Terre (#Mayotte)": "Indian/Mayotte",
    "îles Hajangoua (#Mayotte)": "Indian/Mayotte",
    "île Kakazou (#Mayotte)": "Indian/Mayotte",
    "île aux Vainqueurs (Saint-Pierre-et-Miquelon)": "America/Miquelon",
    "île aux Marins (Saint-Pierre-et-Miquelon)": "America/Miquelon",
    "île aux Pigeons (Saint-Pierre-et-Miquelon)": "America/Miquelon",
    "Saint-Barthélemy": "America/St_Barthelemy",
    "les Petits Saints (Saint-Barthélemy)": "America/St_Barthelemy",
    "les Gros Islets (Saint-Barthélemy)": "America/St_Barthelemy",
    "île Petit Jean (Saint-Barthélemy)": "America/St_Barthelemy",
    "île Fourchue (Saint-Barthélemy)": "America/St_Barthelemy",
    "Saint-Martin": "America/Marigot",
    "île Tintamarre (Saint-Martin)": "America/Marigot",
    "îlet Pinel (Saint-Martin)": "America/Marigot",
    "Archipel de la Société (Polynésie)": "Pacific/Tahiti",
    "Archipel des Tuamotu (Polynésie)": "Pacific/Tahiti",
    "Archipel des Gambier (Polynésie)": "Pacific/Tahiti",
    "Archipel des #Marquises (Polynésie)": "Pacific/Tahiti",
    "Nouvelle-Calédonie": "Pacific/Noumea",
    "île Ouen (Nouvelle-Calédonie)": "Pacific/Noumea",
    "îlots Saint-Phalle (Nouvelle-Calédonie)": "Pacific/Noumea",
    "Wallis-et-Futuna": "Pacific/Wallis",
    "Terre Adélie": "Antarctica/DumontDUrville",
    "île Claude Bernard (Terre Adélie)": "Antarctica/DumontDUrville",
    "île Jean Rostand (Terre Adélie)": "Antarctica/DumontDUrville",
    "île des Pétrels (Terre Adélie)": "Antarctica/DumontDUrville",
    "îles Curie (Terre Adélie)": "Antarctica/DumontDUrville",
    "îlot des Hydrographes (Terre Adélie)": "Antarctica/DumontDUrville",
    "île Altazin (#Kerguelen)": "Indian/Kerguelen",
    "île Léon Lefèvre (#Kerguelen)": "Indian/Kerguelen",
    "île Ravelo (#Kerguelen)": "Indian/Kerguelen",
    "îlots Simone (#Kerguelen)": "Indian/Kerguelen",
    "île Hould (#Kerguelen)": "Indian/Kerguelen",
    "île de la Possession (#Crozet)": "Etc/GMT-4",
    "île de l'Est (#Crozet)": "Etc/GMT-4",
    "île aux Cochons (#Crozet)": "Etc/GMT-4",
    "îlots des Apôtres (#Crozet)": "Etc/GMT-4",
    "île des Pingouins (#Crozet)": "Etc/GMT-4",
    "île Amsterdam": "Indian/Kerguelen",
    "île Saint Paul": "Indian/Kerguelen",
    "île Juan de Nova": "Indian/Mayotte",
    "atoll Bassas da India": "Indian/Mayotte",
    "île Europa": "Indian/Mayotte",
    "îles Glorieuses": "Indian/Mayotte",
    "île Tromelin": "Indian/Mayotte",
    "île #Clipperton": "Pacific/Pitcairn",
    "île aux Oeufs (#Clipperton)": "Pacific/Pitcairn"
}

PREPOSITIONS = {
    "#Guadeloupe": "en ",
    "#Martinique": "en ",
    "rocher du Diamant (#Martinique)": "sur le ",
    "#Guyane": "en ",
    "île Saint-Joseph (#Guyane)": "sur l'",
    "île Royale (#Guyane)": "sur l'",
    "île du Diable (#Guyane)": "sur l'",
    "La Réunion": "à ",
    "#Mayotte": "à ",
    "îles Choazil (#Mayotte)": "sur les ",
    "Petite Terre (#Mayotte)": "à ",
    "îles Hajangoua (#Mayotte)": "sur les ",
    "île Kakazou (#Mayotte)": "sur l'",
    "île aux Vainqueurs (Saint-Pierre-et-Miquelon)": "sur l'",
    "île aux Marins (Saint-Pierre-et-Miquelon)": "sur l'",
    "île aux Pigeons (Saint-Pierre-et-Miquelon)": "sur l'",
    "Saint-Barthélemy": "à ",
    "les Petits Saints (Saint-Barthélemy)": "sur ",
    "les Gros Islets (Saint-Barthélemy)": "sur ",
    "île Petit Jean (Saint-Barthélemy)": "sur l'",
    "île Fourchue (Saint-Barthélemy)": "sur l'",
    "Saint-Martin": "à ",
    "île Tintamarre (Saint-Martin)": "sur l'",
    "îlet Pinel (Saint-Martin)": "sur l'",
    "Archipel de la Société (Polynésie)": "dans l'",
    "Archipel des Tuamotu (Polynésie)": "dans l'",
    "Archipel des Gambier (Polynésie)": "dans l'",
    "Archipel des #Marquises (Polynésie)": "dans l'",
    "Nouvelle-Calédonie": "en ",
    "île Ouen (Nouvelle-Calédonie)": "sur l'",
    "îlots Saint-Phalle (Nouvelle-Calédonie)": "sur les ",
    "Wallis-et-Futuna": "à ",
    "Terre Adélie": "en ",
    "île Claude Bernard (Terre Adélie)": "sur l'",
    "île Jean Rostand (Terre Adélie)": "sur l'",
    "île des Pétrels (Terre Adélie)": "sur l'",
    "îlot des Hydrographes (Terre Adélie)": "sur l'",
    "îles Curie (Terre Adélie)": "sur les ",
    "île Altazin (#Kerguelen)": "sur l'",
    "île Léon Lefèvre (#Kerguelen)": "sur l'",
    "île Ravelo (#Kerguelen)": "sur l'",
    "îlots Simone (#Kerguelen)": "sur les ",
    "île Hould (#Kerguelen)": "sur l'",
    "île de la Possession (#Crozet)": "sur l'",
    "île de l'Est (#Crozet)": "sur l'",
    "îlots des Apôtres (#Crozet)": "sur les ",
    "île aux Cochons (#Crozet)": "sur l'",
    "île des Pingouins (#Crozet)": "sur l'",
    "île Amsterdam": "sur l'",
    "île Saint Paul": "sur l'",
    "île Juan de Nova": "sur l'",
    "île Europa": "sur l'",
    "îles Glorieuses": "sur les ",
    "île Tromelin": "sur l'",
    "atoll Bassas da India": "sur l'",
    "île #Clipperton": "sur l'",
    "île aux Oeufs (#Clipperton)": "sur l'"
}

# Liens Google Maps pour les territoires (À COMPLETER)
MAPS_LINKS = {
    "#Guadeloupe": "https://maps.app.goo.gl/p8A11PsTiYAAX83YA",
    "#Martinique": "https://maps.app.goo.gl/nhNDcYhJqBKn7MHs7",
    "rocher du Diamant (#Martinique)": "https://maps.app.goo.gl/tSRsRd4zrL7MtTsJ7",
    "#Guyane": "https://maps.app.goo.gl/wjrRfJWVhVE6TwyT6",
    "île Saint-Joseph (#Guyane)": "https://maps.app.goo.gl/cHMcxfMruo7Fugbf7",
    "île Royale (#Guyane)": "https://maps.app.goo.gl/1o2RsAfjTRKxmCbA9",
    "île du Diable (#Guyane)": "https://maps.app.goo.gl/X5Gr6oXqnikSvzNV9",
    "La Réunion": "https://maps.app.goo.gl/HkQzmpbeE6ekyXPj8",
    "#Mayotte": "https://maps.app.goo.gl/AohhyEjm7DSUutVn8",
    "îles Choazil (#Mayotte)": "https://maps.app.goo.gl/sXi5dMpYT2SLwbYs8",
    "Petite Terre (#Mayotte)": "https://maps.app.goo.gl/64K2pdHvPSUsHvE1A",
    "îles Hajangoua (#Mayotte)": "https://maps.app.goo.gl/5f4vdT3FFq2MjZpz5",
    "île Kakazou (#Mayotte)": "https://maps.app.goo.gl/WsowaUGLArykrqiw9",
    "île aux Vainqueurs (Saint-Pierre-et-Miquelon)": "https://maps.app.goo.gl/HVkGdhNZYkLXS4NN9",
    "île aux Marins (Saint-Pierre-et-Miquelon)": "https://maps.app.goo.gl/hMeP2UqP5dpuTnzG7",
    "île aux Pigeons (Saint-Pierre-et-Miquelon)": "https://maps.app.goo.gl/ehUuVcLN3HAsBJGr8",
    "Saint-Barthélemy": "",
    "les Petits Saints (Saint-Barthélemy)": "",
    "les Gros Islets (Saint-Barthélemy)": "",
    "île Petit Jean (Saint-Barthélemy)": "",
    "île Fourchue (Saint-Barthélemy)": "",
    "Saint-Martin": "",
    "île Tintamarre (Saint-Martin)": "",
    "îlet Pinel (Saint-Martin)": "",
    "Archipel de la Société (Polynésie)": "",
    "Archipel des Tuamotu (Polynésie)": "",
    "Archipel des Gambier (Polynésie)": "",
    "Archipel des #Marquises (Polynésie)": "",
    "Nouvelle-Calédonie": "",
    "île Ouen (Nouvelle-Calédonie)": "",
    "îlots Saint-Phalle (Nouvelle-Calédonie)": "",
    "Wallis-et-Futuna": "",
    "Terre Adélie": "",
    "île Claude Bernard (Terre Adélie)": "",
    "île Jean Rostand (Terre Adélie)": "",
    "île des Pétrels (Terre Adélie)": "",
    "îles Curie (Terre Adélie)": "",
    "îlot des Hydrographes (Terre Adélie)": "",
    "île Altazin (#Kerguelen)": "",
    "île Léon Lefèvre (#Kerguelen)": "",
    "île Ravelo (#Kerguelen)": "",
    "îlots Simone (#Kerguelen)": "",
    "île Hould (#Kerguelen)": "",
    "île de la Possession (#Crozet)": "",
    "île de l'Est (#Crozet)": "",
    "île aux Cochons (#Crozet)": "",
    "îlots des Apôtres (#Crozet)": "",
    "île des Pingouins (#Crozet)": "",
    "île Amsterdam": "",
    "île Saint Paul": "",
    "île Juan de Nova": "",
    "atoll Bassas da India": "",
    "île Europa": "",
    "îles Glorieuses": "",
    "île Tromelin": "",
    "île #Clipperton": "https://maps.app.goo.gl/M8LPcY3p4b7EQBQk9",  # Exemple existant
    "île aux Oeufs (#Clipperton)": ""
}

def load_tweeted_territories():
    tweeted = set()
    try:
        if os.path.exists(TWEETED_TERRITORIES_FILE):
            with open(TWEETED_TERRITORIES_FILE, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    territory = line.strip()
                    if territory:
                        tweeted.add(territory)
        return tweeted
    except Exception as e:
        print(f"❌ Erreur chargement historique: {e}")
        return set()

def save_tweeted_territory(territory):
    try:
        with open(TWEETED_TERRITORIES_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{territory}\n")
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")

def reset_tweeted_territories():
    try:
        open(TWEETED_TERRITORIES_FILE, 'w').close()
        print("🔄 Réinitialisation de l'historique des territoires")
    except Exception as e:
        print(f"❌ Erreur réinitialisation: {e}")

def get_random_territory(tweeted_territories):
    all_territories = list(TERRITORIES.keys())
    all_territories.remove("Paris")
    available_territories = [t for t in all_territories if t not in tweeted_territories]

    if not available_territories:
        print("🔄 Tous les territoires ont été tweetés. Réinitialisation...")
        reset_tweeted_territories()
        available_territories = all_territories

    return random.choice(available_territories)

def generate_tweet():
    paris_time, paris_date = get_local_time("Europe/Paris")
    tweeted_territories = load_tweeted_territories()
    city = get_random_territory(tweeted_territories)
    tz = TERRITORIES[city]
    territory_time, territory_date = get_local_time(tz)
    preposition = PREPOSITIONS.get(city, "à ")
    link = MAPS_LINKS.get(city, "")

    message = f"⏰ Il est {paris_time} à Paris 🇫🇷\n\n🌎 {territory_time}"
    if territory_date != paris_date:
        message += f" (le {territory_date})"
    message += f" {preposition}{city} 🇫🇷"

    return message, city, link

def main():
    wait_for_winter_adjustment()
    
    now = datetime.now(france_tz)
    print(f"🕐 Heure française: {now.strftime('%H:%M:%S')}")

    api_v1, client_v2 = create_twitter_clients()
    if not api_v1 or not client_v2:
        sys.exit(1)

    tweet, territory, link = generate_tweet()
    
    # Ajouter le lien Maps s'il existe
    if link and link != "À COMPLETER":
        tweet = f"{tweet}\n\n📍 {link}"
    
    print(f"📝 Tweet: {tweet[:100]}...")

    try:
        # Publication sans image
        response = client_v2.create_tweet(text=tweet[:280])
        print(f"✅ Tweet envoyé")
        
        save_tweeted_territory(territory)
        print(f"💾 Territoire '{territory}' ajouté à l'historique")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

print("🏁 Opération terminée")
