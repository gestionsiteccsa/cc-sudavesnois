from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from .forms import (
    CustomAuthenticationForm,
    CustomPasswordResetForm,
    CustomUserChangeForm,
    CustomUserCreationForm,
)
from .models import CustomUser


def est_moderateur(user):
    """
    Renvoie True si l'utilisateur est un modérateur ou un superutilisateur,
    sinon False.
    """
    if user.groups.filter(name="moderator").exists() or user.is_superuser:
        return True
    return False


def register_view(request):
    """Vue d'inscription pour le premier utilisateur uniquement"""
    # Vérifier s'il existe déjà des utilisateurs
    user_count = CustomUser.objects.count()
    if user_count > 0:
        messages.error(
            request,
            _(
                "L'inscription n'est plus disponible. Veuillez contacter un "
                "administrateur."
            ),
        )
        return redirect("accounts:login")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Le premier utilisateur devient automatiquement superadmin
            user.is_staff = True
            user.is_superuser = True
            user.save()

            # Connecter l'utilisateur après l'inscription
            login(request, user)
            messages.success(
                request,
                _(
                    "Votre compte a été créé avec succès."
                    " Vous êtes maintenant connecté."
                ),
            )
            return redirect("accounts:profile")
    else:
        form = CustomUserCreationForm()

    return render(
        request, "accounts/register.html", {"form": form, "user_count": user_count}
    )


def login_view(request):
    """Vue de connexion utilisant l'email"""
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    user_count = CustomUser.objects.count()

    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, _("Vous êtes maintenant connecté."))
                return redirect("accounts:profile")
    else:
        form = CustomAuthenticationForm()

    return render(
        request, "accounts/login.html", {"form": form, "user_count": user_count}
    )


@login_required
def profile_view(request):
    """Vue de profil utilisateur"""
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Votre profil a été mis à jour avec succès."))
            return redirect("accounts:profile")
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, "accounts/profile.html", {"form": form})


def password_reset_view(request):
    """Vue de réinitialisation de mot de passe"""
    if request.method == "POST":
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = CustomUser.objects.get(email=email)
                # Générer un token de réinitialisation
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # Envoyer l'email
                subject = _("Réinitialisation de votre mot de passe - CCSA")
                message = render_to_string(
                    "accounts/password_reset_email.html",
                    {
                        "user": user,
                        "protocol": request.scheme,
                        "domain": request.get_host(),
                        "uid": uid,
                        "token": token,
                    },
                )
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

                return redirect("accounts:password_reset_done")
            except CustomUser.DoesNotExist:
                # Ne pas révéler que l'email n'existe pas pour des raisons de
                # sécurité
                return redirect("accounts:password_reset_done")
    else:
        form = CustomPasswordResetForm()

    return render(request, "accounts/password_reset.html", {"form": form})


def password_reset_done_view(request):
    """Vue de confirmation d'envoi d'email de réinitialisation"""
    return render(request, "accounts/password_reset_done.html")


def password_reset_confirm_view(request, uidb64, token):
    """Vue de confirmation de réinitialisation de mot de passe"""
    try:
        # Décoder l'uid et récupérer l'utilisateur
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)

        # Vérifier que le token est valide
        if default_token_generator.check_token(user, token):
            if request.method == "POST":
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(
                        request, _("Votre mot de passe a été réinitialisé avec succès.")
                    )
                    return redirect("accounts:password_reset_complete")
            else:
                form = SetPasswordForm(user)

            return render(
                request,
                "accounts/password_reset_confirm.html",
                {"form": form, "validlink": True},
            )
        else:
            # Token invalide
            return render(
                request, "accounts/password_reset_confirm.html", {"validlink": False}
            )
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        # Uid invalide
        return render(
            request, "accounts/password_reset_confirm.html", {"validlink": False}
        )


def logout_view(request):
    """Déconnecte l'utilisateur et redirige vers
    la page de connexion avec un message."""
    logout(request)
    messages.success(request, _("Vous avez été déconnecté avec succès."))
    return redirect("accounts:login")


def password_reset_complete_view(request):
    """Vue de confirmation finale de réinitialisation de mot de passe"""
    return render(request, "accounts/password_reset_complete.html")


@login_required
@user_passes_test(lambda u: est_moderateur(u))
def admin_dashboard(request):
    """Vue dashboard admin qui regroupe tous les liens CRUD, réservé au superadmin."""
    return render(request, "accounts/admin.html")


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_user_list(request):
    """Vue de liste des utilisateurs pour l'administrateur"""
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")

        if user_id and action:
            user = get_object_or_404(CustomUser, id=user_id)

            # Empêcher la modification des superadmins par d'autres superadmins
            if user.is_superuser and user != request.user:
                messages.error(
                    request,
                    _("Vous ne pouvez pas modifier un autre " "superadministrateur."),
                )
                return redirect("accounts:admin_user_list")

            if action == "activate":
                user.is_active = True
                user.save()
                messages.success(
                    request, _(f"L'utilisateur {user.username} a été activé.")
                )
            elif action == "deactivate":
                user.is_active = False
                user.save()
                messages.success(
                    request, _(f"L'utilisateur {user.username} a été désactivé.")
                )
            elif action == "delete" and user != request.user:
                username = user.username
                user.delete()
                messages.success(
                    request, _(f"L'utilisateur {username} a été supprimé.")
                )

    users = CustomUser.objects.all().order_by("-is_superuser", "-is_staff", "username")

    return render(request, "accounts/admin_user_list.html", {"users": users})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_create_user(request):
    """Vue de création d'utilisateur pour l'administrateur"""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if form.cleaned_data.get("is_staff"):
                user.is_staff = True
                user.save()

            messages.success(
                request, _(f"L'utilisateur {user.username} a été créé avec succès.")
            )
            return redirect("accounts:admin_user_list")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/admin_create_user.html", {"form": form})
