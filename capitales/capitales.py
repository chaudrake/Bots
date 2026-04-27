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
import keep_alive
from colorama import Fore, Back, Style
from tracery.modifiers import base_english
from datetime import datetime
from dotenv import load_dotenv  # Ajout de cette importation

"""MISE A JOUR DU REPERTOIRE DE TRAVAIL POUR QUE CRON JOB MARCHE"""
#os.chdir('/home/pyth1on/capitales')
#version = "v4.7.8"

print(Fore.GREEN + f"####---> Capitales {version}" + Style.RESET_ALL)

def replit_check(using_replit):
    """Checking for server or replit mode"""
    if using_replit.lower() == "true":
        # Running flask web server to indicate bot status
        keep_alive.keep_alive()
        print(Fore.GREEN + "####---> Running in replit mode..." + Style.RESET_ALL)
        time.sleep(2)
    elif using_replit.lower() == "false":
        print(Fore.GREEN + "####---> Running in local/server mode..." + Style.RESET_ALL)
    else:
        print(Back.RED + Fore.BLACK +
              "####---> Please set 'using_replit' value in setting file to 'True' or 'False'"
              + Style.RESET_ALL)
        sys.exit()

def init_twitter_client():
    """Initialising Twitter API Client"""
    # Chargement des variables d'environnement depuis .env
    #load_dotenv('/home/pyth1on/.env')

    # Getting Twitter API Keys from environment variables
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_key = os.getenv("ACCESS_KEY")
    access_secret = os.getenv("ACCESS_SECRET")

print("Bot lancé")

    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        print(Back.RED + Fore.BLACK +
              "####---> Missing Twitter API credentials in .env file" +
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
    media_ids = []
    for img in imgs:
        try:
            filepath = f"temp-imgs/{img.rsplit('/',1)[1]}"
            request = requests.get(url=img, stream=True, timeout=60)
            with open(filepath, 'wb') as image:
                for chunk in request:
                    image.write(chunk)
            media = api_v1.media_upload(filepath)
            media_ids.append(media.media_id)
        except Exception as error:
            log_string = f"{error} for image {img}"
            add_to_log(log_string)
            backup_file = "temp-imgs/unavailable.jpg"
            media = api_v1.media_upload(backup_file)
            media_ids.append(media.media_id)
        finally:
            if os.path.isfile(filepath):
                os.remove(filepath)
    return media_ids

def post_to_twitter(api_v2, quote, include_datetime, media_ids=None):
    """Handles posting to twitter (with or without media)"""
    if include_datetime.lower() == 'true':
        quote = (f"[{str(datetime.now()).rsplit(':',1)[0]}]\n\n") + quote
    tweet = api_v2.create_tweet(media_ids=media_ids, text=quote)
    print(Fore.GREEN + f'\n####---> Posted: ID={tweet[0]["id"]}, QUOTE={quote}' +
          Style.RESET_ALL)

def manage_index():
    """Gère le fichier index des capitales déjà tweetées"""
    index_file = "index.json"

    # Si le fichier n'existe pas, on le crée vide
    if not os.path.exists(index_file):
        with open(index_file, 'w', encoding="utf-8") as f:
            json.dump({"used": []}, f)

    # Lecture du fichier index
    with open(index_file, 'r', encoding="utf-8") as f:
        index_data = json.load(f)

    # Vérification que la structure est correcte
    if "used" not in index_data:
        index_data = {"used": []}

    return index_data

def tracery_magic():
    """Génère une citation avec gestion des capitales déjà utilisées"""
    # Charger les données
    with open("bot.json", 'r', encoding="utf-8") as f:
        bot_data = json.load(f)

    # Gestion de l'index
    index_data = manage_index()
    used_capitals = index_data["used"]

    # Capitales disponibles = celles qui ne sont pas dans l'index
    available_capitals = []
    for capital in bot_data["pays"]:
        if capital not in used_capitals:
            available_capitals.append(capital)

    # Si aucune capitale disponible, on réinitialise l'index
    if not available_capitals:
        print(Fore.YELLOW + "####---> Toutes les capitales ont été tweetées, réinitialisation de l'index..." + Style.RESET_ALL)
        with open("index.json", 'w', encoding="utf-8") as f:
            json.dump({"used": []}, f)
        available_capitals = bot_data["pays"].copy()
        used_capitals = []

    # Sélection aléatoire parmi les capitales disponibles
    original_pays = bot_data["pays"]
    bot_data["pays"] = available_capitals

    grammar = tracery.Grammar(bot_data)
    grammar.add_modifiers(base_english)
    quote = grammar.flatten("#origin#")

    bot_data["pays"] = original_pays

    # Trouver la capitale utilisée et mettre à jour l'index
    selected_capital = None
    for cap in available_capitals:
        if cap in quote:
            selected_capital = cap
            break

    if selected_capital:
        used_capitals.append(selected_capital)
        with open("index.json", 'w', encoding="utf-8") as f:
            json.dump({"used": used_capitals}, f)

    # Traitement des images comme avant
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

def add_to_log(log_string):
    """Adds a new entry to the logfile"""
    print(Fore.YELLOW + f'####---> {log_string}' + Style.RESET_ALL)
    logger.exception(log_string)

def parse_args(args):
    """Parse arguments given to the bot"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--quote",
        help="Prints out a single quote by parsing the json file",
        action="store_true")
    parser.add_argument(
        "--tweet",
        help="Posts a tweet to twitter regardless of time interval",
        action="store_true")
    return parser.parse_args(args)

def main():
    """The main function for the bot."""
    # Initialising base settings
    config_file = "settings.py"
    config = configparser.ConfigParser()
    config.read(config_file)
    global settings
    settings = config['BotSettings']
    using_replit = settings["using_replit"]
    # DELAI ENTRE 2 TWEETS
    time_between_tweets = 43200
    include_datetime = settings["include_datetime"]
    global logger
    logger = init_logger()
    api_v1, api_v2 = init_twitter_client()

    # Parsing Arguments
    args = parse_args(sys.argv[1:])
    if args.quote:
        quote, imgs = tracery_magic()
        print(Fore.BLUE + f'\n{quote},{imgs}\n' + Style.RESET_ALL)
        sys.exit()
    if args.tweet:
        quote, imgs = tracery_magic()
        if not imgs:
            post_to_twitter(api_v2, quote, include_datetime)
        else:
            media_ids = get_imgs(api_v1, imgs)
            post_to_twitter(api_v2, quote, include_datetime, media_ids)
        sys.exit()

    # Replit check & bot/API initialization
    replit_check(using_replit)
    print(Fore.GREEN + "####---> Starting bot capitales." + Style.RESET_ALL)
    print(Fore.GREEN +
          f'####---> Time between tweets set to {time_between_tweets} seconds...' +
          Style.RESET_ALL)

    # The main loop of the bot
    while True:
        quote, imgs = tracery_magic()
        # Calculating time difference between tweets
        time_now = datetime.now()
        with open(config_file, 'r', encoding="utf-8") as settings_file:
            lines = settings_file.readlines()
        last_line_time_string = lines[-1].split("= ")[-1].split('\n')[0]
        last_tweet_time = datetime.strptime(last_line_time_string,
                                          "%Y-%m-%d %H:%M:%S.%f")
        time_diff = int(((time_now) - last_tweet_time).total_seconds())

        # Tweet decision based on time difference
        if time_diff >= time_between_tweets or "-" in str(time_diff):
            for count, num in enumerate(range(2), start=1):
                try:
                    if not imgs:
                        post_to_twitter(api_v2, quote, include_datetime)
                    else:
                        media_ids = get_imgs(api_v1, imgs)
                        post_to_twitter(api_v2, quote, include_datetime, media_ids)
                    lines[-1] = "last_tweet_time = " + str(time_now)
                    with open(config_file, 'w', encoding="utf-8") as settings_file:
                        settings_file.writelines(lines)
                    break
                except Exception as error:
                    log_string = f'An error has occured Capitales: {error}'
                    add_to_log(log_string)
                    if count < 2:
                        quote, imgs = tracery_magic()
                        retry_after = 30
                        print(Back.RED + Fore.BLACK +
                              f"####---> Retrying in {retry_after} seconds..." +
                              Style.RESET_ALL)
                        time.sleep(retry_after)
            time.sleep(time_between_tweets)
        else:
            diff = time_between_tweets - time_diff
            print(Fore.GREEN + f'####---> Sleeping for {diff} seconds...' +
                  Style.RESET_ALL)
            time.sleep(diff)

if __name__ == "__main__":
    main()
