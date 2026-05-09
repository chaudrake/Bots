#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import sys

# Configuration des chemins (adaptation GitHub)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIRES_DIR = SCRIPT_DIR  # Le script est déjà dans le dossier maires

# Gestion des arguments en ligne de commande
if len(sys.argv) > 1:
    input_file = sys.argv[1]
else:
    input_file = os.path.join(MAIRES_DIR, 'elus-maires-mai.csv')

if len(sys.argv) > 2:
    output_file = sys.argv[2]
else:
    output_file = os.path.join(MAIRES_DIR, 'elus-maires-mai-corrige.csv')

# Fichier des départements
DEPT_FILE = os.path.join(MAIRES_DIR, 'listedesdepartements.txt')

print(f"📂 Dossier de travail : {MAIRES_DIR}")
print(f"📂 Fichier source : {input_file}")
print(f"📂 Fichier de sortie : {output_file}")

def fix_encoding(text):
    """Corrige les caractères mal encodés dans tout le DataFrame"""
    if isinstance(text, str):
        try:
            # Tentative de correction double encodage (problème GitHub Actions)
            wrong_codes = {
                'Ã': 'È', 'Ã©': 'é', 'Ã¨': 'è', 'Ãª': 'ê', 'Ã«': 'ë',
                'Ã¹': 'ù', 'Ã»': 'û', 'Ã¢': 'â', 'Ã¤': 'ä', 'Ã´': 'ô',
                'Ã¶': 'ö', 'Ã®': 'î', 'Ã¯': 'ï', 'Ã§': 'ç', 'ÃŸ': 'ß',
                'Ã€': 'À', 'Ã‚': 'Â', 'Ã‰': 'É'
            }
            for wrong, correct in wrong_codes.items():
                text = text.replace(wrong, correct)
            return text.encode('latin1').decode('utf-8')
        except (UnicodeError, LookupError):
            return text
    return text

def load_departements(file_path):
    """Charge la liste des départements depuis le fichier texte"""
    dept_dict = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if ' : ' in line:
                    code, name = line.strip().split(' : ')
                    dept_dict[code] = name
        print(f"✅ {len(dept_dict)} départements chargés")
    except FileNotFoundError:
        print(f"⚠️ Fichier des départements introuvable : {file_path}")
    return dept_dict

def get_correct_departement(commune_code, dept_dict):
    """Trouve le département correspondant au code de la commune"""
    if pd.isna(commune_code) or commune_code == '':
        return 'Inconnu'

    # Convertir en string et nettoyer
    code_str = str(commune_code).strip().zfill(3)

    try:
        # Cas des DOM-TOM (commençant par 97 ou 98)
        if code_str.startswith('97') or code_str.startswith('98'):
            return dept_dict.get(code_str[:3], 'Outre-mer')

        # Cas standard (métropole) - prendre 2 chiffres
        return dept_dict.get(code_str[:2], 'Inconnu')

    except:
        return 'Inconnu'

def main():
    print("🔧 Correction d'encodage des fichiers maires")
    print("=" * 50)

    # Vérification des fichiers nécessaires
    if not os.path.exists(input_file):
        print(f"❌ Erreur : Fichier source introuvable - {input_file}")
        print(f"   Fichiers présents dans {MAIRES_DIR} :")
        for f in os.listdir(MAIRES_DIR):
            print(f"     - {f}")
        sys.exit(1)

    if not os.path.exists(DEPT_FILE):
        print(f"⚠️ Fichier des départements introuvable : {DEPT_FILE}")

    # 1. Charger la liste des départements
    print("📂 Chargement de la liste des départements...")
    dept_dict = load_departements(DEPT_FILE)

    # 2. Lire le fichier CSV original
    print(f"📂 Lecture : {input_file}")
    try:
        df = pd.read_csv(input_file, sep=';', encoding='latin1')
    except Exception as e:
        print(f"⚠️ Lecture latin1 échouée, tentative utf-8 : {e}")
        df = pd.read_csv(input_file, sep=';', encoding='utf-8')

    # 3. Corriger les en-têtes de colonnes
    df.columns = [fix_encoding(col) for col in df.columns]

    # 4. Corriger tous les accents
    print("🔄 Correction des accents...")
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(fix_encoding)

    # 5. Vérifier et corriger les libellés de département
    if 'Code de la commune' in df.columns:
        df['Code de la commune'] = df['Code de la commune'].astype(str).replace('nan', '')

        df['Département vérifié'] = df['Code de la commune'].apply(
            lambda x: get_correct_departement(x, dept_dict)
        )

        if 'Libellé du département' in df.columns:
            mask = df['Libellé du département'] != df['Département vérifié']
            if mask.any():
                print(f"📝 Correction de {mask.sum()} libellés de département incorrects")
                df['Libellé du département'] = df['Département vérifié']
        else:
            df['Libellé du département'] = df['Département vérifié']

    # 6. Traitement des collectivités à statut particulier
    col_statut = 'Libellé de la collectivité à statut particulier'
    if col_statut in df.columns:
        df['Libellé du département'] = df[col_statut].fillna(df['Libellé du département'])
        df = df.drop(columns=[col_statut])
        print("✅ Nettoyage des collectivités effectué")

    # 7. Sauvegarde
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    df.to_csv(output_file, sep=';', index=False, encoding='utf-8-sig')
    print(f"💾 Sauvegarde : {output_file}")

    print("\n✅ Résumé des corrections :")
    print("   - Correction des caractères mal encodés")
    print("   - Vérification/correction des départements")
    print(f"\n📌 Fichier prêt : {output_file}")

if __name__ == "__main__":
    main()
