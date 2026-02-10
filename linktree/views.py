from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LienForm
from .models import Lien


def linktree_page(request):
    """Vue publique de la page LinkTree"""
    liens = Lien.objects.filter(actif=True).order_by('ordre', 'titre')
    context = {
        'liens': liens,
        'meta_description': (
            'Retrouvez tous nos liens importants sur une seule page - '
            'Réseaux sociaux, contacts, et plus encore.'
        )
    }
    return render(request, 'linktree/linktree_page.html', context)


@permission_required('linktree.view_lien')
def admin_liens_list(request):
    """Vue de la liste des liens pour l'administrateur"""
    liens = Lien.objects.all().order_by('ordre', 'titre')
    return render(request, 'linktree/admin_liens_list.html', {'liens': liens})


@permission_required('linktree.add_lien')
def admin_lien_add(request):
    """Vue d'ajout d'un lien pour l'administrateur"""
    if request.method == 'POST':
        form = LienForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Le lien a été ajouté avec succès.')
            return redirect('linktree:admin_liens_list')
        else:
            messages.error(request, 'Merci de corriger les erreurs dans le formulaire.')
    else:
        form = LienForm()

    return render(request, 'linktree/admin_lien_add.html', {'form': form})


@permission_required('linktree.change_lien')
def admin_lien_edit(request, pk):
    """Vue d'édition d'un lien pour l'administrateur"""
    lien = get_object_or_404(Lien, pk=pk)
    
    if request.method == 'POST':
        form = LienForm(request.POST, instance=lien)
        if form.is_valid():
            form.save()
            messages.success(request, 'Le lien a été modifié avec succès.')
            return redirect('linktree:admin_liens_list')
        else:
            messages.error(request, 'Merci de corriger les erreurs dans le formulaire.')
    else:
        form = LienForm(instance=lien)

    return render(
        request,
        'linktree/admin_lien_edit.html',
        {'form': form, 'lien': lien}
    )


@permission_required('linktree.delete_lien')
def admin_lien_delete(request, pk):
    """Vue de suppression d'un lien pour l'administrateur"""
    lien = get_object_or_404(Lien, pk=pk)

    if request.method == 'POST':
        if request.POST.get('confirm') == 'yes':
            lien.delete()
            messages.success(request, 'Le lien a été supprimé avec succès.')
        else:
            messages.error(request, 'La suppression a été annulée.')
        return redirect('linktree:admin_liens_list')

    return render(
        request,
        'linktree/admin_lien_delete.html',
        {'lien': lien}
    )
