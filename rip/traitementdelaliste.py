# supprime les doublons de liste.txt et les classe par ordre alphabétique
import os

# Chemin vers le fichier
WORKING_DIR = '/home/pyth1on/rip'
INPUT_FILE = os.path.join(WORKING_DIR, 'noms.txt')
OUTPUT_FILE = os.path.join(WORKING_DIR, 'noms.txt')  # Même fichier en sortie

def clean_and_sort_adjectives(input_path, output_path):
    # Lire le fichier d'origine
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Nettoyer (supprimer les espaces mais conserver la casse)
    adjectives = [line.strip() for line in lines if line.strip()]

    # Créer un dictionnaire pour suivre les versions originales
    # La clé est en minuscule, la valeur est la version originale
    unique_dict = {}
    for adj in adjectives:
        key = adj.lower()
        # Garder la première occurrence avec la casse originale
        if key not in unique_dict:
            unique_dict[key] = adj

    # Extraire les valeurs originales et les trier (insensible à la casse)
    unique_adjectives = sorted(unique_dict.values(), key=lambda x: x.lower())

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
        print(f"Noms avant nettoyage : {original_count}")
        print(f"Noms après nettoyage : {final_count}")
        print(f"Doublons supprimés : {original_count - final_count}")

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")