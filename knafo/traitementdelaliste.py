# supprime les doublons de liste.txt et les classe
# règle le problème des accents.
import os
import locale

# Définir la locale pour le tri français
try:
    locale.setlocale(locale.LC_COLLATE, 'fr_FR.UTF-8')
except locale.Error:
    print("Attention: locale française non disponible, utilisation du tri standard")

# Chemin vers le fichier
WORKING_DIR = '/home/pyth1on/knafobot'
INPUT_FILE = os.path.join(WORKING_DIR, 'liste.txt')
OUTPUT_FILE = os.path.join(WORKING_DIR, 'liste.txt')  # Même fichier en sortie

def clean_and_sort_adjectives(input_path, output_path):
    # Lire le fichier d'origine
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Nettoyer et normaliser
    adjectives = [line.strip().lower() for line in lines if line.strip()]

    # Supprimer les doublons
    unique_adjectives = list(set(adjectives))

    # Trier avec la locale française si disponible
    try:
        unique_adjectives.sort(key=locale.strxfrm)
    except (locale.Error, AttributeError):
        # Fallback si la locale n'est pas disponible
        unique_adjectives.sort()

    # Écrire le résultat dans le fichier de sortie
    with open(output_path, 'w', encoding='utf-8') as f:
        for adj in unique_adjectives:
            f.write(f"{adj}\n")

    return len(unique_adjectives)

if __name__ == "__main__":
    try:
        original_count = sum(1 for _ in open(INPUT_FILE, 'r', encoding='utf-8'))
        final_count = clean_and_sort_adjectives(INPUT_FILE, OUTPUT_FILE)

        print(f"Traitement terminé avec succès !")
        print(f"Adjectifs avant nettoyage : {original_count}")
        print(f"Adjectifs après nettoyage : {final_count}")
        print(f"Doublons supprimés : {original_count - final_count}")

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")