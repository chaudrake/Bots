# Bot Twitter de suggestions de repas - Choix selon l'heure
# Tweete à 6h (petit-déj), 11h (déjeuner), 18h (dîner)
# Adapté pour GitHub Actions

import tweepy
import os
import sys
import time
import pytz
from datetime import datetime
import random
import json
import unicodedata
import re

# Récupérer les variables d'environnement (GitHub Secrets)
CONSUMER_KEY = os.getenv('REPAS_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('REPAS_CONSUMER_SECRET')
ACCESS_KEY = os.getenv('REPAS_ACCESS_KEY')
ACCESS_SECRET = os.getenv('REPAS_ACCESS_SECRET')

# Vérification des credentials
if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]):
    print("❌ Missing Twitter API credentials")
    sys.exit(1)

print("✅ Démarrage du script Repas")

france_tz = pytz.timezone('Europe/Paris')

# Fichiers de configuration (chemins relatifs)
STATE_FILE = "meal_state.json"
MEALS_DATA_FILE = "meals_data.json"

def is_summer_time():
    """Détecte l'heure d'été (UTC+2)"""
    now = datetime.now(france_tz)
    return now.utcoffset() == pytz.FixedOffset(120)

def wait_for_adjustment():
    """Ajuste l'exécution pour être à l'heure française"""
    now = datetime.now(france_tz)
    current_hour = now.hour
    
    # Déterminer l'heure cible selon le moment de la journée
    if 5 <= current_hour < 10:
        target_hour = 6
        meal_name = "petit-déjeuner (6h)"
    elif 10 <= current_hour < 15:
        target_hour = 11
        meal_name = "déjeuner (11h)"
    elif 17 <= current_hour < 21:
        target_hour = 18
        meal_name = "dîner (18h)"
    else:
        # En dehors des plages, on ne tweete pas
        return False
    
    # Calculer l'attente nécessaire
    if current_hour < target_hour:
        wait_seconds = (target_hour - current_hour) * 3600 - now.minute * 60 - now.second
        if wait_seconds > 0:
            print(f"⏰ Attente de {wait_seconds//3600}h{(wait_seconds%3600)//60}min pour {meal_name}")
            time.sleep(wait_seconds)
    elif current_hour > target_hour:
        # Déjà après l'heure cible (cas du cron trop tard)
        print(f"⚠️ Déjà après {target_hour}h, tweet immédiat")
    
    return True

def get_current_meal_type():
    """Détermine le type de repas en fonction de l'heure française"""
    now = datetime.now(france_tz)
    current_hour = now.hour

    if 5 <= current_hour < 10:
        return "petit_dejeuner"
    elif 10 <= current_hour < 15:
        return "dejeuner"
    elif 17 <= current_hour < 21:
        return "diner"
    else:
        return None

def normalize_label(s: str) -> str:
    """Normalise une étiquette de plat pour comparaison robuste"""
    if not isinstance(s, str):
        s = str(s)
    s = unicodedata.normalize("NFKC", s)
    s = " ".join(s.strip().split())
    return s.lower()

def extract_keywords(dish_name):
    """Extrait les mots-clés importants d'un nom de plat"""
    stop_words = {
        'de', 'du', 'des', 'à', 'au', 'aux', 'en', 'avec', 'sans', 'et', 'ou',
        'sur', 'sous', 'dans', 'pour', 'par', 'le', 'la', 'les', 'un', 'une',
        'maison', 'accompagné', 'accompagnée', 'quelques', 'rondelles'
    }

    normalized = normalize_label(dish_name)
    words = re.findall(r'\b\w+\b', normalized)
    keywords = [word for word in words if len(word) > 2 and word not in stop_words]
    return set(keywords)

def has_conflicting_keywords(starter, main_course, max_common_keywords=2):
    """Vérifie si l'entrée et le plat principal ont trop de mots-clés en commun"""
    starter_keywords = extract_keywords(starter)
    main_keywords = extract_keywords(main_course)

    similar_preparations = {
        'flan', 'cake', 'beignet', 'gratin', 'tarte', 'quiche', 'soufflé',
        'terrine', 'rillettes', 'pâté', 'velouté', 'soupe', 'salade'
    }

    starter_preps = starter_keywords.intersection(similar_preparations)
    main_preps = main_keywords.intersection(similar_preparations)

    if starter_preps and main_preps:
        print(f"⚠️ Conflit de préparation: {starter_preps} vs {main_preps}")
        return True

    common_ingredients = starter_keywords.intersection(main_keywords)
    if len(common_ingredients) > max_common_keywords:
        print(f"⚠️ Trop d'ingrédients communs: {common_ingredients}")
        return True

    return False

def load_meal_state():
    """Charge l'état depuis le fichier"""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r', encoding="utf-8") as f:
                state = json.load(f)
            
            # Migration si nécessaire
            for key in ["used_petit_dejeuner", "used_repas_principal", "used_entrees"]:
                if key not in state or not isinstance(state[key], list):
                    state[key] = []
            
            return state
    except Exception as e:
        print(f"❌ Erreur lecture état: {e}")
    
    return {
        "used_petit_dejeuner": [],
        "used_repas_principal": [],
        "used_entrees": []
    }

def save_meal_state(state):
    """Sauvegarde l'état dans le fichier"""
    try:
        with open(STATE_FILE, 'w', encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Erreur sauvegarde état: {e}")

class MealGenerator:
    def __init__(self):
        try:
            with open(MEALS_DATA_FILE, 'r', encoding='utf-8') as f:
                self.meals_data = json.load(f)
            print(f"✅ Données repas chargées depuis {MEALS_DATA_FILE}")
        except Exception as e:
            print(f"❌ Erreur chargement données repas: {e}")
            sys.exit(1)

    @property
    def meals(self):
        return {
            "petit_dejeuner": self.meals_data.get("petit_dejeuner", []),
            "repas_principal": self.meals_data.get("repas_principal", [])
        }

    @property
    def starters(self):
        return self.meals_data.get("entrees", [])

    def _pick_random_without_repeat(self, options, used_list_key, state, label_for_logs):
        used_norm = {normalize_label(x) for x in state[used_list_key]}
        remaining = [x for x in options if normalize_label(x) not in used_norm]

        if not remaining:
            print(f"🔁 {label_for_logs}: tous utilisés → remise à zéro.")
            state[used_list_key] = []
            remaining = list(options)

        choice = random.choice(remaining)
        state[used_list_key].append(choice)
        print(f"🎯 {label_for_logs} choisi: {choice}")
        return choice

    def _find_compatible_pair(self, starters_options, main_courses_options, state, max_attempts=50):
        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            starter = self._pick_random_without_repeat(starters_options, "used_entrees", state, "Entrée (tentative)")
            main_course = self._pick_random_without_repeat(main_courses_options, "used_repas_principal", state, "Plat principal (tentative)")
            
            if not has_conflicting_keywords(starter, main_course):
                print(f"✅ Paire compatible trouvée après {attempts} tentative(s)")
                return starter, main_course
            
            print(f"🔄 Conflit détecté, nouvelle tentative ({attempts}/{max_attempts})")
            state["used_entrees"].pop()
            state["used_repas_principal"].pop()
        
        print("⚠️ Impossible de trouver une paire parfaite, utilisation de la dernière tentative")
        return starter, main_course

    def generate_meal(self, meal_type, state):
        if meal_type not in ["petit_dejeuner", "dejeuner", "diner"]:
            return None

        if meal_type == "petit_dejeuner":
            plat_principal = self._pick_random_without_repeat(
                self.meals["petit_dejeuner"], "used_petit_dejeuner", state, "Petit-déjeuner"
            )
            drink = "Une boisson chaude (café, thé vert...) et/ou un jus de fruits et/ou une boisson détox."
            return {
                "type": meal_type,
                "plat_principal": plat_principal,
                "entree": None,
                "drink": drink
            }
        else:
            entree, plat_principal = self._find_compatible_pair(
                self.starters, self.meals["repas_principal"], state
            )
            return {
                "type": meal_type,
                "plat_principal": plat_principal,
                "entree": entree,
                "drink": None
            }

def generate_tweet(meal_data):
    """Génère le texte du tweet"""
    emojis = {"petit_dejeuner": "☀️", "dejeuner": "🍳", "diner": "🍽️"}
    hashtags = {"petit_dejeuner": "#PetitDéjeuner #BonAppétit", "dejeuner": "#Déjeuner #BonAppétit", "diner": "#Dîner #BonAppétit"}
    
    current_date = datetime.now(france_tz).strftime("%d/%m")
    meal_translations = {"petit_dejeuner": "petit-déjeuner", "dejeuner": "déjeuner", "diner": "dîner"}
    meal_type_fr = meal_translations[meal_data['type']]

    tweet_lines = [f"{emojis[meal_data['type']]} Proposition de {meal_type_fr} du {current_date} :", ""]

    if meal_data['entree']:
        tweet_lines.append(f"🥗 Entrée : {meal_data['entree']}.")
    if meal_data['type'] == "petit_dejeuner":
        tweet_lines.append(f"🍽️ {meal_data['plat_principal']}.")
    else:
        tweet_lines.append(f"🍽️ Plat : {meal_data['plat_principal']}.")
    if meal_data['drink']:
        tweet_lines.append(f"🥤 {meal_data['drink']}")

    tweet_lines.extend(["", hashtags[meal_data['type']]])
    return "\n".join(tweet_lines)[:280]

def post_tweet(tweet_text):
    """Poste le tweet sur Twitter"""
    try:
        client = tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_KEY,
            access_token_secret=ACCESS_SECRET
        )
        response = client.create_tweet(text=tweet_text)
        print(f"✅ Tweet publié : {response.data['id']}")
        return True
    except Exception as e:
        print(f"❌ Erreur publication : {e}")
        return False

def execute_nutrition_tweet():
    """Exécute le processus complet de tweet Repas"""
    print("🍽️ Génération de suggestion de repas...")

    meal_type = get_current_meal_type()
    if not meal_type:
        print("❌ Aucun repas programmé à cette heure")
        return

    print(f"📋 Type de repas: {meal_type}")

    state = load_meal_state()
    generator = MealGenerator()
    meal_data = generator.generate_meal(meal_type, state)

    if not meal_data:
        print("❌ Erreur lors de la génération du repas")
        return

    save_meal_state(state)
    print("💾 État sauvegardé")

    tweet_text = generate_tweet(meal_data)
    print(f"📝 Tweet généré ({len(tweet_text)} caractères)")
    print("-" * 40)
    print(tweet_text)
    print("-" * 40)

    success = post_tweet(tweet_text)
    print("✅ Tweet Repas publié!" if success else "❌ Échec de la publication")

def main():
    # Attendre l'heure cible si nécessaire
    if not wait_for_adjustment():
        print("⏭️ En dehors des plages horaires, arrêt")
        return
    
    now = datetime.now(france_tz)
    print(f"🕐 Heure française: {now.strftime('%H:%M:%S')}")
    
    execute_nutrition_tweet()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

print("🏁 Opération terminée")
