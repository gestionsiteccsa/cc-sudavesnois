import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_list_or_404, redirect, render
from django.template.loader import render_to_string

from conseil_communautaire.models import ConseilVille
from contact.forms import ContactForm
from contact.models import ContactEmail
from journal.models import Journal
from services.models import Service

logger = logging.getLogger(__name__)


def is_staff_or_superuser(user):
    """Vérifier si l'utilisateur est staff ou superuser.

    Args:
        user: L'utilisateur à vérifier.

    Returns:
        bool: True si l'utilisateur est staff ou superuser.
    """
    return user.is_staff or user.is_superuser


def home(request):
    # Donnée requises pour la page d'accueil
    if Service.objects.exists():
        services = get_list_or_404(Service.objects.order_by("title"))
    else:
        services = None

    if ConseilVille.objects.exists():
        communes = get_list_or_404(ConseilVille)
        nb_communes = len(communes)
        nb_habitants = 0
        for commune in communes:
            nb_habitants += commune.nb_habitants

    else:
        communes = None
        nb_communes = None
        nb_habitants = None

    # Récupérer le dernier journal (trié par numéro décroissant)
    dernier_journal = Journal.objects.order_by("-number").first()

    if request.method == "POST":
        # Rate limiting simple: 5 requêtes par minute par adresse IP
        if not getattr(settings, "TESTING", False):
            client_ip = (
                request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
                or request.META.get("REMOTE_ADDR")
                or "unknown"
            )
            rate_key = f"contact_rate:{client_ip}"
            try:
                # Initialise le compteur avec expiration de 60s si absent
                created = cache.add(rate_key, 1, timeout=60)
                if not created:
                    current = cache.incr(rate_key)
                    if current > 5:
                        # Trop de tentatives: on bloque discrètement
                        return redirect("home")
            except Exception:
                # En cas de problème de cache, on n'empêche pas la soumission
                pass
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            # Toujours envoyer à contact@cc-sudavesnois.fr
            ccsa_contact_list = ["contact@cc-sudavesnois.fr"]

            # Ajouter les contacts actifs supplémentaires s'ils existent
            if ContactEmail.objects.exists():
                additional_contacts = list(
                    ContactEmail.objects.filter(is_active=True).values_list(
                        "email", flat=True
                    )
                )
                # Ajouter les contacts supplémentaires sans doublons
                for email in additional_contacts:
                    if email not in ccsa_contact_list:
                        ccsa_contact_list.append(email)

            context = {
                "first_name": contact_form.cleaned_data["first_name"],
                "last_name": contact_form.cleaned_data["last_name"],
                "email": contact_form.cleaned_data["email"],
                "phone": contact_form.cleaned_data["phone"],
                "message": contact_form.cleaned_data["message"],
            }

            try:
                # Mail au CCSA (contact@cc-sudavesnois.fr ou ContactEmail actif)
                text_content = render_to_string("email_text.txt", context)
                html_content = render_to_string("email_html.html", context)
                from_email = contact_form.cleaned_data["email"]
                to_email = ccsa_contact_list
                first_name = contact_form.cleaned_data["first_name"]
                last_name = contact_form.cleaned_data["last_name"]
                msg = EmailMultiAlternatives(
                    subject=(
                        f"CONTACT - CCSA : {first_name} {last_name}"
                    ),
                    body=text_content,
                    from_email=from_email,
                    to=to_email,
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                # Mail de confirmation au client depuis
                # nepasrepondre@cc-sudavesnois.fr
                text_content_client = render_to_string(
                    "email_text_client.txt", context
                )
                html_content_client = render_to_string(
                    "email_html_client.html", context
                )
                from_email_confirmation = "CCSA - Ne pas répondre <nepasrepondre@cc-sudavesnois.fr>"
                to_email_client = [contact_form.cleaned_data["email"]]
                msg_client = EmailMultiAlternatives(
                    subject=(
                        f"CONFIRMATION DE CONTACT - CCSA : "
                        f"{first_name} {last_name}"
                    ),
                    body=text_content_client,
                    from_email=from_email_confirmation,
                    to=to_email_client,
                )

                msg_client.attach_alternative(html_content_client, "text/html")
                msg_client.send()

                messages.success(
                    request,
                    (
                        "Votre message a été envoyé avec succès. "
                        "Vous recevrez un email de confirmation sous peu."
                    ),
                )
                user_email = contact_form.cleaned_data["email"]
                logger.info(
                    f"Email de contact envoyé avec succès pour {user_email}"
                )
                return redirect("home")
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de l'email de contact: {e}")
                messages.error(
                    request,
                    (
                        "Une erreur est survenue lors de l'envoi de votre "
                        "message. Veuillez réessayer plus tard ou nous "
                        "contacter directement."
                    ),
                )
                return redirect("home")
        else:
            # Formulaire invalide : re-rendre la page avec les erreurs
            logger.warning(f"Formulaire de contact invalide: {contact_form.errors}")
            context = {
                "services": services,
                "communes": communes,
                "contact_form": contact_form,
                "nb_communes": nb_communes,
                "nb_habitants": nb_habitants,
                "form_has_errors": True,
                "dernier_journal": dernier_journal,
            }
            return render(request, "home/index.html", context)
    else:
        contact_form = ContactForm()

    context = {
        "services": services,
        "communes": communes,
        "contact_form": contact_form,
        "nb_communes": nb_communes,
        "nb_habitants": nb_habitants,
        "form_has_errors": False,
        "dernier_journal": dernier_journal,
    }

    return render(request, "home/index.html", context)


def conseil(request):
    return render(request, "home/conseil.html")


def presentation(request):
    if ConseilVille.objects.exists():
        communes = get_list_or_404(ConseilVille)
        nb_communes = len(communes)
        nb_habitants = 0
        for commune in communes:
            nb_habitants += commune.nb_habitants
    else:
        communes = None
        nb_communes = 0
        nb_habitants = 0

    context = {
        "communes": communes,
        "nb_communes": nb_communes,
        "nb_habitants": nb_habitants,
    }

    return render(request, "home/presentation.html", context)


def marches_publics(request):
    return render(request, "home/marches-publics.html")


def mobilite(request):
    return render(request, "home/mobilite.html")


def habitat(request):
    return render(request, "home/habitat.html")


def collecte_dechets(request):
    return render(request, "home/collecte-dechets.html")


def encombrants(request):
    return render(request, "home/encombrants.html")


def dechetteries(request):
    return render(request, "home/dechetteries.html")


def maisons_sante(request):
    return render(request, "home/maisons-sante.html")


def mutuelle(request):
    return render(request, "home/mutuelle.html")


def contrat_local_sante(request):
    return render(request, "home/contrat-local-sante.html")


def plui(request):
    """Vue pour la page PLUi et le formulaire de modification."""
    from django.contrib import messages
    from .forms import PLUiModificationForm
    from .services import EmailService
    import logging

    logger = logging.getLogger(__name__)

    if request.method == "POST":
        form = PLUiModificationForm(request.POST)

        if form.is_valid():
            # Récupération des données validées
            form_data = form.cleaned_data

            # Envoi de l'email via le service
            if EmailService.send_plui_modification_request(form_data):
                messages.success(
                    request,
                    'Votre demande de modification PLUi a été envoyée avec succès. '
                    'Nous vous contacterons dans les plus brefs délais.'
                )
                logger.info(f"Demande PLUi envoyée pour {form_data['nom_prenom']}")
            else:
                messages.error(
                    request,
                    'Une erreur est survenue lors de l\'envoi de votre demande. '
                    'Veuillez réessayer ou nous contacter directement.'
                )
                logger.error(f"Échec envoi email PLUi pour {form_data['nom_prenom']}")

            return redirect('plui')
        else:
            # Affichage des erreurs de validation
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")

            logger.warning(f"Formulaire PLUi invalide: {form.errors}")
    else:
        form = PLUiModificationForm()

    context = {'form': form}
    return render(request, "home/plui.html", context)


def projet_plui(request):
    return render(request, "home/projet-plui.html")


def equipe(request):
    return render(request, "home/equipe.html")


def mentions_legales(request):
    return render(request, "home/mentions-legales.html")


def politique_confidentialite(request):
    return render(request, "home/politique-confidentialite.html")


def cookies(request):
    return render(request, "home/cookies.html")


def plan_du_site(request):
    return render(request, "home/plan-du-site.html")


def accessibilite(request):
    return render(request, "home/accessibilite.html")


def mediapass(request):
    return render(request, "home/mediapass.html")



def guide_eco_citoyen(request):
    """Vue pour la page Guide Pratique Éco-Citoyen."""
    return render(request, "home/guide-eco-citoyen.html")


def documents_plui(request):
    """Vue pour la page des documents PLUi et le formulaire de modification."""
    from django.contrib import messages
    from .forms import PLUiModificationForm
    from .services import EmailService
    import logging

    logger = logging.getLogger(__name__)

    if request.method == "POST":
        form = PLUiModificationForm(request.POST)

        if form.is_valid():
            # Récupération des données validées
            form_data = form.cleaned_data

            # Envoi de l'email via le service
            if EmailService.send_plui_modification_request(form_data):
                messages.success(
                    request,
                    'Votre demande de modification PLUi a été envoyée avec succès. '
                    'Nous vous contacterons dans les plus brefs délais.'
                )
                logger.info(f"Demande PLUi envoyée pour {form_data['nom_prenom']}")
            else:
                messages.error(
                    request,
                    'Une erreur est survenue lors de l\'envoi de votre demande. '
                    'Veuillez réessayer ou nous contacter directement.'
                )
                logger.error(f"Échec envoi email PLUi pour {form_data['nom_prenom']}")

            return redirect('documents_plui')
        else:
            # Affichage des erreurs de validation
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")

            logger.warning(f"Formulaire PLUi invalide: {form.errors}")
    else:
        form = PLUiModificationForm()

    context = {'form': form}
    return render(request, "home/documents-plui.html", context)


def test_email(request):
    """Vue de test pour l'envoi d'emails."""
    from django.contrib import messages
    from .services import EmailService
    
    # Données de test
    test_data = {
        'nom_prenom': 'Test Utilisateur',
        'adresse': '123 Rue de Test, 59000 Lille',
        'email': 'test@example.com',
        'telephone': '03 27 12 34 56',
        'parcelles': '123, 124',
        'commune': 'Féron',
        'demande': 'Ceci est un test d\'envoi d\'email pour vérifier la configuration.'
    }
    
    try:
        # Test d'envoi
        success = EmailService.send_plui_modification_request(test_data)
        
        if success:
            messages.success(request, 'Email de test envoyé avec succès !')
        else:
            messages.error(request, 'Erreur lors de l\'envoi de l\'email de test.')
            
    except Exception as e:
        messages.error(request, f'Erreur: {str(e)}')
    
    return redirect('documents_plui')


def dev_eco(request):
    return render(request, "home/dev-eco.html")


def kit_logos(request):
    return render(request, "home/kit-logos.html")


def custom_handler404(request, exception=None):
    """Vue personnalisée pour la page 404."""
    response = render(request, "404.html", status=404)
    return response


def custom_handler500(request):
    """Vue personnalisée pour la page 500."""
    # Log de l'erreur pour le débogage (en production, utilisez un système de logging)
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Erreur 500 sur {request.path}", exc_info=True)

    response = render(request, "500.html", status=500)
    return response
