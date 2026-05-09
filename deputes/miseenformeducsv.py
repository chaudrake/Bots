#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de correction d'encodage pour les fichiers CSV des députés français.

Problème résolu :
    Les fichiers exportés depuis certains systèmes (anciens SIGIC, etc.)
    utilisent l'encodage 'latin1' au lieu d'UTF-8, causant des problèmes d'affichage
    des accents et caractères spéciaux.

Corrections effectuées :
    - Conversion des colonnes et données de latin1 → UTF-8
    - Normalisation des libellés de circonscription (ex: "1Ère" → "1ère")
    - Nettoyage des colonnes des collectivités
    - Renommage simplifié des colonnes

Utilisation :
    python miseenformeducsv.py
    python miseenformeducsv.py mon_fichier.csv
    python miseenformeducsv.py mon_fichier.csv mon_fichier_corrige.csv
"""

import pandas as pd
import sys
import os

# Configuration par défaut
DEFAULT_ENTREE = 'elus-deputes-dep.csv'
DEFAULT_SORTIE = 'elus-deputes-depCorrige.csv'


def fix_encoding(text):
    """Corrige les caractères mal encodés (latin1 → UTF-8)"""
    if isinstance(text, str):
        try:
            return text.encode('latin1').decode('utf-8')
        except (UnicodeError, LookupError):
            return text
    return text


def fix_circonscription(text):
    """
    Corrige spécifiquement les formes 'Ère/Ème' et la casse.
    Exemples : "1Ère" → "1ère", "2Ème" → "2ème"
    """
    if isinstance(text, str):
        text = text.replace("Ère", "ère").replace("Ème", "ème")
        # Met la deuxième partie en minuscule
        parts = text.split()
        if len(parts) >= 2:
            parts[1] = parts[1].lower()
            text = " ".join(parts)
    return text


def main():
    """Point d'entrée principal"""
    # Gestion des arguments en ligne de commande
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

    # Vérification que le fichier source existe
    if not os.path.exists(fichier_entree):
        print(f"❌ Erreur : Fichier introuvable - {fichier_entree}")
        print(f"   Placez votre fichier CSV dans le dossier courant ou spécifiez son chemin.")
        sys.exit(1)

    try:
        # 1. Lire le fichier
        print(f"📂 Lecture : {fichier_entree}")
        df = pd.read_csv(fichier_entree, sep=';', encoding='latin1')

        # 2. Corriger les en-têtes
        df.columns = [fix_encoding(col) for col in df.columns]

        # 3. Corriger les accents dans les données
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].apply(fix_encoding)

        # 4. Correction spécifique des circonscriptions
        if 'Libellé de la circonscription législative' in df.columns:
            df['Libellé de la circonscription législative'] = df['Libellé de la circonscription législative'].apply(fix_circonscription)
            print("✅ Normalisation des circonscriptions effectuée")

        # 5. Nettoyage des colonnes départementales
        col_statut = 'Libellé de la collectivité à statut particulier'
        if col_statut in df.columns:
            df['Libellé du département'] = df[col_statut].fillna(df['Libellé du département'])
            df = df.drop(columns=[col_statut])
            print("✅ Nettoyage des collectivités effectué")

        # 6. Renommage des colonnes
        df = df.rename(columns={
            "Prénom de l'élu": "Prenom",
            "Nom de l'élu": "Nom"
        })

        # 7. Sauvegarde
        df.to_csv(fichier_sortie, sep=';', index=False, encoding='utf-8-sig')
        print(f"💾 Sauvegarde : {fichier_sortie}")

        # 8. Résumé
        print("\n✅ Résumé des corrections :")
        print("   - Encodage latin1 → UTF-8")
        print("   - Normalisation des circonscriptions (ex: '1Ère' → '1ère')")
        print("   - Nettoyage des colonnes collectivités")
        print("   - Renommage : 'Prénom de l'élu' → 'Prenom', 'Nom de l'élu' → 'Nom'")
        print(f"\n📌 Fichier prêt : {fichier_sortie}")

    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
