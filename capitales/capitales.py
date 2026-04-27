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


def tracery_magic():
    # Cherche bot.json dans le dossier capitales/
    bot_json_path = os.path.join(os.path.dirname(__file__), "bot.json")
    
    if not os.path.exists(bot_json_path):
        print(Back.RED + Fore.BLACK + f"####---> Fichier bot.json manquant à {bot_json_path}!" + Style.RESET_ALL)
        sys.exit()

    with open(bot_json_path, 'r', encoding="utf-8") as f:
        bot_data = json.load(f)

    grammar = tracery.Grammar(bot_data)
    grammar.add_modifiers(base_english)
    quote = grammar.flatten("#origin#")

    raw_img_links = re.findall(r'\{img\s[^}]*\}', quote)
    parsed_quote = re.sub(r'\{img\s[^}]*\}', '', quote)
    imgs = re.findall(r'\bhttps?://[^}\s]+', ' '.join(raw_img_links))

    return parsed_quote, imgs


def main():
    api_v1, api_v2 = init_twitter_client()
    quote, imgs = tracery_magic()
    post_to_twitter(api_v2, quote)
    print(Fore.GREEN + "####---> Bot terminé!" + Style.RESET_ALL)


if __name__ == "__main__":
    main()
