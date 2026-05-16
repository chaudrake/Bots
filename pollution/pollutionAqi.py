# PollutionAqi.py - Tweet l'indice AQI uniquement
# Adapté pour GitHub Actions
import json
import requests
import tweepy
import os
import sys
import time
import pytz
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Récupérer les variables d'environnement (GitHub Secrets)
CONSUMER_KEY = os.getenv('POLLUTION_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('POLLUTION_CONSUMER_SECRET')
ACCESS_KEY = os.getenv('POLLUTION_ACCESS_KEY')
ACCESS_SECRET = os.getenv('POLLUTION_ACCESS_SECRET')
AIRVISUAL_API_KEY = os.getenv('POLLUTION_AIRVISUAL_API_KEY')

# Vérification des credentials Twitter
if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]):
    print("❌ Missing Twitter API credentials")
    sys.exit(1)

print("✅ Démarrage du script Pollution (Mode AQI unique)")

france_tz = pytz.timezone('Europe/Paris')

def is_summer_time():
    """Détecte si l'heure d'été est active à Paris"""
    now = datetime.now(france_tz)
    return now.dst().total_seconds() != 0

def wait_for_winter_adjustment():
    """Si on est en hiver, attend 1 heure pour caler l'heure française sur la cible"""
    if not is_summer_time():
        print("❄️ Heure d'hiver détectée (UTC+1) - attente de 1 heure")
        time.sleep(3600)
        print("✅ Reprise après attente")
    else:
        print("☀️ Heure d'été détectée (UTC+2) - exécution immédiate")

def load_cities():
    """Charge la liste des villes depuis le fichier JSON"""
    with open('cities.json', 'r', encoding='utf-8') as f:
        cities_data = json.load(f)
        return [{"name": name, "lat": data["lat"], "lon": data["lon"]} for name, data in cities_data.items()]

def fetch_aqi_airvisual(city):
    if not AIRVISUAL_API_KEY:
        return None
    try:
        url = f"http://api.airvisual.com/v2/nearest_city?lat={city['lat']}&lon={city['lon']}&key={AIRVISUAL_API_KEY}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get('status') == 'success':
            return {
                "city": city["name"],
                "aqi": data['data']['current']['pollution']['aqius'],
                "source": "AirVisual"
            }
    except Exception:
        pass
    return None

def fetch_aqi_safe(city):
    try:
        url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={city['lat']}&longitude={city['lon']}&current=us_aqi"
        response = requests.get(url, timeout=5)
        data = response.json()
        if 'current' in data and 'us_aqi' in data['current']:
            return {
                "city": city["name"],
                "aqi": data['current']['us_aqi'],
                "source": "Open-Meteo"
            }
    except Exception:
        pass
    return None

def get_city_aqi(city):
    """Tente AirVisual, sinon bascule sur Open-Meteo"""
    return fetch_aqi_airvisual(city) or fetch_aqi_safe(city)

def generate_aqi_tweet(polluted_cities):
    current_time = datetime.now(france_tz).strftime("%Hh%M")
    tweet_header = f"🌍 #Pollution à {current_time}. Indice Air Quality Index (AQI).\n\n🔴 Villes les plus polluées : 🔴\n"
    tweet_footer = f"\nSource : {polluted_cities[0]['source']}"
    
    # Essaie d'afficher 5 villes, sinon 3, sinon 1 pour ne pas dépasser la limite de Twitter
    for num_cities in [5, 3, 1]:
        city_lines = [f"• {city['city']} : AQI {city['aqi']}" for city in polluted_cities[:num_cities]]
        tweet = "\n".join([tweet_header] + city_lines + [tweet_footer])
        if len(tweet) <= 270:
            return tweet
    return None

def post_tweet(tweet_text):
    try:
        client = tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_KEY,
            access_token_secret=ACCESS_SECRET
        )
        client.create_tweet(text=tweet_text[:280])
        print(f"✅ Tweet AQI publié avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur publication : {e}")
        return False

def execute_pollution_check():
    print("🔍 Lancement du relevé de l'indice AQI...")
    cities = load_cities()
    print(f"📋 {len(cities)} villes chargées")

    # On ne récupère plus que l'AQI, parallélisé pour aller vite
    with ThreadPoolExecutor(max_workers=10) as executor:
        aqi_data = [data for data in executor.map(get_city_aqi, cities) if data]

    if len(aqi_data) < 3:
        print("⚠️ Pas assez de données AQI récupérées pour faire un classement.")
        return

    # Tri des villes de la plus polluée à la moins polluée
    top_aqi = sorted(aqi_data, key=lambda x: x['aqi'], reverse=True)[:5]
    
    # Génération et publication du tweet unique
    aqi_tweet = generate_aqi_tweet(top_aqi)
    if aqi_tweet:
        post_tweet(aqi_tweet)
    else:
        print("❌ Impossible de générer un tweet valide.")

def main():
    wait_for_winter_adjustment()
    now_fr = datetime.now(france_tz)
    print(f"🕐 Heure française d'exécution : {now_fr.strftime('%H:%M:%S')}")
    execute_pollution_check()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)
