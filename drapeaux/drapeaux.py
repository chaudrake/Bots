#le script comprend un index pour ne pas tweeter 2 fois le meme drapeau.
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
#os.chdir('/home/pyth1on/drapeaux')
version = "v4.7.8"

#print(Fore.GREEN + f"####---> Drapeaux {version}" + Style.RET_ALL)

def replit_check(using_replit):
    """Checking for server or replit mode"""
    if using_replit.lower() == "true":
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
    load_dotenv('/home/pyth1on/.env')

    # Getting Twitter API Keys from environment variables
    consumer_key = os.getenv('DRAPEAUX_consumer_key')
    consumer_secret = os.getenv('DRAPEAUX_consumer_secret')
    access_token = os.getenv('DRAPEAUX_access_token')
    access_token_secret = os.getenv('DRAPEAUX_access_token_secret')

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
            add_to_log(log_string)

            # Utiliser une image de backup
            backup_file = "temp-imgs/unavailable.jpg"
            try:
                media = api_v1.media_upload(backup_file)
                media_ids.append(media.media_id)
                print(Fore.YELLOW + f"####---> Utilisation de l'image de backup" + Style.RESET_ALL)
            except Exception as backup_error:
                log_string = f"ERREUR backup image : {backup_error}"
                print(Fore.RED + f"####---> {log_string}" + Style.RESET_ALL)
                add_to_log(log_string)

        finally:
            if 'filepath' in locals() and os.path.isfile(filepath):
                os.remove(filepath)
                print(Fore.BLUE + f"####---> Fichier temporaire supprimé : {filename}" + Style.RESET_ALL)

    return media_ids

def post_to_twitter(api_v2, quote, include_datetime, media_ids=None):
    """Handles posting to twitter (with or without media)"""
    if include_datetime.lower() == 'true':
        quote = (f"[{str(datetime.now()).rsplit(':',1)[0]}]\n\n") + quote
    tweet = api_v2.create_tweet(media_ids=media_ids, text=quote)
    print(Fore.GREEN + f'\n####---> Posted: ID={tweet[0]["id"]}, QUOTE={quote}' +
          Style.RESET_ALL)

def manage_index():
    """Gère le fichier index des drapeaux déjà tweetés (version simplifiée)"""
    index_file = "index.json"

    # Si le fichier n'existe pas, on le crée vide
    if not os.path.exists(index_file):
        with open(index_file, 'w', encoding="utf-8") as f:
            json.dump({"used": []}, f)

    # Lecture du fichier index
    with open(index_file, 'r', encoding="utf-8") as f:
        index_data = json.load(f)

    # Nettoyage des doublons et suppression des URLs
    cleaned_used = []
    seen = set()
    for entry in index_data["used"]:
        # Extraire juste le nom du pays (supprime la partie {img...})
        country_name = entry.split("{")[0].strip()
        if country_name not in seen:
            seen.add(country_name)
            cleaned_used.append(country_name)

    index_data["used"] = cleaned_used

    # Sauvegarder l'index nettoyé
    with open(index_file, 'w', encoding="utf-8") as f:
        json.dump(index_data, f)

    return index_data

def tracery_magic():
    """Version avec index simplifié (noms de pays seulement)"""
    with open("bot.json", 'r', encoding="utf-8") as f:
        bot_data = json.load(f)

    index_data = manage_index()
    used_flags = index_data["used"]

    # Drapeaux disponibles
    available_flags = []
    for flag in bot_data["drapeau"]:
        country_name = flag.split("{")[0].strip()
        decoded_country_name = json.loads(f'"{country_name}"')
        decoded_used_flags = [json.loads(f'"{flag}"') for flag in used_flags]
        if decoded_country_name not in decoded_used_flags:
            available_flags.append(flag)

    # Réinitialisation si besoin
    if not available_flags:
        print(Fore.YELLOW + "####---> Tous les drapeaux ont été tweetés, réinitialisation de l'index..." + Style.RESET_ALL)
        with open("index.json", 'w', encoding="utf-8") as f:
            json.dump({"used": []}, f)
        available_flags = bot_data["drapeau"].copy()

    # Sélection aléatoire
    original_data = bot_data["drapeau"]
    bot_data["drapeau"] = available_flags

    grammar = tracery.Grammar(bot_data)
    grammar.add_modifiers(base_english)
    quote = grammar.flatten("#origin#")

    bot_data["drapeau"] = original_data

    # Identifier le pays sélectionné
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

    # Traitement des images
    raw_img_links = re.findall(r'\{img\s[^}]*\}', quote)
    parsed_quote = re.sub(r'\{img\s[^}]*\}', '', quote)
    imgs = re.findall(r'\bhttps?://[^}\s]+', ' '.join(raw_img_links))

    return parsed_quote, imgs, selected_country_name

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
    time_between_tweets = 43200  # DELAI ENTRE 2 TWEETS
    include_datetime = settings["include_datetime"]
    global logger
    logger = init_logger()
    api_v1, api_v2 = init_twitter_client()

    # Parsing Arguments
    args = parse_args(sys.argv[1:])
    if args.quote:
        quote, imgs, selected_country = tracery_magic()
        print(Fore.BLUE + f'\n{quote}\nImages: {imgs}\nPays: {selected_country}\n' + Style.RESET_ALL)
        sys.exit()
    if args.tweet:
        quote, imgs, selected_country = tracery_magic()
        if not imgs:
            post_to_twitter(api_v2, quote, include_datetime)
        else:
            media_ids = get_imgs(api_v1, imgs)
            post_to_twitter(api_v2, quote, include_datetime, media_ids)

        # Ajouter à l'index après tweet réussi
        if selected_country:
            index_data = manage_index()
            used_flags = index_data["used"]
            encoded_country = json.dumps(selected_country).strip('"')
            if encoded_country not in used_flags:
                used_flags.append(encoded_country)
                with open("index.json", 'w', encoding="utf-8") as f:
                    json.dump({"used": used_flags}, f)
                print(Fore.GREEN + f"####---> Pays ajouté à l'index : {selected_country}" + Style.RESET_ALL)
        sys.exit()

    # Replit check & bot/API initialization
    replit_check(using_replit)
    print(Fore.GREEN + "####---> Starting bot drapeaux." + Style.RESET_ALL)
    print(Fore.GREEN +
          f'####---> Time between tweets set to {time_between_tweets} seconds...' +
          Style.RESET_ALL)

    # The main loop of the bot
    while True:
        quote, imgs, selected_country = tracery_magic()
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
            tweet_success = False
            for attempt in range(2):  # 2 tentatives maximum
                try:
                    print(Fore.CYAN + f"####---> Tentative de tweet {attempt + 1}/2..." + Style.RESET_ALL)

                    if not imgs:
                        post_to_twitter(api_v2, quote, include_datetime)
                    else:
                        media_ids = get_imgs(api_v1, imgs)
                        post_to_twitter(api_v2, quote, include_datetime, media_ids)

                    # SEULEMENT SI LE TWEET RÉUSSIT
                    if selected_country:
                        index_data = manage_index()
                        used_flags = index_data["used"]
                        encoded_country = json.dumps(selected_country).strip('"')
                        if encoded_country not in used_flags:
                            used_flags.append(encoded_country)
                            with open("index.json", 'w', encoding="utf-8") as f:
                                json.dump({"used": used_flags}, f)
                            print(Fore.GREEN + f"####---> Pays ajouté à l'index : {selected_country}" + Style.RESET_ALL)

                    # Mettre à jour le temps du dernier tweet
                    lines[-1] = "last_tweet_time = " + str(time_now)
                    with open(config_file, 'w', encoding="utf-8") as settings_file:
                        settings_file.writelines(lines)

                    tweet_success = True
                    break  # Sortir de la boucle des tentatives

                except Exception as error:
                    log_string = f'ERREUR tweet (tentative {attempt + 1}/2): {error}'
                    print(Fore.RED + f"####---> {log_string}" + Style.RESET_ALL)
                    add_to_log(log_string)

                    if attempt < 1:  # Si ce n'était pas la dernière tentative
                        retry_after = 30
                        print(Fore.YELLOW + f"####---> Nouvelle tentative dans {retry_after} secondes..." + Style.RESET_ALL)
                        time.sleep(retry_after)
                        # Générer un NOUVEAU quote pour la tentative suivante
                        quote, imgs, selected_country = tracery_magic()
                    else:
                        print(Fore.RED + "####---> Échec après 2 tentatives, passage au suivant..." + Style.RESET_ALL)

            if tweet_success:
                time.sleep(time_between_tweets)
            else:
                # Attendre un peu avant de réessayer avec un nouveau pays
                time.sleep(300)  # 5 minutes
        else:
            diff = time_between_tweets - time_diff
            print(Fore.GREEN + f'####---> Sleeping for {diff} seconds...' +
                  Style.RESET_ALL)
            time.sleep(diff)

if __name__ == "__main__":
    main()
