# Liste les deputés qui n'ont pas encore été tweetés
import csv

# Lire les députés tweetés
tweeted = set()
with open('tweeted_deputes.txt', 'r', encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split('|')
        if len(parts) >= 2:
            tweeted.add(parts[1])  # Stocker seulement le code circonscription

# Lire tous les députés du CSV et trouver les absents
not_tweeted = []
with open('elus-deputes-depCorrige.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        circ_code = row['Code de la circonscription législative']
        if circ_code not in tweeted:
            not_tweeted.append(f"{circ_code} - {row['Prenom']} {row['Nom']}")

# Afficher le résultat
print(f"Députés non tweetés ({len(not_tweeted)}) :")
for dep in not_tweeted:
    print(dep)