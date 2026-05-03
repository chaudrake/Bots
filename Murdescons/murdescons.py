import tweepy
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

# Détermine aléatoirement si le script doit s'exécuter (8% de chance)
# Ajusté pour correspondre à la fréquence voulue
if random.random() < 0.92:  # 92% de chance de NE PAS s'exécuter = 8% de chance de s'exécuter
    print("📅 Le script ne s'exécute pas cette fois (92% de chance)")
    sys.exit(0)
else:
    print("📅 Le script s'exécute (8% de chance)")

# Récupérer le contenu du tweet
def get_post_content(name):
    return "Bienvenue " + name.strip() + " sur le #MurDesCons."

# Obtenir la liste complète des noms
def get_full_list():
    with open("liste.txt", "r", encoding="utf-8") as file:
        content = file.read()
        return [name.strip() for name in content.split('\n') if name.strip()]

# Obtenir la liste des noms déjà tweetés
def get_tweeted_list():
    if os.path.exists('tweeted.txt'):
        with open('tweeted.txt', 'r', encoding="utf-8") as file:
            return [name.strip() for name in file.readlines() if name.strip()]
    return []

# Poster les tweets
def post_tweets(api):
    try:
        # Obtenir toutes les entrées et celles déjà tweetées
        all_names = get_full_list()
        tweeted_names = get_tweeted_list()

        print(f"📋 Total des noms: {len(all_names)}")
        print(f"✅ Noms déjà tweetés: {len(tweeted_names)}")

        # Trouver les noms non encore tweetés
        remaining_names = [name for name in all_names if name not in tweeted_names]

        # Si tous les noms ont été tweetés, réinitialiser
        if not remaining_names:
            print("🔄 Tous les noms ont été tweetés, réinitialisation...")
            with open('tweeted.txt', 'w', encoding="utf-8") as file:
                file.write('')  # Vide le fichier
            remaining_names = all_names.copy()

        # Choisir un nom aléatoire parmi les restants
        chosen_name = choice(remaining_names)
        print(f"🎲 Nom choisi: {chosen_name}")

        # Récupérer le contenu du tweet
        content = get_post_content(chosen_name)
        print(f"📝 Contenu: {content}")

        # Publier le tweet (tronqué à 280 caractères)
        tweet_text = content[:280]
        tweet = api.create_tweet(text=tweet_text)
        print(f"✅ Tweet publié: {tweet}")

        if tweet:
            # Ajouter le nom tweeté au fichier
            with open('tweeted.txt', 'a', encoding="utf-8") as file:
                file.write(chosen_name + '\n')
            print(f"💾 Nom ajouté à tweeted.txt: {chosen_name}")
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
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

print("🏁 Opération terminée")
