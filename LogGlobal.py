# central_log.py - À appeler à la fin de chaque bot
import json
import os
from datetime import datetime

LOG_FILE = "central_log.json"

def add_log(bot_name, status, message="", details=""):
    """Ajoute une entrée dans le log central"""
    
    # Charger les logs existants
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    
    # Ajouter la nouvelle entrée
    logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "bot": bot_name,
        "status": status,  # "success", "error", "skipped"
        "message": message[:200],
        "details": details[:500] if details else ""
    })
    
    # Garder seulement les 500 dernières entrées (pour éviter un fichier trop gros)
    if len(logs) > 500:
        logs = logs[-500:]
    
    # Sauvegarder
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)
    
    print(f"📝 Log central mis à jour: {bot_name} - {status}")
