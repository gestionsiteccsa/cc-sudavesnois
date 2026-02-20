import logging
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, redirect, render
from django.template.loader import render_to_string
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.utils import ImageReader

from conseil_communautaire.models import ConseilVille
from contact.forms import ContactForm
from contact.models import ContactEmail
from journal.models import Journal
from services.models import Service
from home.data.collecte_data import get_dates_verre, get_jour_ordures, city_data
from io import BytesIO

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


def telecharger_calendrier_verre(request):
    """
    Vue pour générer et télécharger le calendrier de collecte du verre en PDF.
    """
    from io import BytesIO

    commune = request.GET.get('commune', '')
    rue = request.GET.get('rue', '')

    if not commune:
        return HttpResponse(
            b"Parametre 'commune' requis",
            status=400,
            content_type='text/plain'
        )

    if commune not in city_data:
        return HttpResponse(
            f"Commune '{commune}' non trouvee".encode('utf-8'),
            status=404,
            content_type='text/plain'
        )

    # Déterminer le jour de collecte
    jour_ordures, rue_trouvee = get_jour_ordures(commune, rue)

    # Récupérer les dates de verre
    dates_verre = get_dates_verre(commune, jour_ordures)

    if not dates_verre:
        return HttpResponse(
            f"Aucune date de collecte du verre trouvee pour {commune}".encode('utf-8'),
            status=404,
            content_type='text/plain'
        )

    # Créer le PDF en mémoire
    buffer = BytesIO()

    # Nom du fichier
    if rue:
        filename = f"calendrier-verre-{commune.lower()}-{rue.lower().replace(' ', '-')}.pdf"
    else:
        filename = f"calendrier-verre-{commune.lower()}.pdf"

    # Créer le document PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#006ab3'),
        spaceAfter=20,
        alignment=1  # Centre
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12
    )
    normal_style = styles["Normal"]
    normal_style.fontSize = 10
    
    # Liste des éléments du PDF
    elements = []
    
    # Logo
    try:
        logo_path = settings.BASE_DIR / "static" / "img" / "Kits-Logos" / "PNG_Transparent" / "Logo_couleur.png"
        if logo_path.exists():
            img = ImageReader(str(logo_path))
            # Ajouter le logo (taille réduite)
            from reportlab.platypus import Image
            logo = Image(str(logo_path), width=6*cm, height=3*cm)
            elements.append(logo)
            elements.append(Spacer(1, 0.5*cm))
    except Exception as e:
        logger.warning(f"Impossible de charger le logo: {e}")
    
    # Titre
    elements.append(Paragraph(
        "Calendrier de collecte du verre",
        title_style
    ))
    elements.append(Spacer(1, 0.5*cm))
    
    # Informations de la commune/rue
    elements.append(Paragraph(f"<b>Commune :</b> {commune}", subtitle_style))
    if rue_trouvee:
        elements.append(Paragraph(f"<b>Rue :</b> {rue_trouvee}", subtitle_style))
    
    # Jour de collecte des ordures
    if jour_ordures:
        elements.append(Paragraph(
            f"<b>Collecte des ordures :</b> le {jour_ordures}",
            normal_style
        ))
        elements.append(Spacer(1, 0.3*cm))
    
    # Jour de collecte du verre
    if isinstance(city_data[commune]["verre"], dict):
        if "jour" in city_data[commune]["verre"]:
            jour_verre = city_data[commune]["verre"]["jour"]
        elif jour_ordures and jour_ordures.lower() in city_data[commune]["verre"]:
            jour_verre = jour_ordures
        else:
            jour_verre = list(city_data[commune]["verre"].keys())[0]
        
        elements.append(Paragraph(
            f"<b>Collecte du verre :</b> le {jour_verre}",
            normal_style
        ))
        elements.append(Spacer(1, 0.5*cm))
    
    # Tableau des dates
    elements.append(Paragraph("<b>Dates de collecte 2026-2027</b>", subtitle_style))
    elements.append(Spacer(1, 0.2*cm))
    
    # Préparer les données du tableau
    table_data = [['Date', 'Jour']]
    
    for date_str in dates_verre:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            date_formatee = date_obj.strftime('%d/%m/%Y')
            jour_semaine = date_obj.strftime('%A').capitalize()
            table_data.append([date_formatee, jour_semaine])
        except ValueError:
            continue
    
    # Créer le tableau
    table = Table(table_data, colWidths=[8*cm, 8*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#006ab3')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 1*cm))
    
    # Footer avec contact
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=1
    )
    elements.append(Paragraph(
        "Communauté de Communes Sud-Avesnois<br/>"
        "24 avenue de la Marlière - 59610 FOURMIES<br/>"
        "Tél : 03 27 60 65 24 | contact@cc-sudavesnois.fr",
        footer_style
    ))
    
    # Générer le PDF
    doc.build(elements)

    # Créer la réponse HTTP avec le PDF
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response
