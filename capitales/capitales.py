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
    """Gère l'index des capitales déjà tweetées"""
    index_file = os.path.join(script_dir, "index.json")

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

    with open(index_file, 'w', encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False)

    return index_data


def tracery_magic():
    # Cherche bot.json dans le répertoire courant d'abord, puis dans le répertoire du script
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
    
    # Gestion de l'index - filtre les capitales déjà utilisées
    index_data = manage_index()
    used_capitals = index_data["used"]
    
    # Vérifie si la clé "capitale" existe dans bot_data
    if "capitale" in bot_data:
        available_capitals = []
        for capitale in bot_data["capitale"]:
            # Compare la chaîne complète (ex: "de la FRANCE est PARIS.")
            if capitale not in used_capitals:
                available_capitals.append(capitale)
        
        # Si toutes les capitales ont été utilisées, on réinitialise
        if not available_capitals:
            print(Fore.YELLOW + "####---> Toutes les capitales ont été tweetées, réinitialisation de l'index..." + Style.RESET_ALL)
            with open(os.path.join(script_dir, "index.json"), 'w', encoding="utf-8") as f:
                json.dump({"used": []}, f)
            available_capitals = bot_data["capitale"].copy()
        
        # Sauvegarde la liste originale et la remplace par celles disponibles
        original_capitals = bot_data["capitale"]
        bot_data["capitale"] = available_capitals
    else:
        original_capitals = None
        available_capitals = []
    
    grammar = tracery.Grammar(bot_data)
    grammar.add_modifiers(base_english)
    quote = grammar.flatten("#origin#")
    
    # Restaure la liste originale des capitales
    if original_capitals is not None:
        bot_data["capitale"] = original_capitals
    
    # Extrait quelle capitale a été tweetée
    selected_capital = None
    if available_capitals:
        for capitale in available_capitals:
            if capitale in quote:
                selected_capital = capitale
                print(Fore.CYAN + f"####---> Capitale sélectionnée : {capitale.split('est')[0].strip().upper() if 'est' in capitale else capitale}" + Style.RESET_ALL)
                break
    
    if not selected_capital:
        print(Fore.RED + "####---> ATTENTION : Aucune capitale identifiée dans le tweet !" + Style.RESET_ALL)

    raw_img_links = re.findall(r'\{img\s[^}]*\}', quote)
    parsed_quote = re.sub(r'\{img\s[^}]*\}', '', quote)
    imgs = re.findall(r'\bhttps?://[^}\s]+', ' '.join(raw_img_links))

    return parsed_quote, imgs, selected_capital


def main():
    api_v1, api_v2 = init_twitter_client()
    quote, imgs, selected_capital = tracery_magic()
    
    # Poste le tweet
    post_to_twitter(api_v2, quote)
    
    # Ajoute la capitale à l'index après un tweet réussi
    if selected_capital:
        index_data = manage_index()
        used_capitals = index_data["used"]
        if selected_capital not in used_capitals:
            used_capitals.append(selected_capital)
            index_file = os.path.join(script_dir, "index.json")
            with open(index_file, 'w', encoding="utf-8") as f:
                json.dump({"used": used_capitals}, f, ensure_ascii=False)
            print(Fore.GREEN + f"####---> Capitale ajoutée à l'index : {selected_capital.split('est')[0].strip() if 'est' in selected_capital else selected_capital}" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + "####---> Aucune capitale ajoutée à l'index (non identifiée)" + Style.RESET_ALL)
    
    print(Fore.GREEN + "####---> Bot terminé!" + Style.RESET_ALL)


if __name__ == "__main__":
    main()
