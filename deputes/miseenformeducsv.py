#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import sys
import os

DEFAULT_ENTREE = 'elus-deputes-dep.csv'
DEFAULT_SORTIE = 'elus-deputes-depCorrige.csv'

def fix_encoding_deep(text):
    """
    Corrige les caractères mal encodés.
    Gère le cas spécifique des doubles encodages (Ã -> È, etc.)
    """
    if not isinstance(text, str):
        return text
    
    replacements = {
        'Ã': 'È',
        'Ã©': 'é',
        'Ã¨': 'è',
        'Ãª': 'ê',
        'Ã«': 'ë',
        'Ã¹': 'ù',
        'Ã»': 'û',
        'Ã¢': 'â',
        'Ã¤': 'ä',
        'Ã´': 'ô',
        'Ã¶': 'ö',
        'Ã®': 'î',
        'Ã¯': 'ï',
        'Ã§': 'ç',
        'ÃŸ': 'ß',
        'Â°': '°',
        'Â±': '±',
        'Â²': '²',
        'Â³': '³',
    }
    
    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)
    
    try:
        text = text.encode('latin1').decode('utf-8')
    except (UnicodeError, LookupError):
        pass
    
    return text

def fix_circonscription(text):
    """Normalise les libellés de circonscription"""
    if isinstance(text, str):
        text = text.replace("Ère", "ère").replace("Ème", "ème")
        text = text.replace("1ere", "1ère").replace("2eme", "2ème")
        text = text.replace("3eme", "3ème").replace("4eme", "4ème")
        text = text.replace("5eme", "5ème").replace("6eme", "6ème")
        text = text.replace("7eme", "7ème").replace("8eme", "8ème")
        text = text.replace("9eme", "9ème")
        parts = text.split()
        if len(parts) >= 2:
            parts[1] = parts[1].lower()
            text = " ".join(parts)
    return text

def fix_dates(df):
    """Normalise les colonnes de dates au format JJ/MM/AAAA"""
    date_columns = ['Date de naissance', 'Date de début du mandat']
    
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format='%Y-%m-%d', errors='coerce')
            df[col] = df[col].dt.strftime('%d/%m/%Y')
            print(f"✅ Dates normalisees : {col} (JJ/MM/AAAA)")
    
    return df

def main():
    if len(sys.argv) > 1:
        fichier_entree = sys.argv[1]
    else:
        fichier_entree = DEFAULT_ENTREE

    if len(sys.argv) > 2:
        fichier_sortie = sys.argv[2]
    else:
        fichier_sortie = DEFAULT_SORTIE

    print("🔧 Correction d'encodage des fichiers députés")
    print("=" * 50)

    if not os.path.exists(fichier_entree):
        print(f"❌ Erreur : Fichier introuvable - {fichier_entree}")
        sys.exit(1)

    try:
        with open(fichier_entree, 'rb') as f:
            content = f.read()
            try:
                content_str = content.decode('utf-8')
            except UnicodeDecodeError:
                content_str = content.decode('latin1')
        
        temp_file = fichier_entree + '.temp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content_str)
        
        df = pd.read_csv(temp_file, sep=';', encoding='utf-8')
        os.remove(temp_file)
        
        print(f"📂 Lecture : {fichier_entree}")

        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].apply(fix_encoding_deep)

        if 'Libellé de la circonscription législative' in df.columns:
            df['Libellé de la circonscription législative'] = df['Libellé de la circonscription législative'].apply(fix_circonscription)
            print("✅ Normalisation des circonscriptions effectuée")

        df = fix_dates(df)

        col_statut = 'Libellé de la collectivité à statut particulier'
        if col_statut in df.columns:
            df['Libellé du département'] = df[col_statut].fillna(df['Libellé du département'])
            df = df.drop(columns=[col_statut])
            print("✅ Nettoyage des collectivités effectué")

        df = df.rename(columns={
            "Prénom de l'élu": "Prenom",
            "Nom de l'élu": "Nom"
        })

        df.to_csv(fichier_sortie, sep=';', index=False, encoding='utf-8-sig')
        print(f"💾 Sauvegarde : {fichier_sortie}")

        print("\n📊 Aperçu des 3 premières lignes corrigées :")
        for col in ['Libellé de la circonscription législative', 'Prenom', 'Nom', 'Date de naissance']:
            if col in df.columns:
                print(f"   {col}: {df[col].iloc[0]}")

        print("\n✅ Résumé des corrections :")
        print("   - Correction des caractères mal encodés")
        print("   - Normalisation des circonscriptions")
        print("   - Normalisation des dates (JJ/MM/AAAA)")
        print(f"\n📌 Fichier prêt : {fichier_sortie}")

    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
