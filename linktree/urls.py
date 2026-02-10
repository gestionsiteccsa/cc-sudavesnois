from django.urls import path
from . import views

app_name = 'linktree'

urlpatterns = [
    # Page publique
    path('nos-liens/', views.linktree_page, name='linktree_page'),
    
    # Administration
    path('adminccsa/liens/', views.admin_liens_list, name='admin_liens_list'),
    path('adminccsa/liens/ajouter/', views.admin_lien_add, name='admin_lien_add'),
    path('adminccsa/liens/modifier/<int:pk>/',
         views.admin_lien_edit, name='admin_lien_edit'),
    path('adminccsa/liens/supprimer/<int:pk>/',
         views.admin_lien_delete, name='admin_lien_delete'),
]
