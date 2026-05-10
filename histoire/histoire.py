import tweepy
import os
import random
import sys
from pathlib import Path

# Définition du dossier de travail
WORKING_DIR = Path(__file__).parent.absolute()

# Chemins des fichiers
LISTE_FILE = os.path.join(WORKING_DIR, 'liste.txt')
INDEX_FILE = os.path.join(WORKING_DIR, 'index.txt')

def get_keys():
    """Récupère les clés depuis les variables d'environnement."""
    return (
        os.getenv('CONSUMER_KEY'),
        os.getenv('CONSUMER_SECRET'),
        os.getenv('ACCESS_KEY'),
        os.getenv('ACCESS_SECRET')
    )

def main():
    # 1. Vérification des clés
    consumer_key, consumer_secret, access_key, access_secret = get_keys()
    if not all([consumer_key, consumer_secret, access_key, access_secret]):
        print("Erreur : Clés API manquantes dans l'environnement.")
        sys.exit(1)

    # 2. Lecture de la liste complète
    try:
        with open(LISTE_FILE, 'r', encoding='utf-8') as f:
            lignes = [l.strip() for l in f.readlines() if l.strip()]
    except FileNotFoundError:
        print(f"Erreur : {LISTE_FILE} introuvable.")
        sys.exit(1)

    # 3. Lecture de l'index (dernière ligne traitée)
    if not os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write("0")
        current_index = 0
    else:
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            try:
                current_index = int(f.read().strip())
            except ValueError:
                current_index = 0

    # 4. Sélection de la prochaine ligne
    if current_index >= len(lignes):
        print("Fin de la liste atteinte. Réinitialisation à 0.")
        current_index = 0

    phrase_a_tweeter = lignes[current_index]

    # 5. Envoi du Tweet
    try:
        client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_key,
            access_token_secret=access_secret
        )
        client.create_tweet(text=phrase_a_tweeter)
        print(f"Tweet envoyé : {phrase_a_tweeter}")

        # 6. Mise à jour de l'index uniquement si le tweet a réussi
        new_index = current_index + 1
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write(str(new_index))
        print(f"Nouvel index sauvegardé : {new_index}")

    except Exception as e:
        print(f"Erreur lors de l'envoi du tweet : {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
  
