from django.urls import path

from . import views

app_name = 'backup'

urlpatterns = [
    path('adminccsa/sauvegardes/', views.list_backups, name='list_backups'),
    path('adminccsa/sauvegardes/telecharger-direct/', views.create_backup_download, name='create_backup_download'),
    path('adminccsa/sauvegardes/stocker/', views.create_backup_store, name='create_backup_store'),
    path('adminccsa/sauvegardes/telecharger/<str:filename>/', views.download_backup, name='download_backup'),
    path('adminccsa/sauvegardes/supprimer/<str:filename>/', views.delete_backup, name='delete_backup'),
]
