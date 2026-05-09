#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import sys
import codecs

# Configuration des chemins
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIRES_DIR = SCRIPT_DIR

input_file = os.path.join(MAIRES_DIR, 'elus-maires-mai.csv')
output_file = os.path.join(MAIRES_DIR, 'elus-maires-mai-corrige.csv')
DEPT_FILE = os.path.join(MAIRES_DIR, 'listedesdepartements.txt')

def repair_utf8(text):
    """
    Répare les chaînes UTF-8 corrompues.
    Transforme 'ClÃ©menciat' → 'Clémenciat'
    Transforme 'IngÃ©nieur' → 'Ingénieur'
    """
    if not isinstance(text, str):
        return text
    
    # Méthode : tenter de ré-interpréter la chaîne comme du latin1 puis re-encoder en UTF-8
    try:
        # Convertir la chaîne en bytes comme si c'était du latin1
        as_latin1 = text.encode('latin1')
        # Re-décoder en UTF-8
        result = as_latin1.decode('utf-8')
        return result
    except (UnicodeEncodeError, UnicodeDecodeError):
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

    # Lecture du CSV avec correction UTF-8
    print("📂 Lecture et correction du fichier...")
    
    # Lire le fichier en mode binaire
    with open(input_file, 'rb') as f:
        raw_content = f.read()
    
    # Décoder en ignorant les erreurs
    raw_text = raw_content.decode('utf-8', errors='replace')
    
    # Écrire temporairement
    temp_file = input_file + '.temp'
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(raw_text)
    
    # Lire avec pandas
    df = pd.read_csv(temp_file, sep=';', encoding='utf-8', dtype=str)
    os.remove(temp_file)
    
    print(f"📊 {len(df)} lignes chargées")

    # CORRECTION CRITIQUE : appliquer repair_utf8 à TOUTES les cellules
    print("🔄 Correction des caractères mal encodés (ClÃ©menciat → Clémenciat)...")
    for col in df.columns:
        df[col] = df[col].astype(str).apply(repair_utf8)

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

    # Aperçu des corrections
    print("\n📊 Vérification des corrections :")
    
    # Tester sur les premières lignes (sans backslash dans f-string)
    commune_col = 'Libellé de la commune'
    prenom_col = "Prénom de l'élu"
    nom_col = "Nom de l'élu"
    
    if commune_col in df.columns:
        print(f"   Exemple commune: {df[commune_col].iloc[0][:30]}")
    if prenom_col in df.columns:
        print(f"   Exemple prénom: {df[prenom_col].iloc[0]}")
    if nom_col in df.columns:
        print(f"   Exemple nom: {df[nom_col].iloc[0]}")

    print("\n✅ Terminé !")

if __name__ == "__main__":
    main()
