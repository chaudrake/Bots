# le script comprend un index pour ne pas tweeter 2 fois le meme drapeau.
import os
import re
import time
import sys
import json
import requests
import configparser
import argparse
import logging
import tweepy
import tracery
from colorama import Fore, Back, Style
from tracery.modifiers import base_english
from datetime import datetime
from dotenv import load_dotenv

version = "v4.7.8"
print(Fore.GREEN + f"####---> Drapeaux {version}" + Style.RESET_ALL)


def init_twitter_client():
    """Initialising Twitter API Client"""
    # Chargement des variables d'environnement depuis GitHub Secrets
    consumer_key = os.getenv("DRAPEAUX_CONSUMER_KEY")
    consumer_secret = os.getenv("DRAPEAUX_CONSUMER_SECRET")
    access_token = os.getenv("DRAPEAUX_ACCESS_TOKEN")
    access_token_secret = os.getenv("DRAPEAUX_ACCESS_TOKEN_SECRET")

    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        print(Back.RED + Fore.BLACK +
              "####---> Missing Twitter API credentials" +
              Style.RESET_ALL)
        sys.exit()

    print(Fore.GREEN + "####---> Obtained Credentials..." + Style.RESET_ALL)

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api_v1 = tweepy.API(auth)
    api_v2 = tweepy.Client(consumer_key=consumer_key,
                         consumer_secret=consumer_secret,
                         access_token=access_token,
                         access_token_secret=access_token_secret)
    return api_v1, api_v2


def get_imgs(api_v1, imgs):
    """Downloads images from url list and returns image filepaths"""
    # Crée le dossier temp-imgs s'il n'existe pas
    os.makedirs("temp-imgs", exist_ok=True)
    
    media_ids = []
    for img in imgs:
        try:
            filename = img.rsplit('/',1)[1]
            filepath = f"temp-imgs/{filename}"
            print(Fore.BLUE + f"####---> Téléchargement de l'image : {filename}" + Style.RESET_ALL)

            request = requests.get(url=img, stream=True, timeout=60)
            with open(filepath, 'wb') as image:
                for chunk in request:
                    image.write(chunk)

            print(Fore.BLUE + f"####---> Upload de l'image vers Twitter..." + Style.RESET_ALL)
            media = api_v1.media_upload(filepath)
            media_ids.append(media.media_id)
            print(Fore.GREEN + f"####---> Image uploadée avec succès : {filename}" + Style.RESET_ALL)

        except Exception as error:
            log_string = f"ERREUR image {img} : {error}"
            print(Fore.RED + f"####---> {log_string}" + Style.RESET_ALL)

        finally:
            if 'filepath' in locals() and os.path.isfile(filepath):
                os.remove(filepath)
                print(Fore.BLUE + f"####---> Fichier temporaire supprimé : {filename}" + Style.RESET_ALL)

    return media_ids


def post_to_twitter(api_v2, quote, include_datetime, media_ids=None):
    """Handles posting to twitter (with or without media)"""
    if include_datetime.lower() == 'true':
        quote = (f"[{str(datetime.now()).rsplit(':',1)[0]}]\n\n") + quote
    tweet = api_v2.create_tweet(media_ids=media_ids, text=quote[:280])
    print(Fore.GREEN + f'\n####---> Posted: ID={tweet[0]["id"]}' + Style.RESET_ALL)


def manage_index():
    """Gère le fichier index des drapeaux déjà tweetés (version simplifiée)"""
    index_file = "index.json"

    if not os.path.exists(index_file):
        with open(index_file, 'w', encoding="utf-8") as f:
            json.dump({"used": []}, f)

    with open(index_file, 'r', encoding="utf-8") as f:
        index_data = json.load(f)

    cleaned_used = []
    seen = set()
    for entry in index_data["used"]:
        country_name = entry.split("{")[0].strip()
        if country_name not in seen:
            seen.add(country_name)
            cleaned_used.append(country_name)

    index_data["used"] = cleaned_used

    with open(index_file, 'w', encoding="utf-8") as f:
        json.dump(index_data, f)

    return index_data


def tracery_magic():
    """Version avec index simplifié (noms de pays seulement)"""
    with open("bot.json", 'r', encoding="utf-8") as f:
        bot_data = json.load(f)

    index_data = manage_index()
    used_flags = index_data["used"]

    available_flags = []
    for flag in bot_data["drapeau"]:
        country_name = flag.split("{")[0].strip()
        if country_name not in used_flags:
            available_flags.append(flag)

    if not available_flags:
        print(Fore.YELLOW + "####---> Tous les drapeaux ont été tweetés, réinitialisation de l'index..." + Style.RESET_ALL)
        with open("index.json", 'w', encoding="utf-8") as f:
            json.dump({"used": []}, f)
        available_flags = bot_data["drapeau"].copy()

    original_data = bot_data["drapeau"]
    bot_data["drapeau"] = available_flags

    grammar = tracery.Grammar(bot_data)
    grammar.add_modifiers(base_english)
    quote = grammar.flatten("#origin#")

    bot_data["drapeau"] = original_data

    selected_country_name = None
    for flag in available_flags:
        country_name = flag.split("{")[0].strip()
        if country_name in quote:
            selected_country_name = country_name
            break

    if selected_country_name:
        print(Fore.CYAN + f"####---> Pays sélectionné : {selected_country_name}" + Style.RESET_ALL)
    else:
        print(Fore.RED + "####---> ATTENTION : Aucun pays identifié dans le quote !" + Style.RESET_ALL)

    raw_img_links = re.findall(r'\{img\s[^}]*\}', quote)
    parsed_quote = re.sub(r'\{img\s[^}]*\}', '', quote)
    imgs = re.findall(r'\bhttps?://[^}\s]+', ' '.join(raw_img_links))

    return parsed_quote, imgs, selected_country_name


def main():
    """The main function for the bot."""
    api_v1, api_v2 = init_twitter_client()
    
    quote, imgs, selected_country = tracery_magic()
    
    if not imgs:
        post_to_twitter(api_v2, quote, "false")
    else:
        media_ids = get_imgs(api_v1, imgs)
        post_to_twitter(api_v2, quote, "false", media_ids)

    # Ajouter à l'index après tweet réussi
    if selected_country:
        index_data = manage_index()
        used_flags = index_data["used"]
        if selected_country not in used_flags:
            used_flags.append(selected_country)
            with open("index.json", 'w', encoding="utf-8") as f:
                json.dump({"used": used_flags}, f)
            print(Fore.GREEN + f"####---> Pays ajouté à l'index : {selected_country}" + Style.RESET_ALL)
    
    print(Fore.GREEN + "####---> Bot terminé!" + Style.RESET_ALL)


if __name__ == "__main__":
    main()
