import os
import re
import sys
import json
import requests
import tweepy
import tracery
from colorama import Fore, Back, Style
from tracery.modifiers import base_english
from datetime import datetime

version = "v4.7.8"
script_dir = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
print(Fore.GREEN + f"####---> Capitales {version}" + Style.RESET_ALL)


def init_twitter_client():
    consumer_key = os.getenv("CAPITALES_CONSUMER_KEY")
    consumer_secret = os.getenv("CAPITALES_CONSUMER_SECRET")
    access_token = os.getenv("CAPITALES_ACCESS_TOKEN")
    access_token_secret = os.getenv("CAPITALES_ACCESS_TOKEN_SECRET")

    print(Fore.GREEN + "####---> Récupération des credentials..." + Style.RESET_ALL)

    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        print(Back.RED + Fore.BLACK + "####---> Missing Twitter API credentials" + Style.RESET_ALL)
        sys.exit()

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api_v1 = tweepy.API(auth)
    api_v2 = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    return api_v1, api_v2


def post_to_twitter(api_v2, quote):
    tweet = api_v2.create_tweet(text=quote[:280])
    print(Fore.GREEN + f'\n####---> Posted: ID={tweet[0]["id"]}' + Style.RESET_ALL)


def manage_index():
    """Gère l'index des pays/capitales déjà tweetés"""
    index_file = os.path.join(script_dir, "index.json")
    reset_needed = False

    if not os.path.exists(index_file):
        with open(index_file, 'w', encoding="utf-8") as f:
            json.dump({"used": []}, f)

    with open(index_file, 'r', encoding="utf-8") as f:
        index_data = json.load(f)

    # Nettoyage des doublons
    cleaned_used = []
    seen = set()
    for entry in index_data["used"]:
        if entry not in seen:
            seen.add(entry)
            cleaned_used.append(entry)

    index_data["used"] = cleaned_used

    # Sauvegarde propre
    with open(index_file, 'w', encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False)

    return index_data


def reset_index():
    """Réinitialise complètement l'index"""
    index_file = os.path.join(script_dir, "index.json")
    with open(index_file, 'w', encoding="utf-8") as f:
        json.dump({"used": []}, f)
    print(Fore.YELLOW + "####---> Index réinitialisé !" + Style.RESET_ALL)
    return {"used": []}


def tracery_magic():
    # Cherche bot.json
    if os.path.exists("bot.json"):
        bot_json_path = "bot.json"
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bot_json_path = os.path.join(script_dir, "bot.json")
        
        print(Fore.YELLOW + f"####---> Chemin du script: {script_dir}" + Style.RESET_ALL)
        print(Fore.YELLOW + f"####---> Recherche bot.json dans: {bot_json_path}" + Style.RESET_ALL)
        
        if not os.path.exists(bot_json_path):
            print(Back.RED + Fore.BLACK + f"####---> Fichier bot.json manquant!" + Style.RESET_ALL)
            print(Fore.YELLOW + "Contenu du dossier script:" + Style.RESET_ALL)
            os.system(f"ls -la {script_dir}")
            sys.exit()

    with open(bot_json_path, 'r', encoding="utf-8") as f:
        bot_data = json.load(f)
    
    # Gestion de l'index
    index_data = manage_index()
    used_countries = index_data["used"]
    
    # Vérifie si la clé "pays" existe
    if "pays" in bot_data:
        available_countries = []
        for pays in bot_data["pays"]:
            if pays not in used_countries:
                available_countries.append(pays)
        
        # Si tous les pays ont été utilisés, on réinitialise
        if not available_countries:
            print(Fore.YELLOW + "####---> Tous les pays ont été tweetés, réinitialisation de l'index..." + Style.RESET_ALL)
            reset_index()
            # Recharge l'index réinitialisé
            available_countries = bot_data["pays"].copy()
            print(Fore.GREEN + f"####---> {len(available_countries)} pays disponibles" + Style.RESET_ALL)
        
        # Sauvegarde la liste originale et la remplace par celles disponibles
        original_pays = bot_data["pays"]
        bot_data["pays"] = available_countries
    else:
        original_pays = None
        available_countries = []
    
    grammar = tracery.Grammar(bot_data)
    grammar.add_modifiers(base_english)
    
    if isinstance(bot_data["origin"], list):
        origin_template = bot_data["origin"][0]
    else:
        origin_template = bot_data["origin"]
    
    quote = grammar.flatten(origin_template)
    
    # Restaure la liste originale des pays
    if original_pays is not None:
        bot_data["pays"] = original_pays
    
    # Extrait quel pays a été tweeté
    selected_country = None
    if available_countries:
        for pays in available_countries:
            country_name = pays.split(" est ")[0].replace("de l'", "").replace("de la ", "").replace("du ", "").replace("des ", "").strip()
            if country_name in quote or pays.split(" est ")[0] in quote:
                selected_country = pays
                print(Fore.CYAN + f"####---> Pays sélectionné : {country_name}" + Style.RESET_ALL)
                break
    
    if not selected_country:
        print(Fore.RED + "####---> ATTENTION : Aucun pays identifié dans le tweet !" + Style.RESET_ALL)

    raw_img_links = re.findall(r'\{img\s[^}]*\}', quote)
    parsed_quote = re.sub(r'\{img\s[^}]*\}', '', quote)
    imgs = re.findall(r'\bhttps?://[^}\s]+', ' '.join(raw_img_links))

    return parsed_quote, imgs, selected_country


def main():
    api_v1, api_v2 = init_twitter_client()
    quote, imgs, selected_country = tracery_magic()
    
    # Poste le tweet
    post_to_twitter(api_v2, quote)
    
    # Ajoute le pays à l'index après un tweet réussi
    if selected_country:
        index_data = manage_index()
        used_countries = index_data["used"]
        if selected_country not in used_countries:
            used_countries.append(selected_country)
            index_file = os.path.join(script_dir, "index.json")
            with open(index_file, 'w', encoding="utf-8") as f:
                json.dump({"used": used_countries}, f, ensure_ascii=False)
            country_name = selected_country.split(" est ")[0].replace("de l'", "").replace("de la ", "").replace("du ", "").replace("des ", "").strip()
            print(Fore.GREEN + f"####---> Pays ajouté à l'index : {country_name}" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + "####---> Aucun pays ajouté à l'index (non identifié)" + Style.RESET_ALL)
    
    print(Fore.GREEN + "####---> Bot terminé!" + Style.RESET_ALL)


if __name__ == "__main__":
    main()