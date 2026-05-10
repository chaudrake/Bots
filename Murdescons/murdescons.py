import tweepy
import random
from random import choice
import os
import sys

# Récupérer les variables d'environnement (GitHub Secrets)
ACCESS_KEY = os.getenv('MURDESCONS_ACCESS_TOKEN')
ACCESS_SECRET = os.getenv('MURDESCONS_ACCESS_TOKEN_SECRET')
CONSUMER_KEY = os.getenv('MURDESCONS_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('MURDESCONS_CONSUMER_SECRET')

# Vérification des credentials
if not all([ACCESS_KEY, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET]):
    print("❌ Missing Twitter API credentials")
    sys.exit(1)

# Créer un client Tweepy
api = tweepy.Client(
    access_token=ACCESS_KEY,
    access_token_secret=ACCESS_SECRET,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET
)

print('🚀 Lancement du bot Mur Des Cons')

# 8% de chance de s'exécuter
if random.random() < 0.08:
    print("📅 Le script s'exécute (8% de chance)")
else:
    print("📅 Le script ne s'exécute pas cette fois (92% de chance)")
    sys.exit(0)

def get_post_content(name):
    return "Bienvenue " + name.strip() + " sur le #MurDesCons."

def get_full_list():
    """Lit liste.txt et retourne une liste unique sans doublons"""
    with open("liste.txt", "r", encoding="utf-8") as file:
        content = file.read()
        names = [name.strip() for name in content.split('\n') if name.strip()]
        # Supprime les doublons tout en préservant l'ordre
        seen = set()
        unique_names = []
        for name in names:
            if name not in seen:
                seen.add(name)
                unique_names.append(name)
        return unique_names

def get_tweeted_list():
    """Lit tweeted.txt et retourne une liste unique"""
    if os.path.exists('tweeted.txt'):
        with open('tweeted.txt', 'r', encoding="utf-8") as file:
            names = [name.strip() for name in file.readlines() if name.strip()]
            # Supprime les doublons éventuels
            seen = set()
            unique_names = []
            for name in names:
                if name not in seen:
                    seen.add(name)
                    unique_names.append(name)
            return unique_names
    return []

def post_tweets(api):
    try:
        # Obtenir toutes les entrées et celles déjà tweetées
        all_names = get_full_list()
        tweeted_names = get_tweeted_list()

        print(f"📋 Total des noms uniques: {len(all_names)}")
        print(f"✅ Noms déjà tweetés: {len(tweeted_names)}")

        # Trouver les noms non encore tweetés
        remaining_names = [name for name in all_names if name not in tweeted_names]

        # Si tous les noms ont été tweetés, réinitialiser
        if not remaining_names:
            print("🔄 Tous les noms ont été tweetés, réinitialisation...")
            with open('tweeted.txt', 'w', encoding="utf-8") as file:
                file.write('')
            remaining_names = all_names.copy()
            print(f"📋 Réinitialisation : {len(remaining_names)} noms disponibles")

        # Choisir un nom aléatoire parmi les restants
        chosen_name = choice(remaining_names)
        print(f"🎲 Nom choisi: {chosen_name}")

        # Récupérer le contenu du tweet
        content = get_post_content(chosen_name)
        print(f"📝 Contenu: {content}")

        # Publier le tweet (tronqué à 280 caractères)
        tweet_text = content[:280]
        tweet = api.create_tweet(text=tweet_text)
        print(f"✅ Tweet publié - ID: {tweet[0]['id']}")

        # Ajouter le nom tweeté au fichier
        with open('tweeted.txt', 'a', encoding="utf-8") as file:
            file.write(chosen_name + '\n')
        print(f"💾 Nom ajouté à tweeted.txt: {chosen_name}")
        
        # Afficher la progression
        new_tweeted_count = len(get_tweeted_list())
        remaining_count = len(all_names) - new_tweeted_count
        print(f"📊 Progression: {new_tweeted_count}/{len(all_names)} tweetés ({remaining_count} restants)")
        
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    try:
        if post_tweets(api):
            print('✅ Tweet posté avec succès')
        else:
            print('❌ Erreur lors de la publication du tweet')
            sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

print("🏁 Opération terminée")
