import os
from pathlib import Path

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import BackupSettingsForm
from .models import BackupSettings
from .utils import cleanup_old_backups, create_backup_zip, get_stored_backups


@staff_member_required
def list_backups(request):
    """Affiche la liste des backups et les paramètres."""
    settings_obj = BackupSettings.get_settings()
    backups = get_stored_backups()
    
    if request.method == 'POST' and 'update_settings' in request.POST:
        form = BackupSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Paramètres de sauvegarde mis à jour avec succès.")
            return redirect('backup:list_backups')
    else:
        form = BackupSettingsForm(instance=settings_obj)
    
    context = {
        'backups': backups,
        'form': form,
        'settings': settings_obj,
    }
    return render(request, 'backup/list_backups.html', context)


@staff_member_required
def create_backup_download(request):
    """Crée un backup et le télécharge immédiatement."""
    try:
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backup_ccsa_{timestamp}.zip'
        
        # Créer le backup dans un fichier temporaire
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            create_backup_zip(tmp.name)
            tmp_path = tmp.name
        
        # Envoyer le fichier
        response = FileResponse(
            open(tmp_path, 'rb'),
            as_attachment=True,
            filename=filename
        )
        
        # Nettoyer le fichier temporaire après envoi
        response['X-Temp-File'] = tmp_path
        
        messages.success(request, f"Backup {filename} créé et téléchargé avec succès.")
        return response
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la création du backup : {str(e)}")
        return redirect('backup:list_backups')


@staff_member_required
def create_backup_store(request):
    """Crée un backup et le stocke sur le serveur."""
    try:
        backup_path = create_backup_zip()
        deleted = cleanup_old_backups(retention_count=4)
        
        messages.success(
            request, 
            f"Backup {backup_path.name} créé et stocké avec succès."
        )
        if deleted:
            messages.info(request, f"Anciens backups supprimés : {', '.join(deleted)}")
        
        return redirect('backup:list_backups')
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la création du backup : {str(e)}")
        return redirect('backup:list_backups')


@staff_member_required
def download_backup(request, filename):
    """Télécharge un backup stocké."""
    from django.conf import settings
    
    backup_dir = Path(settings.BACKUP_ROOT)
    file_path = backup_dir / filename
    
    # Sécurité : vérifier que le fichier est bien dans le dossier de backup
    try:
        file_path.resolve().relative_to(backup_dir.resolve())
    except ValueError:
        raise Http404("Fichier non trouvé")
    
    if not file_path.exists():
        raise Http404("Fichier non trouvé")
    
    return FileResponse(
        open(file_path, 'rb'),
        as_attachment=True,
        filename=filename
    )


@staff_member_required
def delete_backup(request, filename):
    """Supprime un backup stocké."""
    from django.conf import settings
    
    backup_dir = Path(settings.BACKUP_ROOT)
    file_path = backup_dir / filename
    
    # Sécurité : vérifier que le fichier est bien dans le dossier de backup
    try:
        file_path.resolve().relative_to(backup_dir.resolve())
    except ValueError:
        raise Http404("Fichier non trouvé")
    
    if file_path.exists():
        file_path.unlink()
        messages.success(request, f"Backup {filename} supprimé avec succès.")
    else:
        messages.error(request, "Fichier non trouvé.")
    
    return redirect('backup:list_backups')
