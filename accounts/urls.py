from django.urls import path

from . import views

app_name = "accounts"  # Ajout du namespace

urlpatterns = [
    # Inscription (uniquement pour le premier utilisateur)
    path("register/", views.register_view, name="register"),
    # Connexion / Déconnexion
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # Profil utilisateur
    path("profile/", views.profile_view, name="profile"),
    # Réinitialisation de mot de passe
    path("password-reset/", views.password_reset_view, name="password_reset"),
    path(
        "password-reset/done/",
        views.password_reset_done_view,
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.password_reset_confirm_view,
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        views.password_reset_complete_view,
        name="password_reset_complete",
    ),
    # Dashboard admin (superadmin uniquement)
    path("adminccsa/", views.admin_dashboard, name="admin_dashboard"),
    # Administration des utilisateurs (superadmin uniquement)
    path("adminccsa/utilisateurs/", views.admin_user_list, name="admin_user_list"),
    path(
        "adminccsa/utilisateurs/creer/",
        views.admin_create_user,
        name="admin_create_user",
    ),
]
