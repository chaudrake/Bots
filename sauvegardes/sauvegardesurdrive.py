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
    'backups_to_keep': 5,   # Nombre de sauvegardes à conserver
    'backup_days': [2, 6]   # 2=mercredi, 6=dimanche (Monday=0)
}

def create_backup():
    """Crée une archive zip du dossier parent (Bots) en excluant le dossier sauvegarde"""
    # Détermine la racine du projet (un niveau au-dessus du dossier 'sauvegardes')
    base_path = Path(__file__).resolve().parent.parent
    
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    backup_name = f"SauvegardeBots_{date_str}.zip"
    # On crée le zip à la racine du projet temporairement
    backup_path = base_path / backup_name
    
    print(f"📦 Préparation de la sauvegarde depuis : {base_path}")
    
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # On parcourt tout le dossier racine
        for file in base_path.rglob('*'):
            # Liste des éléments à ignorer
            # On ignore 'sauvegardes' pour éviter la récursion et le dossier .git
            excludes = ['.git', '__pycache__', 'sauvegardes', '.zip', 'credentials.json', '.pyc', '.log']
            
            # Vérification si le fichier ou l'un de ses dossiers parents est dans la liste d'exclusion
            if any(ex in file.parts for ex in excludes) or any(file.name.endswith(ex) for ex in ['.zip', '.log']):
                continue
            
            if file.is_file():
                # On écrit le fichier dans le zip avec son chemin relatif à la racine 'Bots'
                zipf.write(file, file.relative_to(base_path))
    
    print(f"✅ Sauvegarde créée localement: {backup_name} ({backup_path.stat().st_size / 1024 / 1024:.2f} MB)")
    return backup_name, backup_path

def authentifier():
    """Authentification OAuth avec Google Drive (pour GitHub Actions)"""
    # On cherche settings.yaml dans le même dossier que le script
    settings_path = Path(__file__).parent / "settings.yaml"
    gauth = GoogleAuth(settings_file=str(settings_path))
    
    credentials_json = os.getenv('GOOGLE_DRIVE_CREDENTIALS')
    if not credentials_json:
        raise Exception("❌ GOOGLE_DRIVE_CREDENTIALS non défini dans les secrets GitHub")
    
    # Création du fichier temporaire pour pydrive
    cred_file = Path(__file__).parent / "credentials.json"
    with open(cred_file, "w") as f:
        f.write(credentials_json)
    
    gauth.LoadCredentialsFile(str(cred_file))
    
    if gauth.credentials is None:
        raise Exception("❌ Credentials invalides")
    elif gauth.access_token_expired:
        print("♻️ Access token expiré → rafraîchissement...")
        gauth.Refresh()
    
    return GoogleDrive(gauth)

def upload_to_drive(drive, file_path, drive_folder_id):
    """Upload un fichier vers Google Drive"""
    gfile = drive.CreateFile({
        'title': os.path.basename(file_path),
        'parents': [{'id': drive_folder_id}]
    })
    gfile.SetContentFile(file_path)
    gfile.Upload()
    print(f"✅ Upload réussi: {gfile['title']}")
    return gfile

def get_drive_backups(drive, drive_folder_id):
    """Récupère la liste des backups existants sur Drive"""
    query = f"'{drive_folder_id}' in parents and trashed=false and title contains 'SauvegardeBots_'"
    file_list = drive.ListFile({'q': query}).GetList()
    
    backups = []
    for file in file_list:
        match = re.search(r'SauvegardeBots_(\d{4}-\d{2}-\d{2})\.zip', file['title'])
        if match:
            backups.append((match.group(1), file))
    
    backups.sort(reverse=True, key=lambda x: x[0])
    return backups

def clean_old_drive_backups(drive, backups, keep_count):
    """Supprime les anciennes sauvegardes sur Drive"""
    if len(backups) <= keep_count:
        print(f"ℹ️ {len(backups)} sauvegardes sur Drive. Rien à supprimer.")
        return
    
    to_delete = backups[keep_count:]
    for date_str, file in to_delete:
        print(f"🗑️ Suppression : {file['title']}")
        file.Delete()
    print(f"✅ Nettoyage terminé.")

def main():
    print(f"🚀 Lancement du script - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    today_weekday = datetime.datetime.today().weekday()
    if today_weekday not in CONFIG['backup_days']:
        print(f"📅 Pas de sauvegarde aujourd'hui (Jour {today_weekday}).")
        sys.exit(0)
    
    drive_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    if not drive_folder_id:
        print("❌ Erreur: GOOGLE_DRIVE_FOLDER_ID manquant.")
        sys.exit(1)
    
    backup_name, backup_path = create_backup()
    
    try:
        drive = authentifier()
        upload_to_drive(drive, str(backup_path), drive_folder_id)
        
        print("\n🧹 Nettoyage Drive...")
        drive_backups = get_drive_backups(drive, drive_folder_id)
        clean_old_drive_backups(drive, drive_backups, CONFIG['backups_to_keep'])
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {str(e)}")
        sys.exit(1)
    
    finally:
        if backup_path.exists():
            backup_path.unlink()
            print(f"🗑️ Nettoyage local terminé.")
        
        # Supprimer le fichier de credentials temporaire s'il existe
        cred_file = Path(__file__).parent / "credentials.json"
        if cred_file.exists():
            cred_file.unlink()

    print("✅ Opération terminée avec succès!")

if __name__ == "__main__":
    main()
  
