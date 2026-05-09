#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import sys

# Configuration des chemins (adaptation GitHub)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INPUT = os.path.join(SCRIPT_DIR, 'elus-maires-mai.csv')
DEFAULT_OUTPUT = os.path.join(SCRIPT_DIR, 'elus-maires-mai-corrige.csv')
DEPT_FILE = os.path.join(SCRIPT_DIR, 'listedesdepartements.txt')

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
    except FileNotFoundError:
        print(f"⚠️ Fichier des départements introuvable : {file_path}")
        print("   Utilisation d'un dictionnaire vide")
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
    """Point d'entrée principal"""
    # Gestion des arguments en ligne de commande (optionnel)
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = DEFAULT_INPUT

    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = DEFAULT_OUTPUT

    print("🔧 Correction d'encodage des fichiers maires")
    print("=" * 50)

    # Vérification des fichiers nécessaires
    if not os.path.exists(input_file):
        print(f"❌ Erreur : Fichier source introuvable - {input_file}")
        sys.exit(1)

    if not os.path.exists(DEPT_FILE):
        print(f"⚠️ Fichier des départements introuvable : {DEPT_FILE}")

    # 1. Charger la liste des départements
    print("📂 Chargement de la liste des départements...")
    dept_dict = load_departements(DEPT_FILE)
    print(f"   {len(dept_dict)} départements chargés")

    # 2. Lire le fichier CSV original (gestion d'encodage robuste)
    print(f"📂 Lecture : {input_file}")
    try:
        # Tentative de lecture avec latin1
        df = pd.read_csv(input_file, sep=';', encoding='latin1')
    except Exception as e:
        print(f"⚠️ Lecture latin1 échouée, tentative utf-8 : {e}")
        df = pd.read_csv(input_file, sep=';', encoding='utf-8')

    # 3. Corriger les en-têtes de colonnes
    df.columns = [fix_encoding(col) for col in df.columns]

    # 4. Corriger tous les accents dans toutes les colonnes texte
    print("🔄 Correction des accents...")
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(fix_encoding)

    # 5. Vérifier et corriger les libellés de département
    if 'Code de la commune' in df.columns:
        # Convertir la colonne en string et remplacer les NaN
        df['Code de la commune'] = df['Code de la commune'].astype(str).replace('nan', '')

        df['Département vérifié'] = df['Code de la commune'].apply(
            lambda x: get_correct_departement(x, dept_dict)
        )

        # Comparaison avec le département existant
        if 'Libellé du département' in df.columns:
            mask = df['Libellé du département'] != df['Département vérifié']
            if mask.any():
                print(f"📝 Correction de {mask.sum()} libellés de département incorrects")
                df['Libellé du département'] = df['Département vérifié']
        else:
            df['Libellé du département'] = df['Département vérifié']

    # 6. Traitement des collectivités à statut particulier (si la colonne existe)
    col_statut = 'Libellé de la collectivité à statut particulier'
    if col_statut in df.columns:
        df['Libellé du département'] = df[col_statut].fillna(df['Libellé du département'])
        df = df.drop(columns=[col_statut])
        print("✅ Nettoyage des collectivités effectué")

    # 7. Sauvegarder le fichier corrigé
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    df.to_csv(output_file, sep=';', index=False, encoding='utf-8-sig')
    print(f"💾 Sauvegarde : {output_file}")

    # Aperçu des corrections
    print("\n📊 Aperçu (3 premières lignes) :")
    for col in ['Libellé du département']:
        if col in df.columns:
            print(f"   {col}: {df[col].iloc[0]}")

    print("\n✅ Résumé des corrections :")
    print("   - Correction des caractères mal encodés")
    print("   - Vérification/correction des départements via code commune")
    print("   - Nettoyage des colonnes collectivités")
    print(f"\n📌 Fichier prêt : {output_file}")

if __name__ == "__main__":
    main()
