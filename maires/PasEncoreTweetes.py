# Liste les maires qui n'ont pas encore été tweetés
import csv

# Lire les maires tweetés
tweeted = set()
try:
    with open('tweeted_maires.txt', 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) >= 2:
                tweeted.add(parts[1])  # Stocker seulement le code circonscription
except FileNotFoundError:
    print("Fichier tweeted_maires.txt non trouvé")
    tweeted = set()

# Lire tous les maires du CSV et trouver les absents
not_tweeted = []
try:
    with open('elus-maires-mai-corrige.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')

        for row in reader:
            circ_code = row['Code de la commune']
            if circ_code not in tweeted:
                # Utiliser les mêmes noms que dans les en-têtes
                prenom = row['Prénom de l\'élu']  # Notez l'apostrophe échappée
                nom = row['Nom de l\'élu']
                not_tweeted.append(f"{circ_code} - {prenom} {nom}")

except FileNotFoundError:
    print("Fichier elus-maires-mai-corrige.csv non trouvé")
except Exception as e:
    print(f"Erreur lors de la lecture du CSV: {e}")

# Afficher le résultat
print(f"Maires non tweetés ({len(not_tweeted)}) :")
for dep in not_tweeted:
    print(dep)

# Afficher le rappel du nombre total à la fin
print(f"\nAu final : {len(not_tweeted)} maires restants à tweeter")