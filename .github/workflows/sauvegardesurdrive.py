# Script qui vérifie le jour et effectue la sauvegarde sur Google Drive
# Adapté pour GitHub Actions
import datetime
import os
import re
import sys
import json
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import zipfile
from pathlib import Path

# Configuration
CONFIG = {
    'bots_folder': 'Bots',  # Dossier à sauvegarder (relatif)
    'backups_to_keep': 5,   # Nombre de sauvegardes à conserver
    'backup_days': [2, 6]   # 2=mercredi, 6=dimanche (Monday=0)
}

def create_backup():
    """Crée une archive zip du dossier Bots"""
    bots_path = Path(CONFIG['bots_folder'])
    if not bots_path.exists():
        raise FileNotFoundError(f"Dossier {CONFIG['bots_folder']} introuvable")
    
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    backup_name = f"SauvegardeBots_{date_str}.zip"
    backup_path = Path(backup_name)
    
    print(f"📦 Création de la sauvegarde: {backup_name}")
    
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in bots_path.rglob('*'):
            # Exclure les fichiers inutiles
            if any(exclude in str(file) for exclude in ['.git', '__pycache__', '.pyc', '.log', 'temp-imgs']):
                continue
            zipf.write(file, file.relative_to(bots_path.parent))
    
    print(f"✅ Sauvegarde créée: {backup_name} ({backup_path.stat().st_size / 1024 / 1024:.2f} MB)")
    return backup_name, backup_path

def authentifier():
    """Authentification OAuth avec Google Drive (pour GitHub Actions)"""
    gauth = GoogleAuth(settings_file="settings.yaml")
    
    # Charger les credentials depuis les variables d'environnement
    credentials_json = os.getenv('GOOGLE_DRIVE_CREDENTIALS')
    if not credentials_json:
        raise Exception("❌ GOOGLE_DRIVE_CREDENTIALS non défini dans les secrets GitHub")
    
    # Sauvegarder credentials.json temporairement
    with open("credentials.json", "w") as f:
        f.write(credentials_json)
    
    gauth.LoadCredentialsFile("credentials.json")
    
    if gauth.credentials is None:
        raise Exception("❌ Credentials invalides ou expirés")
    elif gauth.access_token_expired:
        print("♻️ Access token expiré → rafraîchissement...")
        gauth.Refresh()
        if gauth.access_token_expired:
            raise Exception("❌ Échec du rafraîchissement du token")
        else:
            print("✅ Nouvel access token obtenu")
    else:
        print("🔓 Utilisation d'un access token valide")
    
    gauth.SaveCredentialsFile("credentials.json")
    return GoogleDrive(gauth)

def upload_to_drive(drive, file_path, drive_folder_id):
    """Upload un fichier vers Google Drive"""
    gfile = drive.CreateFile({
        'title': os.path.basename(file_path),
        'parents': [{'id': drive_folder_id}]
    })
    gfile.SetContentFile(file_path)
    gfile.Upload()
    print(f"✅ Fichier uploadé sur Google Drive: {gfile['title']}")
    return gfile

def get_drive_backups(drive, drive_folder_id):
    """Récupère la liste des backups existants sur Drive"""
    file_list = drive.ListFile({
        'q': f"'{drive_folder_id}' in parents and trashed=false and title contains 'SauvegardeBots_'"
    }).GetList()
    
    backups = []
    for file in file_list:
        match = re.search(r'SauvegardeBots_(\d{4}-\d{2}-\d{2})\.zip', file['title'])
        if match:
            backups.append((match.group(1), file))
    
    # Trier par date (du plus récent au plus ancien)
    backups.sort(reverse=True, key=lambda x: x[0])
    return backups

def clean_old_drive_backups(drive, backups, keep_count):
    """Supprime les anciennes sauvegardes sur Drive"""
    if len(backups) <= keep_count:
        print(f"ℹ️ {len(backups)} sauvegardes sur Drive (<= {keep_count}), aucune suppression")
        return
    
    to_delete = backups[keep_count:]
    for date_str, file in to_delete:
        print(f"🗑️ Suppression de l'ancienne sauvegarde Drive: {file['title']}")
        file.Delete()
    
    print(f"✅ {len(to_delete)} sauvegarde(s) supprimée(s)")

def main():
    print(f"🚀 Démarrage du script de sauvegarde - {datetime.datetime.now()}")
    
    # Vérifier le jour de la semaine
    today_weekday = datetime.datetime.today().weekday()
    if today_weekday not in CONFIG['backup_days']:
        jour_semaine = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'][today_weekday]
        print(f"📅 Aujourd'hui: {jour_semaine} - Pas de sauvegarde programmée")
        sys.exit(0)
    
    print(f"📅 Jour de sauvegarde - Lancement...")
    
    # Récupérer l'ID du dossier Drive depuis les secrets
    drive_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    if not drive_folder_id:
        raise Exception("❌ GOOGLE_DRIVE_FOLDER_ID non défini dans les secrets GitHub")
    
    # Créer la sauvegarde locale
    backup_name, backup_path = create_backup()
    
    try:
        # Authentifier et uploader
        drive = authentifier()
        upload_to_drive(drive, str(backup_path), drive_folder_id)
        
        # Nettoyer les anciennes sauvegardes sur Drive
        print("\n🧹 Nettoyage des anciennes sauvegardes sur Drive...")
        drive_backups = get_drive_backups(drive, drive_folder_id)
        clean_old_drive_backups(drive, drive_backups, CONFIG['backups_to_keep'])
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        sys.exit(1)
    
    finally:
        # Nettoyer le fichier temporaire
        if backup_path.exists():
            backup_path.unlink()
            print(f"🗑️ Fichier local supprimé: {backup_name}")
    
    print("✅ Sauvegarde terminée avec succès!")

if __name__ == "__main__":
    main()
