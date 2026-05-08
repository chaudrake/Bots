import pandas as pd
import numpy as np

# ========================
# CONFIGURATION DES FICHIERS
# ========================
FICHIER_ENTREE = 'elus-deputes-dep.csv'
FICHIER_SORTIE = 'elus-deputes-depCorrige.csv'
# ========================

def fix_encoding(text):
    """Corrige les caractères mal encodés dans tout le DataFrame"""
    if isinstance(text, str):
        return text.encode('latin1').decode('utf-8')
    return text

def fix_circonscription(text):
    """Corrige spécifiquement les formes 'Ère/Ème' et la casse"""
    if isinstance(text, str):
        text = text.replace("Ère", "ère").replace("Ème", "ème")
        # Met en minuscule après le numéro
        parts = text.split()
        if len(parts) >= 2:
            parts[1] = parts[1].lower()  # "Circonscription" en minuscule
            text = " ".join(parts)
    return text

# 1. Lire le fichier
df = pd.read_csv(FICHIER_ENTREE, sep=';', encoding='latin1')

# 2. Corriger les en-têtes
df.columns = [fix_encoding(col) for col in df.columns]

# 3. Corriger les accents dans les données
for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].apply(fix_encoding)

# 4. Correction spécifique des circonscriptions
if 'Libellé de la circonscription législative' in df.columns:
    df['Libellé de la circonscription législative'] = df['Libellé de la circonscription législative'].apply(fix_circonscription)

# 5. Vérification
print("Exemple de corrections :")
print(df['Libellé de la circonscription législative'].head(3))

# 6. Nettoyage des colonnes départementales
col_statut = 'Libellé de la collectivité à statut particulier'
if col_statut in df.columns:
    df['Libellé du département'] = df[col_statut].fillna(df['Libellé du département'])
    df = df.drop(columns=[col_statut])

# 7. Renommage des colonnes
df = df.rename(columns={
    "Prénom de l'élu": "Prenom",
    "Nom de l'élu": "Nom"
})

# 8. Sauvegarde
df.to_csv(FICHIER_SORTIE, sep=';', index=False, encoding='utf-8-sig')

print("\nRésumé des corrections :")
print("- Encodage UTF-8 corrigé")
print("- Libellés des circonscriptions normalisés (ex: '1Ère' → '1ère circonscription')")
print("- Colonnes renommées pour plus de simplicité")
print(f"\nFichier sauvegardé sous : {FICHIER_SORTIE}")