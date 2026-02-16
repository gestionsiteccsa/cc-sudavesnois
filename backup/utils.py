import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone


def get_backup_dir():
    """Retourne le chemin du dossier de backup."""
    return Path(settings.BACKUP_ROOT)


def create_backup_zip(output_path=None):
    """
    Crée un backup ZIP contenant la BDD SQLite et le dossier media.
    
    Args:
        output_path: Chemin du fichier ZIP à créer. Si None, retourne le zip en mémoire.
    
    Returns:
        Path du fichier créé ou None si output_path est None
    """
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    
    if output_path is None:
        backup_dir = get_backup_dir()
        backup_dir.mkdir(parents=True, exist_ok=True)
        output_path = backup_dir / f'backup_{timestamp}.zip'
    
    # Créer le ZIP
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 1. Base de données SQLite
        db_path = settings.DATABASES['default']['NAME']
        if os.path.exists(db_path):
            zipf.write(db_path, f'db/db.sqlite3')
        
        # 2. Dossier media
        media_root = settings.MEDIA_ROOT
        if os.path.exists(media_root):
            for root, dirs, files in os.walk(media_root):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.join('media', os.path.relpath(file_path, media_root))
                    zipf.write(file_path, arcname)
        
        # 3. Fichier manifest
        manifest = {
            'created_at': timezone.now().isoformat(),
            'timestamp': timestamp,
            'database': 'db.sqlite3',
            'media_path': 'media/',
        }
        import json
        zipf.writestr('manifest.json', json.dumps(manifest, indent=2))
    
    return output_path


def cleanup_old_backups(retention_count=4):
    """
    Supprime les anciens backups pour ne garder que les N plus récents.
    
    Args:
        retention_count: Nombre de backups à conserver (défaut: 4)
    """
    backup_dir = get_backup_dir()
    
    if not backup_dir.exists():
        return []
    
    # Lister tous les fichiers backup_*.zip
    backups = sorted(
        backup_dir.glob('backup_*.zip'),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    deleted = []
    for old_backup in backups[retention_count:]:
        old_backup.unlink()
        deleted.append(old_backup.name)
    
    return deleted


def get_stored_backups():
    """
    Retourne la liste des backups stockés avec leurs métadonnées.
    
    Returns:
        Liste de dicts avec 'name', 'size', 'created_at', 'path'
    """
    backup_dir = get_backup_dir()
    
    if not backup_dir.exists():
        return []
    
    backups = []
    for backup_file in sorted(backup_dir.glob('backup_*.zip'), reverse=True):
        stat = backup_file.stat()
        backups.append({
            'name': backup_file.name,
            'size': stat.st_size,
            'size_human': format_size(stat.st_size),
            'created_at': datetime.fromtimestamp(stat.st_mtime),
            'path': backup_file,
        })
    
    return backups


def format_size(size_bytes):
    """Formatte la taille en bytes en format lisible."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def send_backup_notification(success, email_to, backup_name=None, error_message=None):
    """
    Envoie un email de notification après une sauvegarde.
    
    Args:
        success: True si la sauvegarde a réussi
        email_to: Adresse email du destinataire
        backup_name: Nom du fichier backup (si succès)
        error_message: Message d'erreur (si échec)
    """
    if not email_to:
        return
    
    if success:
        subject = '[CCSA] Sauvegarde automatique réussie'
        message = f"""Bonjour,

La sauvegarde automatique du site CCSA s'est déroulée avec succès.

Détails :
- Fichier : {backup_name}
- Date : {timezone.now().strftime('%d/%m/%Y à %H:%M')}
- Emplacement : {get_backup_dir()}

Les 4 dernières sauvegardes sont conservées. Les plus anciennes sont automatiquement supprimées.

Cordialement,
Le système de backup CCSA
"""
    else:
        subject = '[CCSA] ÉCHEC de la sauvegarde automatique'
        message = f"""Bonjour,

La sauvegarde automatique du site CCSA a échoué.

Date : {timezone.now().strftime('%d/%m/%Y à %H:%M')}
Erreur : {error_message}

Veuillez vérifier le système et lancer une sauvegarde manuelle si nécessaire.

Cordialement,
Le système de backup CCSA
"""
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email_to],
        fail_silently=True,
    )
