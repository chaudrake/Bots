import os
import json
import random
import tweepy
import sys
from colorama import Fore, Style

# On se place dans le répertoire du bot
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def init_twitter_client():
    # [span_2](start_span)Utilisation des secrets GitHub passés en variables d'environnement[span_2](end_span)
    consumer_key = os.getenv('RIP_CONSUMER_KEY')
    consumer_secret = os.getenv('RIP_CONSUMER_SECRET')
    access_token = os.getenv('RIP_ACCESS_TOKEN')
    access_token_secret = os.getenv('RIP_ACCESS_TOKEN_SECRET')

    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        print(Fore.RED + "####---> Erreur : Clés API manquantes dans l'environnement" + Style.RESET_ALL)
        sys.exit(1)

    api_v2 = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    return api_v2

def load_names():
    # [span_3](start_span)Chargement de noms.txt[span_3](end_span)
    with open("noms.txt", 'r', encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def load_used_names():
    if os.path.exists('used_names.json'):
        with open('used_names.json', 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

def save_used_names(used_names):
    with open('used_names.json', 'w', encoding='utf-8') as f:
        json.dump(list(used_names), f, ensure_ascii=False, indent=4)

def pick_name():
    all_names = load_names()
    used_names = load_used_names()

    available_names = [n for n in all_names if n not in used_names]
    
    # Réinitialisation si tout est utilisé
    if not available_names:
        print(Fore.YELLOW + "####---> Réinitialisation de la liste." + Style.RESET_ALL)
        used_names.clear()
        available_names = all_names

    chosen_name = random.choice(available_names)
    used_names.add(chosen_name)
    save_used_names(used_names)
    return chosen_name

def main():
    print(Fore.GREEN + "####---> RipBot (GitHub Edition)" + Style.RESET_ALL)
    
    api_v2 = init_twitter_client()
    name = pick_name()
    
    tweet_text = f"#RIP 💀 {name} 💀"
    
    try:
        api_v2.create_tweet(text=tweet_text)
        print(Fore.GREEN + f"####---> Tweeté : {tweet_text}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"####---> Erreur : {e}" + Style.RESET_ALL)
        sys.exit(1)

if __name__ == "__main__":
    main()

