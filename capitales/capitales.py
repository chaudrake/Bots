import os
import re
import time
import sys
import json
import requests
import argparse
import logging
import tweepy
import tracery
from colorama import Fore, Back, Style
from tracery.modifiers import base_english
from datetime import datetime

version = "v4.7.8"

print(Fore.GREEN + f"####---> Capitales {version}" + Style.RESET_ALL)


def init_twitter_client():
    """Initialising Twitter API Client"""
    consumer_key = os.getenv("CAPITALES_CONSUMER_KEY")
    consumer_secret = os.getenv("CAPITALES_CONSUMER_SECRET")
    access_token = os.getenv("CAPITALES_ACCESS_TOKEN")
    access_token_secret = os.getenv("CAPITALES_ACCESS_TOKEN_SECRET")

    print(Fore.GREEN + "####---> Récupération des credentials..." + Style.RESET_ALL)
    print(f"Consumer Key présente: {bool(consumer_key)}")
    print(f"Access Token présente: {bool(access_token)}")

    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        print(Back.RED + Fore.BLACK +
              "####---> Missing Twitter API credentials in environment variables" +
              Style.RESET_ALL)
        sys.exit()

    print(Fore.GREEN + "####---> Credentials obtenus avec succès!" + Style.RESET_ALL)

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


def get_imgs(api_v1, imgs):
    """Downloads images from url list and returns image filepaths"""
    os.makedirs("temp-imgs", exist_ok=True)

    media_ids = []
    for img in imgs:
        try:
            filepath = f"temp-imgs/{img.rsplit('/', 1)[1]}"
            request = requests.get(url=img, stream=True, timeout=60)
            with open(filepath, 'wb') as image:
                for chunk in request:
                    image.write(chunk)
            media = api_v1.media_upload(filepath)
            media_ids.append(media.media_id)
        except Exception as error:
            log_string = f"{error} for image {img}"
            print(Fore.YELLOW + f'####---> {log_string}' + Style.RESET_ALL)
            backup_file = "temp-imgs/unavailable.jpg"
            if os.path.isfile(backup_file):
                media = api_v1.media_upload(backup_file)
                media_ids.append(media.media_id)
        finally:
            if os.path.isfile(filepath):
                os.remove(filepath)
    return media_ids


def post_to_twitter(api_v2, quote, include_datetime, media_ids=None):
    """Handles posting to twitter (with or without media)"""
    if include_datetime:
        quote = (f"[{str(datetime.now()).rsplit(':', 1)[0]}]\n\n") + quote
    tweet = api_v2.create_tweet(media_ids=media_ids, text=quote[:280])
    print(Fore.GREEN + f'\n####---> Posted: ID={tweet[0]["id"]}' + Style.RESET_ALL)


def manage_index():
    """Gère le fichier index des capitales déjà tweetées"""
    index_file = "index.json"

    if not os.path.exists(index_file):
        with open(index_file, 'w', encoding="utf-8") as f:
            json.dump({"used": []}, f)

    with open(index_file, 'r', encoding="utf-8") as f:
        index_data = json.load(f)

    if "used" not in index_data:
        index_data = {"used": []}

    return index_data


def tracery_magic():
    """Génère une citation avec gestion des capitales déjà utilisées"""
    if not os.path.exists("bot.json"):
        print(Back.RED + Fore.BLACK +
              "####---> Fichier bot.json manquant!" + Style.RESET_ALL)
        sys.exit()

    with open("bot.json", 'r', encoding="utf-8") as f:
        bot_data = json.load(f)

    index_data = manage_index()
    used_capitals = index_data["used"]

    available_capitals = []
    for capital in bot_data["pays"]:
        if capital not in used_capitals:
            available_capitals.append(capital)

    if not available_capitals:
        print(Fore.YELLOW + "####---> Toutes les capitales ont été tweetées, réinitialisation..." + Style.RESET_ALL)
        with open("index.json", 'w', encoding="utf-8") as f:
            json.dump({"used": []}, f)
        available_capitals = bot_data["pays"].copy()
        used_capitals = []

    original_pays = bot_data["pays"]
    bot_data["pays"] = available_capitals

    grammar = tracery.Grammar(bot_data)
    grammar.add_modifiers(base_english)
    quote = grammar.flatten("#origin#")

    bot_data["pays"] = original_pays

    selected_capital = None
    for cap in available_capitals:
        if cap in quote:
            selected_capital = cap
            break

    if selected_capital:
        used_capitals.append(selected_capital)
        with open("index.json", 'w', encoding="utf-8") as f:
            json.dump({"used": used_capitals}, f)

    raw_img_links = re.findall(r'\{img\s[^}]*\}', quote)
    parsed_quote = re.sub(r'\{img\s[^}]*\}', '', quote)
    imgs = re.findall(r'\bhttps?://[^}\s]+', ' '.join(raw_img_links))

    return parsed_quote, imgs


def init_logger():
    """Initializes the logger"""
    logger = logging.getLogger("Twitter-Bot")
    log_format = logging.Formatter('\n%(asctime)s %(message)s')
    log_file = logging.FileHandler('bot.log')
    log_file.setFormatter(log_format)
    logger.addHandler(log_file)
    return logger


def main():
    """The main function for the bot."""
    global logger
    logger = init_logger()
    api_v1, api_v2 = init_twitter_client()

    quote, imgs = tracery_magic()

    if not imgs:
        post_to_twitter(api_v2, quote, True)
    else:
        media_ids = get_imgs(api_v1, imgs)
        post_to_twitter(api_v2, quote, True, media_ids)

    print(Fore.GREEN + "####---> Bot terminé avec succès!" + Style.RESET_ALL)


if __name__ == "__main__":
    main()
