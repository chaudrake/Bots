#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import sys

# Configuration des chemins
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIRES_DIR = SCRIPT_DIR

input_file = os.path.join(MAIRES_DIR, 'elus-maires-mai.csv')
output_file = os.path.join(MAIRES_DIR, 'elus-maires-mai-corrige.csv')
DEPT_FILE = os.path.join(MAIRES_DIR, 'listedesdepartements.txt')

def fix_encoding_deep(text):
    """
    Corrige les caractères mal encodés (version renforcée pour GitHub Actions)
    Gère les doubles encodages comme Ã© → é, Ã → È, etc.
    """
    if not isinstance(text, str):
        return text
    
    # Dictionnaire de correction des caractères corrompus
    replacements = {
        'Ã': 'È', 'Ã©': 'é', 'Ã¨': 'è', 'Ãª': 'ê', 'Ã«': 'ë',
        'Ã¹': 'ù', 'Ã»': 'û', 'Ã¢': 'â', 'Ã¤': 'ä', 'Ã´': 'ô',
        'Ã¶': 'ö', 'Ã®': 'î', 'Ã¯': 'ï', 'Ã§': 'ç', 'ÃŸ': 'ß',
        'Ã€': 'À', 'Ã‚': 'Â', 'Ã‰': 'É', 'Ã‡': 'Ç', 'Ã™': 'Ù',
        'Ã»': 'û', 'Ã›': 'Û', 'ÃŽ': 'Î', 'Ã”': 'Ô', 'Ã…': 'Å',
        'Ã†': 'Æ', 'Ã˜': 'Ø', 'Â°': '°', 'Â±': '±', 'Â²': '²', 'Â³': '³',
        'â‚¬': '€', 'â€š': '‚', 'Æ’': 'ƒ', 'â€ž': '„', 'â€¦': '…',
        'â€¡': '‡', 'Ë†': 'ˆ', 'â€¹': '‹', 'Å’': 'Œ', 'Å½': 'Ž',
        'â€˜': '‘', 'â€™': '’', 'â€œ': '“', 'â€': '”', 'â€¢': '•',
        'â€“': '–', 'â€”': '—', 'Ëœ': '˜', 'â„¢': '™', 'Å¡': 'š',
        'â€º': '›', 'Å“': 'œ', 'Å¾': 'ž', 'Å¸': 'Ÿ'
    }
    
    # Application des remplacements
    for wrong, correct in replacements.items():
        if wrong in text:
            text = text.replace(wrong, correct)
    
    # Tentative de correction par re-encodage
    try:
        text = text.encode('latin1').decode('utf-8')
    except (UnicodeError, LookupError):
        pass
    
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

    code_str = str(commune_code).strip().zfill(3)

    try:
        if code_str.startswith('97') or code_str.startswith('98'):
            return dept_dict.get(code_str[:3], 'Outre-mer')
        return dept_dict.get(code_str[:2], 'Inconnu')
    except:
        return 'Inconnu'

def main():
    print(f"📂 Dossier : {MAIRES_DIR}")
    print(f"📂 Source : {input_file}")
    print(f"📂 Sortie : {output_file}")
    print("🔧 Correction d'encodage des fichiers maires")
    print("=" * 50)

    if not os.path.exists(input_file):
        print(f"❌ Fichier source introuvable - {input_file}")
        sys.exit(1)

    # Chargement des départements
    dept_dict = load_departements(DEPT_FILE)

    # Lecture du CSV avec gestion d'encodage robuste
    print("📂 Lecture du fichier...")
    try:
        # D'abord en mode binaire pour détecter l'encodage
        with open(input_file, 'rb') as f:
            raw = f.read()
        
        # Essayons de décoder intelligemment
        try:
            content = raw.decode('utf-8')
        except UnicodeDecodeError:
            content = raw.decode('latin1')
        
        # Écrire temporairement
        temp_file = input_file + '.temp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        df = pd.read_csv(temp_file, sep=';', encoding='utf-8')
        os.remove(temp_file)
        
    except Exception as e:
        print(f"⚠️ Lecture directe : {e}")
        df = pd.read_csv(input_file, sep=';', encoding='latin1')

    # Correction des en-têtes
    df.columns = [fix_encoding_deep(col) for col in df.columns]

    # Correction des données textuelles
    print("🔄 Correction des accents...")
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(fix_encoding_deep)

    # Vérification et correction des départements
    if 'Code de la commune' in df.columns:
        df['Code de la commune'] = df['Code de la commune'].astype(str).replace('nan', '')

        df['Département vérifié'] = df['Code de la commune'].apply(
            lambda x: get_correct_departement(x, dept_dict)
        )

        if 'Libellé du département' in df.columns:
            mask = df['Libellé du département'] != df['Département vérifié']
            if mask.any():
                print(f"📝 Correction de {mask.sum()} libellés de département")
                df['Libellé du département'] = df['Département vérifié']
        else:
            df['Libellé du département'] = df['Département vérifié']

    # Nettoyage des collectivités
    col_statut = 'Libellé de la collectivité à statut particulier'
    if col_statut in df.columns:
        df['Libellé du département'] = df[col_statut].fillna(df['Libellé du département'])
        df = df.drop(columns=[col_statut])
        print("✅ Nettoyage des collectivités effectué")

    # Sauvegarde
    df.to_csv(output_file, sep=';', index=False, encoding='utf-8-sig')
    print(f"💾 Sauvegarde : {output_file}")

    # Aperçu
    print("\n📊 Aperçu des corrections :")
    test_cols = ['Libellé du département', 'Nom de l\'élu', 'Prénom de l\'élu']
    for col in test_cols:
        if col in df.columns:
            val = str(df[col].iloc[0])[:50]
            print(f"   {col}: {val}")

    print("\n✅ Terminé !")

if __name__ == "__main__":
    main()
