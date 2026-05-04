# Pollution.py - Tweet AQI, PM2.5 et Ozone
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

# Vérification des credentials
if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]):
    print("❌ Missing Twitter API credentials")
    sys.exit(1)

print("✅ Démarrage du script Pollution")

france_tz = pytz.timezone('Europe/Paris')

def is_summer_time():
    """Détecte l'heure d'été (UTC+2)"""
    now = datetime.now(france_tz)
    return now.utcoffset() == pytz.FixedOffset(120)

def wait_for_winter_adjustment():
    """Si on est en hiver, attend 1 heure pour caler l'heure française"""
    if not is_summer_time():
        print("❄️ Heure d'hiver détectée - attente de 1 heure")
        time.sleep(3600)
        print("✅ Reprise après attente")
    else:
        print("☀️ Heure d'été - exécution immédiate")

def load_cities():
    """Charge la liste des villes depuis le fichier JSON"""
    with open('cities.json', 'r', encoding='utf-8') as f:
        cities_data = json.load(f)
        return [{"name": name, "lat": data["lat"], "lon": data["lon"]} for name, data in cities_data.items()]

def fetch_pm25(city):
    try:
        url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={city['lat']}&longitude={city['lon']}&current=pm2_5"
        response = requests.get(url, timeout=3)
        data = response.json()
        return {"city": city["name"], "pm25": round(data['current']['pm2_5'], 1)}
    except Exception:
        return None

def fetch_ozone(city):
    try:
        url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={city['lat']}&longitude={city['lon']}&current=ozone"
        response = requests.get(url, timeout=3)
        data = response.json()
        return {"city": city["name"], "ozone": round(data['current']['ozone'], 1)}
    except Exception:
        return None

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
                "pollutant": data['data']['current']['pollution']['mainus'],
                "source": "AirVisual"
            }
    except Exception:
        pass
    return None

def fetch_aqi_safe(city):
    try:
        url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={city['lat']}&longitude={city['lon']}&current=us_aqi,pm2_5"
        response = requests.get(url, timeout=5)
        data = response.json()
        if 'current' in data and 'us_aqi' in data['current']:
            aqi = data['current']['us_aqi']
            return {
                "city": city["name"],
                "aqi": aqi,
                "pollutant": None,
                "source": "Open-Meteo"
            }
    except Exception:
        pass
    return None

def get_city_aqi(city):
    return fetch_aqi_airvisual(city) or fetch_aqi_safe(city)

def generate_pm25_tweet(polluted):
    current_time = datetime.now(france_tz).strftime("%Hh%M")
    base = [f"🌍 #Pollution aux #ParticulesFines (PM2.5) à {current_time}.", "\n🔴 Villes les plus polluées : 🔴\n"]
    footer = "\nSource : Open-Meteo"
    for n in [5, 3, 1]:
        cities_lines = [f"• {c['city']} : {c['pm25']} µg/m³" for c in polluted[:n]]
        tweet = "\n".join(base + cities_lines + [footer])
        if len(tweet) <= 270:
            return tweet, n
    return None, 0

def generate_ozone_tweet(polluted):
    current_time = datetime.now(france_tz).strftime("%Hh%M")
    base = [f"🌍 #Pollution à l'#Ozone (O₃) à {current_time}.", "\n🔴 Villes les plus polluées : 🔴\n"]
    footer = "\nSource : Open-Meteo"
    for n in [5, 3, 1]:
        cities_lines = [f"• {c['city']} : {c['ozone']} µg/m³" for c in polluted[:n]]
        tweet = "\n".join(base + cities_lines + [footer])
        if len(tweet) <= 270:
            return tweet, n
    return None, 0

def generate_aqi_tweet(polluted_cities):
    current_time = datetime.now(france_tz).strftime("%Hh%M")
    tweet_header = f"🌍 #Pollution à {current_time}. Indice Air Quality Index (AQI).\n\n🔴 Villes les plus polluées : 🔴\n"
    tweet_footer = f"\nSource : {polluted_cities[0]['source']}"
    for num_cities in [5, 3, 1]:
        city_lines = [f"• {city['city']} : AQI {city['aqi']}" for city in polluted_cities[:num_cities]]
        tweet = "\n".join([tweet_header] + city_lines + [tweet_footer])
        if len(tweet) <= 270:
            return tweet, num_cities
    return None, 0

def post_tweet(tweet_text):
    try:
        client = tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_KEY,
            access_token_secret=ACCESS_SECRET
        )
        response = client.create_tweet(text=tweet_text[:280])
        print(f"✅ Tweet publié : {response.data['id']}")
        return True
    except Exception as e:
        print(f"❌ Erreur publication : {e}")
        return False

def execute_pollution_check():
    print("🔍 Lancement du relevé pollution...")
    cities = load_cities()
    print(f"📋 {len(cities)} villes chargées")

    with ThreadPoolExecutor(max_workers=10) as executor:
        print("\n🔄 Récupération des données PM2.5...")
        pm25_data = [data for data in executor.map(fetch_pm25, cities) if data]
        print(f"   ✅ {len(pm25_data)} données PM2.5 récupérées")
        
        print("\n🔄 Récupération des données Ozone...")
        ozone_data = [data for data in executor.map(fetch_ozone, cities) if data]
        print(f"   ✅ {len(ozone_data)} données Ozone récupérées")
        
        print("\n🔄 Récupération des données AQI...")
        aqi_data = [data for data in executor.map(get_city_aqi, cities) if data]
        print(f"   ✅ {len(aqi_data)} données AQI récupérées")

    tweets_postes = 0
    
    # PM2.5
    if len(pm25_data) >= 3:
        top_pm25 = sorted(pm25_data, key=lambda x: x['pm25'], reverse=True)[:5]
        pm25_tweet, _ = generate_pm25_tweet(top_pm25)
        if pm25_tweet and post_tweet(pm25_tweet):
            tweets_postes += 1
            print(f"✅ Tweet PM2.5 posté")
    else:
        print(f"⚠️ Pas assez de données PM2.5 ({len(pm25_data)}/3)")

    # Ozone
    if len(ozone_data) >= 3:
        top_ozone = sorted(ozone_data, key=lambda x: x['ozone'], reverse=True)[:5]
        ozone_tweet, _ = generate_ozone_tweet(top_ozone)
        if ozone_tweet and post_tweet(ozone_tweet):
            tweets_postes += 1
            print(f"✅ Tweet Ozone posté")
    else:
        print(f"⚠️ Pas assez de données Ozone ({len(ozone_data)}/3)")

    # AQI
    if len(aqi_data) >= 3:
        top_aqi = sorted(aqi_data, key=lambda x: x['aqi'], reverse=True)[:5]
        aqi_tweet, _ = generate_aqi_tweet(top_aqi)
        if aqi_tweet and post_tweet(aqi_tweet):
            tweets_postes += 1
            print(f"✅ Tweet AQI posté")
    else:
        print(f"⚠️ Pas assez de données AQI ({len(aqi_data)}/3)")

    print(f"📊 Résumé: {tweets_postes}/3 tweets postés")

def main():
    # Ajustement pour l'heure d'hiver
    wait_for_winter_adjustment()
    
    # Vérifier l'heure française actuelle
    now_fr = datetime.now(france_tz)
    print(f"🕐 Heure française: {now_fr.strftime('%H:%M:%S')}")
    
    execute_pollution_check()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

print("🏁 Opération terminée")
