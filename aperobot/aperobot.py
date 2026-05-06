import tweepy
import os
from datetime import datetime
import pytz

# On garde votre configuration de fuseau horaire
paris_tz = pytz.timezone("Europe/Paris")

def main():
    # 1. RESTAURATION DES IDENTIFIANTS ORIGINAUX (SECRETS)
    consumer_key = os.environ.get("API_KEY")
    consumer_secret = os.environ.get("API_SECRET_KEY")
    access_token = os.environ.get("ACCESS_TOKEN")
    access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # 2. RÉCUPÉRATION DE L'HEURE PRÉCISE (Logique Fuseaux)
    now = datetime.now(paris_tz)
    heure_exacte = now.strftime("%Hh%M") # ex: 22h04
    heure_ronde = now.hour # Pour la sélection du texte

    # 3. RESTAURATION DES TEXTES SELON L'HEURE (Adaptés avec l'heure précise)
    if heure_ronde == 8:
        tweet = f"{heure_exacte}, c'est l'heure du café !"
    elif heure_ronde == 12:
        tweet = f"{heure_exacte}, c'est l'heure du miam !"
    elif heure_ronde == 18:
        tweet = f"{heure_exacte}, c'est l'heure de l'apéro !"
    elif heure_ronde == 19:
        tweet = f"{heure_exacte}, c'est encore l'heure de l'apéro !"
    else:
        # Votre demande spécifique : "22h04, ce n'est plus l'heure"
        tweet = f"{heure_exacte}, ce n'est plus l'heure"

    # 4. ENVOI DU TWEET
    try:
        api.update_status(tweet)
        print(f"Tweet envoyé : {tweet}")
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    main()
    
