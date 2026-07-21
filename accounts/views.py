import hashlib
import logging
import smtplib
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from contact.models import ContactEmail

from .forms import (
    AdminUserCreationForm,
    CustomAuthenticationForm,
    CustomPasswordResetForm,
    CustomUserChangeForm,
    CustomUserCreationForm,
)
from .models import CustomUser

logger = logging.getLogger(__name__)
audit_logger = logging.getLogger("accounts.audit")

User = get_user_model()


class UserAction:
    """Actions d'administration disponibles sur un utilisateur."""

    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"
    DELETE = "delete"
    _ALL = {ACTIVATE, DEACTIVATE, DELETE}


def _rate_limit_key(prefix, value):
    """
    Génère une clé de cache pour le rate-limiting en hashant la valeur
    afin d'éviter les collisions et de respecter la limite de longueur
    des clés (ex: memcached limite à 250 caractères).
    """
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:32]
    return f"{prefix}:{digest}"


def est_moderateur(user):
    """
    Renvoie True si l'utilisateur est un modérateur ou un superutilisateur,
    sinon False.
    """
    return user.groups.filter(name="moderator").exists() or user.is_superuser


def _apply_session_expiry(request, remember_me: str | None) -> None:
    """
    Configure l'expiration de la session en fonction de la case
    « Se souvenir de moi ».

    - Case cochée : la session dure ``settings.SESSION_COOKIE_AGE``
      secondes (30 jours) et est glissante (``SESSION_SAVE_EVERY_REQUEST``).
    - Case non cochée : la session expire à la fermeture du navigateur.
    """
    if remember_me:
        request.session.set_expiry(settings.SESSION_COOKIE_AGE)
    else:
        request.session.set_expiry(0)


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
            user = form.save(commit=False)
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
    """Vue de connexion utilisant l'email avec protection rate limiting"""
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    user_count = CustomUser.objects.count()

    if request.method == "POST":
        # Rate limiting pour prévenir les attaques par force brute
        if not getattr(settings, "TESTING", False):
            # Obtenir l'IP réelle du client
            client_ip = request.META.get("REMOTE_ADDR") or "unknown"

            # Créer des clés de rate limiting par IP et par email
            rate_key_ip = _rate_limit_key("login_rate_ip", client_ip)
            email_key = request.POST.get("username", "unknown")
            rate_key_email = _rate_limit_key("login_rate_email", email_key)

            try:
                # Vérifier le rate limiting par IP (max 10 tentatives par 15 minutes)
                ip_attempts = cache.get(rate_key_ip, 0)
                if ip_attempts >= 10:
                    logger.warning(
                        f"Trop de tentatives de connexion depuis l'IP {client_ip}"
                    )
                    messages.error(
                        request,
                        _(
                            "Trop de tentatives de connexion depuis cette adresse IP. "
                            "Veuillez attendre 15 minutes avant de réessayer."
                        ),
                    )
                    return render(
                        request,
                        "accounts/login.html",
                        {"form": CustomAuthenticationForm(), "user_count": user_count},
                    )

                # Vérifier le rate limiting par email (max 5 tentatives par 15 minutes)
                email_attempts = cache.get(rate_key_email, 0)
                if email_attempts >= 5:
                    logger.warning(
                        f"Trop de tentatives de connexion pour l'email {email_key}"
                    )
                    messages.error(
                        request,
                        _(
                            "Trop de tentatives de connexion. "
                            "Veuillez attendre 15 minutes avant de réessayer."
                        ),
                    )
                    return render(
                        request,
                        "accounts/login.html",
                        {"form": CustomAuthenticationForm(), "user_count": user_count},
                    )
            except Exception as e:
                logger.error(f"Erreur dans le rate limiting: {e}")
                # En cas d'erreur, on continue mais on log l'erreur

        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=email, password=password)

            if user is not None:
                # Connexion réussie - réinitialiser les compteurs de rate limiting
                if not getattr(settings, "TESTING", False):
                    try:
                        cache.delete(rate_key_ip)
                        cache.delete(rate_key_email)
                    except Exception:
                        pass

                login(request, user)
                _apply_session_expiry(request, request.POST.get("remember_me"))
                logger.info(f"Connexion réussie pour l'utilisateur {email}")
                messages.success(request, _("Vous êtes maintenant connecté."))
                return redirect("accounts:profile")
            else:
                # Échec de connexion - incrémenter les compteurs
                if not getattr(settings, "TESTING", False):
                    try:
                        # Incrémenter le compteur IP
                        try:
                            cache.incr(rate_key_ip)
                        except ValueError:
                            cache.set(rate_key_ip, 1, timeout=900)  # 15 minutes

                        # Incrémenter le compteur email
                        try:
                            cache.incr(rate_key_email)
                        except ValueError:
                            cache.set(rate_key_email, 1, timeout=900)  # 15 minutes

                        logger.warning(
                            f"Échec de connexion pour {email_key} depuis {client_ip}"
                        )
                    except Exception:
                        pass

                messages.error(
                    request,
                    _("Adresse email ou mot de passe incorrect."),
                )
        else:
            # Formulaire invalide - incrémenter aussi les compteurs
            if not getattr(settings, "TESTING", False):
                try:
                    try:
                        cache.incr(rate_key_ip)
                    except ValueError:
                        cache.set(rate_key_ip, 1, timeout=900)
                    try:
                        cache.incr(rate_key_email)
                    except ValueError:
                        cache.set(rate_key_email, 1, timeout=900)
                except Exception:
                    pass
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


DASHBOARD_STATS_CACHE_KEY = "admin_dashboard_stats"
DASHBOARD_STATS_CACHE_TTL = 60  # secondes

CHECK_PAGES_CACHE_KEY = "check_pages_results"
CHECK_PAGES_CACHE_TTL = 300  # 5 minutes


def _compute_dashboard_stats():
    """
    Calcule les statistiques du dashboard en effectuant un COUNT par modèle.

    Les requetes ``COUNT(*)`` sont optimisees par Django (elles utilisent
    l'index sur la cle primaire). Le resultat est mis en cache court terme
    pour eviter de multiplier les COUNT a chaque hit de la page d'accueil
    admin (la page est rafraichie frequemment par les moderateurs).
    """
    from bureau_communautaire.models import Document, Elus
    from commissions.models import Commission
    from conseil_communautaire.models import ConseilMembre, ConseilVille
    from journal.models import Journal
    from services.models import Service

    return {
        "journals": Journal.objects.count(),
        "elus": Elus.objects.count(),
        "services": Service.objects.count(),
        "membres": ConseilMembre.objects.count(),
        "commissions": Commission.objects.count(),
        "villes": ConseilVille.objects.count(),
        "documents": Document.objects.count(),
        "contacts": ContactEmail.objects.count(),
    }


@login_required
@user_passes_test(lambda u: est_moderateur(u))
def admin_dashboard(request):
    """Vue dashboard admin qui regroupe tous les liens CRUD, réservé au superadmin."""
    from journal.models import Journal

    # Les stats de base sont mises en cache (60s) ; le compteur users,
    # qui depend de l'utilisateur courant, est calcule separement.
    stats = cache.get(DASHBOARD_STATS_CACHE_KEY)
    if stats is None:
        stats = _compute_dashboard_stats()
        cache.set(DASHBOARD_STATS_CACHE_KEY, stats, DASHBOARD_STATS_CACHE_TTL)

    # Statistiques admin (superuser uniquement)
    if request.user.is_superuser:
        stats["users"] = CustomUser.objects.count()

    # Derniers journaux publiés
    recent_journals = Journal.objects.order_by("-release_date")[:5]

    context = {
        "stats": stats,
        "recent_journals": recent_journals,
    }

    return render(request, "accounts/admin.html", context)


USER_LIST_PAGE_SIZE = 25


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_user_list(request):
    """
    Vue de liste des utilisateurs pour l'administrateur.

    - GET : affiche la liste paginée (recherche par email ou username).
    - POST : applique une action d'administration (activate/deactivate/delete).
      L'action est validée strictement ; toute valeur inconnue est rejetée
      avec un message d'erreur explicite.
    """
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")

        if user_id and action:
            if action not in UserAction._ALL:
                logger.warning(
                    "Action admin inconnue reçue: %r (user_id=%s, request_user=%s)",
                    action,
                    user_id,
                    request.user.pk,
                )
                messages.error(
                    request, _("Action inconnue. Aucun changement n'a été effectué.")
                )
                return redirect("accounts:admin_user_list")

            user = get_object_or_404(CustomUser, id=user_id)

            # Un superadmin ne peut pas modifier un autre superadmin
            if user.is_superuser and user != request.user:
                messages.error(
                    request,
                    _("Vous ne pouvez pas modifier un autre superadministrateur."),
                )
                return redirect("accounts:admin_user_list")

            # Empêcher un administrateur de s'auto-verrouiller
            if user == request.user and action in {
                UserAction.DEACTIVATE,
                UserAction.DELETE,
            }:
                messages.error(
                    request,
                    _(
                        "Vous ne pouvez pas désactiver ou supprimer votre "
                        "propre compte."
                    ),
                )
                return redirect("accounts:admin_user_list")

            if action == UserAction.ACTIVATE:
                user.is_active = True
                user.save(update_fields=["is_active"])
                audit_logger.info(
                    "user_activated target_user_id=%s by_user_id=%s target_email=%s",
                    user.pk,
                    request.user.pk,
                    user.email,
                )
                messages.success(
                    request,
                    _("L'utilisateur %(username)s a été activé.")
                    % {"username": user.username or user.email},
                )
            elif action == UserAction.DEACTIVATE:
                user.is_active = False
                user.save(update_fields=["is_active"])
                audit_logger.info(
                    "user_deactivated target_user_id=%s by_user_id=%s target_email=%s",
                    user.pk,
                    request.user.pk,
                    user.email,
                )
                messages.success(
                    request,
                    _("L'utilisateur %(username)s a été désactivé.")
                    % {"username": user.username or user.email},
                )
            elif action == UserAction.DELETE:
                username = user.username
                target_email = user.email
                target_pk = user.pk
                user.delete()
                audit_logger.warning(
                    "user_deleted target_user_id=%s by_user_id=%s target_email=%s",
                    target_pk,
                    request.user.pk,
                    target_email,
                )
                messages.success(
                    request,
                    _("L'utilisateur %(username)s a été supprimé.")
                    % {"username": username or target_email},
                )
        return redirect("accounts:admin_user_list")

    queryset = CustomUser.objects.all()
    search = request.GET.get("q", "").strip()
    if search:
        queryset = queryset.filter(
            Q(email__icontains=search) | Q(username__icontains=search)
        )
    queryset = queryset.order_by("-is_superuser", "-is_staff", "username")

    paginator = Paginator(queryset, USER_LIST_PAGE_SIZE)
    page = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "accounts/admin_user_list.html",
        {"page": page, "search": search},
    )


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_create_user(request):
    """
    Vue de création d'utilisateur pour l'administrateur.

    Utilise :class:`AdminUserCreationForm` qui gère la génération d'un mot de
    passe temporaire sécurisé (CSPRNG) et expose ``form.generated_password``
    en cas de génération automatique.
    """
    if request.method == "POST":
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            generated_password = form.generated_password

            if generated_password:
                _send_welcome_email(user, generated_password, request)

            if generated_password:
                messages.success(
                    request,
                    _(
                        "L'utilisateur %(username)s a été créé avec succès. "
                        "Mot de passe temporaire : %(password)s"
                    )
                    % {
                        "username": user.username or user.email,
                        "password": generated_password,
                    },
                )
            else:
                messages.success(
                    request,
                    _("L'utilisateur %(username)s a été créé avec succès.")
                    % {"username": user.username or user.email},
                )
            return redirect("accounts:admin_user_list")
    else:
        form = AdminUserCreationForm()

    return render(request, "accounts/admin_create_user.html", {"form": form})


@login_required
@user_passes_test(lambda u: est_moderateur(u))
def check_pages(request):
    """Vérifie le code HTTP de toutes les pages du site avec cache 5 min."""
    cached = cache.get(CHECK_PAGES_CACHE_KEY)
    if cached and request.GET.get("refresh") != "1":
        return render(request, "accounts/admin_check_pages.html", cached)

    base_url = request.build_absolute_uri("/").rstrip("/")
    pages = _get_pages_to_check()
    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_map = {
            executor.submit(_check_page, base_url, path, name): (name, path)
            for name, path in pages
        }
        for future in as_completed(future_map):
            try:
                results.append(future.result())
            except Exception as e:
                results.append(
                    {
                        "name": future_map[future][0],
                        "path": future_map[future][1],
                        "status_code": None,
                        "status": "error",
                        "response_time": None,
                        "error": str(e),
                    }
                )

    results.sort(key=lambda r: r["path"])

    context = {
        "results": results,
        "total": len(results),
        "ok_count": sum(1 for r in results if r["status"] == "ok"),
        "warning_count": sum(1 for r in results if r["status"] == "warning"),
        "error_count": sum(1 for r in results if r["status"] == "error"),
    }
    cache.set(CHECK_PAGES_CACHE_KEY, context, CHECK_PAGES_CACHE_TTL)

    return render(request, "accounts/admin_check_pages.html", context)


def _get_pages_to_check():
    """Génère la liste des pages à vérifier."""
    pages = []

    static_names = [
        ("Accueil", "home"),
        ("Élus", "bureau-communautaire:elus"),
        ("Conseil communautaire", "conseil_communautaire:conseil"),
        ("Comptes rendus", "comptes_rendus:comptes_rendus"),
        ("Procès-verbaux", "comptes_rendus:proces_verbaux"),
        ("Présentation", "presentation"),
        ("Compétences", "competences:competences"),
        ("Journal", "journal:journal"),
        ("Commissions", "commissions:commissions"),
        ("Marchés publics", "marches_publics"),
        ("Mobilité", "mobilite"),
        ("Habitat", "habitat"),
        ("Collecte des déchets", "collecte_dechets"),
        ("Encombrants", "encombrants"),
        ("Déchetteries", "dechetteries"),
        ("Maisons de santé", "maisons_sante"),
        ("Mutuelle", "mutuelle"),
        ("Contrat local de santé", "contrat_local_sante"),
        ("PLUi", "plui"),
        ("Guide des services", "equipe"),
        ("Semestriels", "semestriels:semestriel"),
        ("Rapports d'activité", "rapports_activite:rapports_activite"),
        ("Mentions légales", "mentions_legales"),
        ("Politique de confidentialité", "politique_confidentialite"),
        ("Politique des cookies", "cookies"),
        ("Plan du site", "plan_du_site"),
        ("Accessibilité", "accessibilite"),
        ("Médi@'pass", "mediapass"),
        ("CTG", "ctg"),
        ("Guide éco-citoyen", "guide_eco_citoyen"),
        ("CLÉA", "clea"),
        ("Développement économique", "dev_eco"),
        ("Kit logos", "kit_logos"),
        ("Liens utiles", "linktree:linktree_page"),
        ("Communes membres", "communes-membres:list"),
        ("Partenaires", "partenaires:partenaires"),
    ]

    for name, url_name in static_names:
        try:
            path = reverse(url_name)
            pages.append((name, path))
        except Exception:
            pass

    # Pages dynamiques : communes
    try:
        from conseil_communautaire.models import ConseilVille

        for ville in ConseilVille.objects.all():
            try:
                path = reverse("communes-membres:commune", kwargs={"slug": ville.slug})
                pages.append((f"Commune : {ville.city_name}", path))
            except Exception:
                pass
    except Exception:
        pass

    # Pages dynamiques : journaux
    try:
        from journal.models import Journal

        for journal in Journal.objects.all():
            try:
                path = reverse("journal:journal_detail", kwargs={"id": journal.id})
                pages.append((f"Journal : {journal.title}", path))
            except Exception:
                pass
    except Exception:
        pass

    return pages


def _check_page(base_url, path, name):
    """Vérifie statut HTTP et temps de réponse d'une page."""
    url = f"{base_url}{path}"
    start = time.time()
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            code = resp.status
            elapsed = round(time.time() - start, 2)

        if code == 200:
            status = "ok"
        elif 300 <= code < 400:
            status = "warning"
        else:
            status = "error"

        return {
            "name": name,
            "path": path,
            "status_code": code,
            "status": status,
            "response_time": elapsed,
            "error": None,
        }
    except urllib.error.HTTPError as e:
        elapsed = round(time.time() - start, 2)
        code = e.code
        return {
            "name": name,
            "path": path,
            "status_code": code,
            "status": "error" if code >= 400 else "warning",
            "response_time": elapsed,
            "error": None,
        }
    except urllib.error.URLError as e:
        elapsed = round(time.time() - start, 2)
        return {
            "name": name,
            "path": path,
            "status_code": None,
            "status": "error",
            "response_time": elapsed,
            "error": str(e.reason),
        }
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        return {
            "name": name,
            "path": path,
            "status_code": None,
            "status": "error",
            "response_time": elapsed,
            "error": str(e),
        }


def _send_welcome_email(user, password: str, request) -> bool:
    """
    Envoie un email de bienvenue avec le mot de passe temporaire.

    Échoue silencieusement en cas d'erreur SMTP pour ne pas bloquer la
    création du compte ; l'erreur est journalisée pour audit.
    """
    subject = _("Votre compte CCSA a été créé")
    context = {
        "user": user,
        "password": password,
        "domain": request.get_host(),
        "protocol": request.scheme,
    }
    try:
        message = render_to_string("accounts/welcome_email.txt", context)
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except (smtplib.SMTPException, OSError) as exc:
        logger.error("Échec d'envoi de l'email de bienvenue à %s: %s", user.email, exc)
        return False
