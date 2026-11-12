# PollutionAqi.py - Tweet l'indice AQI uniquement (Requêtes groupées Open-Meteo)
import json
import requests
import tweepy
import os
import sys
import pytz
from datetime import datetime

# Récupérer les variables d'environnement (GitHub Secrets)
CONSUMER_KEY = os.getenv('POLLUTION_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('POLLUTION_CONSUMER_SECRET')
ACCESS_KEY = os.getenv('POLLUTION_ACCESS_KEY')
ACCESS_SECRET = os.getenv('POLLUTION_ACCESS_SECRET')

# Vérification des credentials Twitter
if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]):
    print("❌ Missing Twitter API credentials")
    sys.exit(1)

print("✅ Démarrage du script Pollution (Mode AQI groupé)")

france_tz = pytz.timezone('Europe/Paris')

def load_cities():
    """Charge la liste des villes depuis le fichier JSON"""
    with open('cities.json', 'r', encoding='utf-8') as f:
        cities_data = json.load(f)
        return [{"name": name, "lat": data["lat"], "lon": data["lon"]} for name, data in cities_data.items()]

def fetch_all_aqi_openmeteo(cities):
    """Récupère l'AQI de toutes les villes par lots de 100 en une seule requête par lot"""
    results = []
    batch_size = 100
    host = ".".join(["air-quality-api", "open-meteo", "com"])
    base_url = f"https://{host}/v1/air-quality"

    
    for i in range(0, len(cities), batch_size):
        batch = cities[i:i + batch_size]
        lats = ",".join(str(c["lat"]) for c in batch)
        lons = ",".join(str(c["lon"]) for c in batch)
        
        params = {
            "latitude": lats,
            "longitude": lons,
            "current": "us_aqi"
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Si une seule ville dans le lot, Open-Meteo renvoie un dict, sinon une liste de dicts
            if isinstance(data, dict):
                data = [data]
                
            for city, item in zip(batch, data):
                if 'current' in item and item['current'].get('us_aqi') is not None:
                    results.append({
                        "city": city["name"],
                        "aqi": item['current']['us_aqi'],
                        "source": "Open-Meteo"
                    })
        except Exception as e:
            print(f"❌ Erreur lors de la requête Open-Meteo (lot {i // batch_size + 1}) : {e}")
            
    return results

def generate_aqi_tweet(polluted_cities):
    current_time = datetime.now(france_tz).strftime("%Hh%M")
    tweet_header = f"🌍 #Pollution à {current_time}. Indice Air Quality Index (AQI).\n\n🔴 Villes les plus polluées : 🔴\n"
    first_city = next(iter(polluted_cities))
    tweet_footer = f"\nSource : {first_city['source']}"
    
    for num_cities in (5, 3, 1):
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
        print("✅ Tweet AQI publié avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur publication : {e}")
        return False

def execute_pollution_check():
    print("🔍 Lancement du relevé de l'indice AQI...")
    cities = load_cities()
    print(f"📋 {len(cities)} villes chargées")

    # Récupération groupée (3 requêtes au lieu de 287)
    aqi_data = fetch_all_aqi_openmeteo(cities)

    print(f"📊 Données récupérées pour {len(aqi_data)}/{len(cities)} villes")

    if len(aqi_data) < 3:
        print("⚠️ Pas assez de données AQI récupérées pour faire un classement.")
        return

    # Tri des villes de la plus polluée à la moins polluée
    top_aqi = sorted(aqi_data, key=lambda x: x['aqi'], reverse=True)[:5]
    print(f"🏆 Top 5 : {top_aqi}")
    
    # Génération et publication du tweet unique
    aqi_tweet = generate_aqi_tweet(top_aqi)
    if aqi_tweet:
        post_tweet(aqi_tweet)
    else:
        print("❌ Impossible de générer un tweet valide.")

def main():
    now_fr = datetime.now(france_tz)
    print(f"🕐 Heure française d'exécution : {now_fr.strftime('%H:%M:%S')}")
    execute_pollution_check()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)
