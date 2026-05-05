#!/usr/bin/env python3
# Script de statistiques pour le bot Repas
# Ca compte le nombre de plats tweetés et restants.

import json
import os
from datetime import datetime
import pytz

# Fichiers de configuration (mêmes que dans repas.py)
STATE_FILE = "meal_state.json"
MEALS_DATA_FILE = "meals_data.json"

def normalize_label(s: str) -> str:
    """Normalise une étiquette pour comparaison (identique à repas.py)"""
    import unicodedata
    if not isinstance(s, str):
        s = str(s)
    s = unicodedata.normalize("NFKC", s)
    s = " ".join(s.strip().split())
    return s.lower()

def load_data():
    """Charge les données et l'état"""
    try:
        with open(MEALS_DATA_FILE, 'r', encoding='utf-8') as f:
            meals_data = json.load(f)
        print("✅ Données repas chargées")
    except Exception as e:
        print(f"❌ Erreur chargement données: {e}")
        return None, None

    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            print("✅ État chargé")
        else:
            state = {
                "used_petit_dejeuner": [],
                "used_repas_principal": [],
                "used_entrees": []
            }
            print("ℹ️  Fichier d'état non trouvé, utilisation état vide")
    except Exception as e:
        print(f"❌ Erreur chargement état: {e}")
        state = {
            "used_petit_dejeuner": [],
            "used_repas_principal": [],
            "used_entrees": []
        }

    return meals_data, state

def calculate_statistics(meals_data, state):
    """Calcule les statistiques d'utilisation"""
    stats = {}

    # Petit-déjeuner
    if "petit_dejeuner" in meals_data:
        petit_dejeuner_all = meals_data["petit_dejeuner"]
        petit_dejeuner_used = state.get("used_petit_dejeuner", [])

        # Conversion en sets normalisés pour comparaison
        petit_dejeuner_all_norm = {normalize_label(x) for x in petit_dejeuner_all}
        petit_dejeuner_used_norm = {normalize_label(x) for x in petit_dejeuner_used}

        # Éléments réellement utilisés (présents dans la liste complète)
        petit_dejeuner_actual_used_norm = petit_dejeuner_used_norm.intersection(petit_dejeuner_all_norm)
        petit_dejeuner_remaining_norm = petit_dejeuner_all_norm - petit_dejeuner_actual_used_norm

        # Reconversion en noms originaux
        petit_dejeuner_actual_used = []
        for item in petit_dejeuner_all:
            if normalize_label(item) in petit_dejeuner_actual_used_norm:
                petit_dejeuner_actual_used.append(item)

        petit_dejeuner_remaining = []
        for item in petit_dejeuner_all:
            if normalize_label(item) in petit_dejeuner_remaining_norm:
                petit_dejeuner_remaining.append(item)

        stats["petit_dejeuner"] = {
            "total": len(petit_dejeuner_all),
            "utilises": len(petit_dejeuner_actual_used),
            "restants": len(petit_dejeuner_remaining),
            "liste_utilises": petit_dejeuner_actual_used,
            "liste_restants": petit_dejeuner_remaining
        }

    # Entrées
    if "entrees" in meals_data:
        entrees_all = meals_data["entrees"]
        entrees_used = state.get("used_entrees", [])

        entrees_all_norm = {normalize_label(x) for x in entrees_all}
        entrees_used_norm = {normalize_label(x) for x in entrees_used}

        entrees_actual_used_norm = entrees_used_norm.intersection(entrees_all_norm)
        entrees_remaining_norm = entrees_all_norm - entrees_actual_used_norm

        entrees_actual_used = []
        for item in entrees_all:
            if normalize_label(item) in entrees_actual_used_norm:
                entrees_actual_used.append(item)

        entrees_remaining = []
        for item in entrees_all:
            if normalize_label(item) in entrees_remaining_norm:
                entrees_remaining.append(item)

        stats["entrees"] = {
            "total": len(entrees_all),
            "utilises": len(entrees_actual_used),
            "restants": len(entrees_remaining),
            "liste_utilises": entrees_actual_used,
            "liste_restants": entrees_remaining
        }

    # Plats principaux
    if "repas_principal" in meals_data:
        plats_all = meals_data["repas_principal"]
        plats_used = state.get("used_repas_principal", [])

        plats_all_norm = {normalize_label(x) for x in plats_all}
        plats_used_norm = {normalize_label(x) for x in plats_used}

        plats_actual_used_norm = plats_used_norm.intersection(plats_all_norm)
        plats_remaining_norm = plats_all_norm - plats_actual_used_norm

        plats_actual_used = []
        for item in plats_all:
            if normalize_label(item) in plats_actual_used_norm:
                plats_actual_used.append(item)

        plats_remaining = []
        for item in plats_all:
            if normalize_label(item) in plats_remaining_norm:
                plats_remaining.append(item)

        stats["plats_principaux"] = {
            "total": len(plats_all),
            "utilises": len(plats_actual_used),
            "restants": len(plats_remaining),
            "liste_utilises": plats_actual_used,
            "liste_restants": plats_remaining
        }

    return stats

def display_statistics(stats):
    """Affiche les statistiques de manière lisible"""
    print("\n" + "="*60)
    print("📊 STATISTIQUES DU BOT REPAS")
    print("="*60)

    # Dernière mise à jour
    tz = pytz.timezone('Europe/Paris')
    now = datetime.now(tz).strftime("%d/%m/%Y à %H:%M:%S")
    print(f"\n🕐 Dernière analyse : {now}")

    # Petit-déjeuner
    if "petit_dejeuner" in stats:
        pd = stats["petit_dejeuner"]
        pourcentage = (pd["utilises"] / pd["total"] * 100) if pd["total"] > 0 else 0
        print(f"\n☀️  PETIT-DÉJEUNER")
        print(f"   • Total disponible : {pd['total']}")
        print(f"   • Déjà proposés : {pd['utilises']}")
        print(f"   • Restants : {pd['restants']}")
        print(f"   • Progression : {pourcentage:.1f}%")

    # Entrées
    if "entrees" in stats:
        ent = stats["entrees"]
        pourcentage = (ent["utilises"] / ent["total"] * 100) if ent["total"] > 0 else 0
        print(f"\n🥗 ENTREES")
        print(f"   • Total disponible : {ent['total']}")
        print(f"   • Déjà proposées : {ent['utilises']}")
        print(f"   • Restantes : {ent['restants']}")
        print(f"   • Progression : {pourcentage:.1f}%")

    # Plats principaux
    if "plats_principaux" in stats:
        plat = stats["plats_principaux"]
        pourcentage = (plat["utilises"] / plat["total"] * 100) if plat["total"] > 0 else 0
        print(f"\n🍽️  PLATS PRINCIPAUX")
        print(f"   • Total disponible : {plat['total']}")
        print(f"   • Déjà proposés : {plat['utilises']}")
        print(f"   • Restants : {plat['restants']}")
        print(f"   • Progression : {pourcentage:.1f}%")

    print("\n" + "="*60)

def display_detailed_lists(stats):
    """Affiche les listes détaillées sur demande"""
    print("\n" + "="*60)
    print("📋 LISTES DÉTAILLÉES")
    print("="*60)

    # Entrées utilisées
    if "entrees" in stats and stats["entrees"]["liste_utilises"]:
        print(f"\n📥 ENTREES DÉJÀ PROPOSÉES ({len(stats['entrees']['liste_utilises'])}):")
        for i, entree in enumerate(stats["entrees"]["liste_utilises"], 1):
            print(f"   {i:2d}. {entree}")

    # Plats utilisés
    if "plats_principaux" in stats and stats["plats_principaux"]["liste_utilises"]:
        print(f"\n📥 PLATS DÉJÀ PROPOSÉS ({len(stats['plats_principaux']['liste_utilises'])}):")
        for i, plat in enumerate(stats["plats_principaux"]["liste_utilises"], 1):
            print(f"   {i:2d}. {plat}")

    # Petit-déjeuners utilisés
    if "petit_dejeuner" in stats and stats["petit_dejeuner"]["liste_utilises"]:
        print(f"\n📥 PETIT-DÉJEUNERS DÉJÀ PROPOSÉS ({len(stats['petit_dejeuner']['liste_utilises'])}):")
        for i, pd in enumerate(stats["petit_dejeuner"]["liste_utilises"], 1):
            print(f"   {i:2d}. {pd}")

    print("\n" + "="*60)

def main():
    """Fonction principale"""
    print("🔍 Analyse des statistiques du bot Repas...")

    meals_data, state = load_data()
    if not meals_data:
        print("❌ Impossible de charger les données. Arrêt.")
        return

    stats = calculate_statistics(meals_data, state)
    display_statistics(stats)

    # Demander si l'utilisateur veut voir les listes détaillées
    try:
        response = input("\n📋 Voulez-vous voir les listes détaillées ? (o/N) : ").strip().lower()
        if response in ['o', 'oui', 'y', 'yes']:
            display_detailed_lists(stats)
    except:
        pass  # Ignorer les erreurs d'input

    print("\n✅ Analyse terminée!")

if __name__ == "__main__":
    main()