import pandas as pd
import numpy as np

def fix_encoding(text):
    """Corrige les caractères mal encodés dans tout le DataFrame"""
    if isinstance(text, str):
        return text.encode('latin1').decode('utf-8')
    return text

def load_departements(file_path):
    """Charge la liste des départements depuis le fichier texte"""
    dept_dict = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if ' : ' in line:
                code, name = line.strip().split(' : ')
                dept_dict[code] = name
    return dept_dict

def get_correct_departement(commune_code, dept_dict):
    """Trouve le département correspondant au code de la commune"""
    if pd.isna(commune_code) or commune_code == '':
        return 'Inconnu'

    # Convertir en string et nettoyer
    code_str = str(commune_code).strip().zfill(3)  # zfill pour garantir 3 chiffres

    try:
        # Cas de la Corse (2A et 2B)
        #if code_str.startswith('2A') or code_str.startswith('2B'):
        #    return dept_dict.get(code_str[:2], 'Corse')

        # Cas des DOM-TOM (commençant par 97 ou 98)
        if code_str.startswith('97') or code_str.startswith('98'):
            return dept_dict.get(code_str[:3], 'Outre-mer')

        # Cas standard (métropole) - prendre 2 chiffres
        return dept_dict.get(code_str[:2], 'Inconnu')

    except:
        return 'Inconnu'

# 1. Charger la liste des départements
dept_dict = load_departements('listedesdepartements.txt')

# 2. Lire le fichier CSV original
df = pd.read_csv('elus-maires-mai.csv', sep=';', encoding='latin1')

# 3. Corriger les en-têtes de colonnes
df.columns = [fix_encoding(col) for col in df.columns]

# 4. Corriger tous les accents dans toutes les colonnes texte
for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].apply(fix_encoding)

# 5. Vérifier et corriger les libellés de département
# Convertir la colonne en string et remplacer les NaN
df['Code de la commune'] = df['Code de la commune'].astype(str).replace('nan', '')

df['Département vérifié'] = df['Code de la commune'].apply(
    lambda x: get_correct_departement(x, dept_dict)
)

# Comparaison avec le département existant
mask = df['Libellé du département'] != df['Département vérifié']
if mask.any():
    print(f"Correction de {mask.sum()} libellés de département incorrects")
    df['Libellé du département'] = df['Département vérifié']

# 6. Traitement des collectivités à statut particulier (si la colonne existe)
col_statut = 'Libellé de la collectivité à statut particulier'
if col_statut in df.columns:
    df['Libellé du département'] = df[col_statut].fillna(df['Libellé du département'])
    df = df.drop(columns=[col_statut])

# 7. Sauvegarder le fichier corrigé
df.to_csv('elus-maires-mai-corrige.csv', sep=';', index=False, encoding='utf-8-sig')

print("Fichier corrigé créé : 'elus-maires-mai-corrige.csv'")
print("Tous les accents et libellés de département ont été corrigés.")