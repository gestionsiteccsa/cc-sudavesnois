import logging
from datetime import datetime
from xml.sax.saxutils import escape as xml_escape

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page

from app.utils import get_client_ip, hash_ip, normalize_filename, rate_limit
from conseil_communautaire.models import ConseilVille
from contact.forms import ContactForm
from contact.models import ContactEmail
from home.data.collecte_data import (
    city_data,
    get_dates_verre,
    get_jour_ordures,
)
from journal.models import Journal
from services.models import Service

logger = logging.getLogger(__name__)


@cache_page(300)
def home(request):
    # Donnée requises pour la page d'accueil

    # Optimisé : récupération unique des services
    services = list(Service.objects.order_by("title"))
    services = services if services else None

    # Optimisé : 1 aggregate pour les stats + 1 liste pour l'affichage
    communes_stats = ConseilVille.objects.aggregate(
        nb=Count("id"),
        total_hab=Sum("nb_habitants"),
    )
    nb_communes = communes_stats["nb"] or 0
    nb_habitants = communes_stats["total_hab"] or 0
    communes = list(
        ConseilVille.objects.only("city_name", "slug").order_by("city_name")
    )
    communes = communes if communes else None

    # Récupérer le dernier journal (trié par numéro décroissant)
    dernier_journal = Journal.objects.order_by("-number").first()

    if request.method == "POST":
        # Rate limiting simple: 5 requêtes par minute par adresse IP
        if not getattr(settings, "TESTING", False):
            allowed, current, limit = rate_limit(
                request,
                action="contact_form",
                max_calls=5,
                window=60,
            )
            if not allowed:
                client_ip = get_client_ip(request)
                logger.warning(
                    "Rate limit contact depasse: IP=%s hash=%s current=%d",
                    client_ip,
                    hash_ip(client_ip),
                    current,
                )
                return redirect("home")
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            # Toujours envoyer à contact@cc-sudavesnois.fr
            ccsa_contact_list = ["contact@cc-sudavesnois.fr"]

            # Récupérer les contacts actifs supplémentaires en une seule requete
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
                # SECURITE: utiliser DEFAULT_FROM_EMAIL comme From pour eviter
                # le rejet SPF/DKIM. Le reply-to est positionne sur l'email
                # du visiteur pour que l'agent puisse repondre.
                visitor_email = contact_form.cleaned_data["email"]
                to_email = ccsa_contact_list
                first_name = contact_form.cleaned_data["first_name"]
                last_name = contact_form.cleaned_data["last_name"]
                msg = EmailMultiAlternatives(
                    subject=(f"CONTACT - CCSA : {first_name} {last_name}"),
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=to_email,
                    reply_to=[visitor_email],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                # Mail de confirmation au client depuis
                # nepasrepondre@cc-sudavesnois.fr
                text_content_client = render_to_string("email_text_client.txt", context)
                html_content_client = render_to_string(
                    "email_html_client.html", context
                )
                from_email_confirmation = (
                    "CCSA - Ne pas répondre <nepasrepondre@cc-sudavesnois.fr>"
                )
                to_email_client = [contact_form.cleaned_data["email"]]
                msg_client = EmailMultiAlternatives(
                    subject=(
                        f"CONFIRMATION DE CONTACT - CCSA : " f"{first_name} {last_name}"
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
                logger.info(f"Email de contact envoyé avec succès pour {user_email}")
                return redirect("home")
            except Exception as e:
                logger.error(
                    f"Erreur lors de l'envoi de l'email de contact: {e}",
                    exc_info=True,
                )
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


@cache_page(60 * 15)
def conseil(request):
    return render(request, "home/conseil.html")


@cache_page(60 * 15)
def presentation(request):
    # 1 aggregate + 1 liste au lieu de charger toutes les colonnes pour sommer
    communes_stats = ConseilVille.objects.aggregate(
        nb=Count("id"),
        total_hab=Sum("nb_habitants"),
    )
    nb_communes = communes_stats["nb"] or 0
    nb_habitants = communes_stats["total_hab"] or 0
    communes = list(
        ConseilVille.objects.only("city_name", "slug").order_by("city_name")
    )
    communes = communes if communes else None

    context = {
        "communes": communes,
        "nb_communes": nb_communes,
        "nb_habitants": nb_habitants,
    }

    return render(request, "home/presentation.html", context)


@cache_page(60 * 15)
def marches_publics(request):
    return render(request, "home/marches-publics.html")


@cache_page(60 * 15)
def mobilite(request):
    return render(request, "home/mobilite.html")


@cache_page(60 * 15)
def habitat(request):
    return render(request, "home/habitat.html")


@cache_page(60 * 15)
def collecte_dechets(request):
    return render(request, "home/collecte-dechets.html")


@cache_page(60 * 15)
def encombrants(request):
    return render(request, "home/encombrants.html")


@cache_page(60 * 15)
def dechetteries(request):
    return render(request, "home/dechetteries.html")


@cache_page(60 * 15)
def maisons_sante(request):
    return render(request, "home/maisons-sante.html")


@cache_page(60 * 15)
def mutuelle(request):
    return render(request, "home/mutuelle.html")


@cache_page(60 * 15)
def contrat_local_sante(request):
    return render(request, "home/contrat-local-sante.html")


def plui(request):
    """Vue pour la page PLUi et le formulaire de modification."""
    return _handle_plui_form(request, "plui", "home/plui.html")


def _handle_plui_form(request, success_url_name, template_name):
    """
    Helper mutualisé pour les vues ``plui`` et ``documents_plui``.

    Args:
        request: requête Django.
        success_url_name: nom de l'URL de redirection en cas de succès/échec.
        template_name: chemin du template à rendre.

    Returns:
        HttpResponse (redirect ou render).
    """
    from .forms import PLUiModificationForm
    from .services import EmailService

    if request.method == "POST":
        form = PLUiModificationForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data

            if EmailService.send_plui_modification_request(form_data):
                messages.success(
                    request,
                    "Votre demande de modification PLUi a été envoyée avec succès. "
                    "Nous vous contacterons dans les plus brefs délais.",
                )
                logger.info("Demande PLUi envoyée pour %s", form_data.get("nom_prenom"))
            else:
                messages.error(
                    request,
                    "Une erreur est survenue lors de l'envoi de votre demande. "
                    "Veuillez réessayer ou nous contacter directement.",
                )
                logger.error(
                    "Échec envoi email PLUi pour %s", form_data.get("nom_prenom")
                )

            return redirect(success_url_name)

        # Formulaire invalide: regrouper les erreurs en un seul message Django
        error_messages = []
        for field, errors in form.errors.items():
            label = form.fields[field].label or field
            for error in errors:
                error_messages.append(f"{label}: {error}")
        if error_messages:
            messages.error(request, " ; ".join(error_messages))
        logger.warning("Formulaire PLUi invalide: %s", form.errors)
    else:
        form = PLUiModificationForm()

    context = {"form": form}
    return render(request, template_name, context)


@cache_page(60 * 15)
def projet_plui(request):
    return render(request, "home/projet-plui.html")


@cache_page(60 * 15)
def equipe(request):
    return render(request, "home/equipe.html")


@cache_page(60 * 60 * 24)
def mentions_legales(request):
    return render(request, "home/mentions-legales.html")


@cache_page(60 * 60 * 24)
def politique_confidentialite(request):
    return render(request, "home/politique-confidentialite.html")


@cache_page(60 * 60 * 24)
def cookies(request):
    return render(request, "home/cookies.html")


@cache_page(60 * 60 * 24)
def plan_du_site(request):
    return render(request, "home/plan-du-site.html")


@cache_page(60 * 60 * 24)
def accessibilite(request):
    return render(request, "home/accessibilite.html")


@cache_page(60 * 15)
def mediapass(request):
    return render(request, "home/mediapass.html")


@cache_page(60 * 15)
def ctg(request):
    """Vue pour la page Convention Territoriale Globale (CTG)."""
    return render(request, "home/ctg.html")


@cache_page(60 * 15)
def guide_eco_citoyen(request):
    """Vue pour la page Guide Pratique Éco-Citoyen."""
    return render(request, "home/guide-eco-citoyen.html")


@cache_page(60 * 15)
def clea(request):
    """Vue pour la page CLÉA (Contrat Local d'Éducation Artistique)."""
    return render(request, "home/clea.html")


def documents_plui(request):
    """Vue pour la page des documents PLUi et le formulaire de modification."""
    return _handle_plui_form(request, "documents_plui", "home/documents-plui.html")


@cache_page(60 * 15)
def modification_simplifiee_1(request):
    """Vue pour la page Modification Simplifiée n°1 du PLUi."""
    return render(request, "home/modification-simplifiee-1.html")


def test_email(request):
    """Vue de test pour l'envoi d'emails. **Désactivée en production.**"""
    if not settings.DEBUG:
        # SECURITE: route de test interdite en prod
        logger.warning(
            "Tentative d'accès à test_email par %s",
            get_client_ip(request),
        )
        return custom_handler404(request)

    from .services import EmailService

    test_data = {
        "nom_prenom": "Test Utilisateur",
        "adresse": "123 Rue de Test, 59000 Lille",
        "email": "test@example.com",
        "telephone": "03 27 12 34 56",
        "parcelles": "123, 124",
        "commune": "Féron",
        "demande": "Ceci est un test d'envoi d'email pour vérifier la configuration.",
    }

    try:
        success = EmailService.send_plui_modification_request(test_data)
        if success:
            messages.success(request, "Email de test envoyé avec succès !")
        else:
            messages.error(request, "Erreur lors de l'envoi de l'email de test.")
    except Exception as e:
        messages.error(request, f"Erreur: {e!s}")
        logger.error("test_email a echoue: %s", e, exc_info=True)

    return redirect("documents_plui")


@cache_page(60 * 15)
def dev_eco(request):
    return render(request, "home/dev-eco.html")


@cache_page(60 * 15)
def kit_logos(request):
    return render(request, "home/kit-logos.html")


def custom_handler404(request, exception=None):
    """Vue personnalisée pour la page 404."""
    response = render(request, "404.html", status=404)
    return response


def custom_handler500(request):
    """Vue personnalisée pour la page 500."""
    logger.error("Erreur 500 sur %s", request.path, exc_info=True)
    response = render(request, "500.html", status=500)
    return response


def telecharger_calendrier_verre(request):
    """
    Vue pour générer et télécharger le calendrier de collecte du verre en PDF.

    Sécurités appliquées :
    - Rate limit par IP (10/min)
    - Validation de la commune (whitelist dans ``city_data``)
    - Échappement XML de toutes les données utilisateur avant rendu PDF
      (mitigation XSS dans reportlab ``Paragraph``)
    - Métadonnées PDF (Title, Author, Subject, Language) pour accessibilité
    """
    from io import BytesIO

    # Imports reportlab localisés pour ne pas alourdir le process Django
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        Image,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    # Rate limiting: max 10 requêtes par minute par IP
    allowed, current, limit = rate_limit(
        request,
        action="pdf_download",
        max_calls=10,
        window=60,
    )
    if not allowed:
        client_ip = get_client_ip(request)
        logger.warning(
            "Rate limit PDF depasse: IP=%s hash=%s current=%d",
            client_ip,
            hash_ip(client_ip),
            current,
        )
        return HttpResponse(
            "Trop de requetes. Veuillez reessayer dans une minute.".encode("utf-8"),
            status=429,
            content_type="text/plain",
        )

    commune = request.GET.get("commune", "")
    rue = request.GET.get("rue", "")

    if not commune:
        return HttpResponse(
            b"Parametre 'commune' requis", status=400, content_type="text/plain"
        )

    if commune not in city_data:
        return HttpResponse(
            f"Commune '{commune}' non trouvee".encode("utf-8"),
            status=404,
            content_type="text/plain",
        )

    # Déterminer le jour de collecte
    jour_ordures, rue_trouvee = get_jour_ordures(commune, rue)

    # Récupérer les dates de verre
    dates_verre = get_dates_verre(commune, jour_ordures)

    if not dates_verre:
        return HttpResponse(
            f"Aucune date de collecte du verre trouvee pour {commune}".encode("utf-8"),
            status=404,
            content_type="text/plain",
        )

    # Créer le PDF en mémoire
    buffer = BytesIO()

    # Nom de fichier sécurisé via helper (reutilisable)
    safe_commune = normalize_filename(commune)
    if rue:
        safe_rue = normalize_filename(rue)
        filename = f"calendrier-verre-{safe_commune}-{safe_rue}.pdf"
    else:
        filename = f"calendrier-verre-{safe_commune}.pdf"

    # Créer le document PDF avec métadonnées d'accessibilité
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"Calendrier de collecte du verre - {commune}",
        author="Communaute de Communes Sud-Avesnois",
        subject="Calendrier annuel de collecte du verre",
        lang="fr-FR",
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=colors.HexColor("#006ab3"),
        spaceAfter=5,
        alignment=1,
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Heading2"],
        fontSize=10,
        textColor=colors.HexColor("#333333"),
        spaceAfter=10,
    )
    normal_style = styles["Normal"]
    normal_style.fontSize = 10

    elements = []

    # Logo (image decorative = vide explicite)
    try:
        logo_path = (
            settings.BASE_DIR
            / "static"
            / "img"
            / "Kits-Logos"
            / "PNG_Transparent"
            / "Logo_couleur.png"
        )
        if logo_path.exists():
            logo = Image(str(logo_path), width=6 * cm, height=3 * cm)
            elements.append(logo)
            elements.append(Spacer(1, 0.1 * cm))
    except Exception as e:
        logger.warning("Impossible de charger le logo: %s", e)

    # SECURITE: échapper les entrées utilisateur avant injection dans un
    # Paragraph reportlab (qui interprète le XML).
    safe_commune_escaped = xml_escape(commune)
    safe_rue_escaped = xml_escape(rue_trouvee) if rue_trouvee else ""
    safe_jour_ordures_escaped = xml_escape(jour_ordures) if jour_ordures else ""

    # Titre
    elements.append(
        Paragraph(
            f"Calendrier de collecte du verre de {safe_commune_escaped}",
            title_style,
        )
    )
    elements.append(Spacer(1, 0.1 * cm))

    # Informations de la rue
    if rue_trouvee:
        elements.append(
            Paragraph(f"<b>Rue :</b> {safe_rue_escaped}", subtitle_style)
        )

    # Jour de collecte du verre
    verre_info = city_data[commune]["verre"]
    if isinstance(verre_info, dict):
        if "jour" in verre_info:
            jour_verre = verre_info["jour"]
        elif jour_ordures and jour_ordures.lower() in verre_info:
            jour_verre = jour_ordures
        else:
            jour_verre = next(iter(verre_info.keys()))

        elements.append(
            Paragraph(
                f"<b>Collecte du verre :</b> le {xml_escape(jour_verre)}",
                normal_style,
            )
        )
        elements.append(Spacer(1, 0.1 * cm))

    # Tableau des dates
    elements.append(Paragraph("<b>Dates de collecte 2026-2027</b>", subtitle_style))
    elements.append(Spacer(1, 0.1 * cm))

    # Mapping des jours anglais vers français
    jours_fr = {
        "Monday": "Lundi",
        "Tuesday": "Mardi",
        "Wednesday": "Mercredi",
        "Thursday": "Jeudi",
        "Friday": "Vendredi",
        "Saturday": "Samedi",
        "Sunday": "Dimanche",
    }

    dates_2026 = []
    dates_2027 = []

    for date_str in dates_verre:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            jour_en = date_obj.strftime("%A")
            jour_semaine = jours_fr.get(jour_en, jour_en)
            date_formatee = date_obj.strftime("%d/%m/%Y")
            ligne = f"Le {jour_semaine.lower()} {date_formatee}"

            if date_obj.year == 2026:
                dates_2026.append(ligne)
            elif date_obj.year == 2027:
                dates_2027.append(ligne)
        except ValueError:
            continue

    # Préparer les données du tableau (2 colonnes : 2026 et 2027)
    table_data = [["2026", "2027"]]
    max_rows = max(len(dates_2026), len(dates_2027))

    for i in range(max_rows):
        row = [
            dates_2026[i] if i < len(dates_2026) else "",
            dates_2027[i] if i < len(dates_2027) else "",
        ]
        table_data.append(row)

    # Créer le tableau
    table = Table(table_data, colWidths=[8 * cm, 8 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#006ab3")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 10),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.lightgrey],
                ),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, 0.5 * cm))

    # Ajouter l'image Collect.png
    try:
        collect_image_path = settings.BASE_DIR / "static" / "img" / "Collect.png"
        if collect_image_path.exists():
            img = Image(str(collect_image_path), width=16 * cm, height=6 * cm)
            elements.append(img)
            elements.append(Spacer(1, 0.5 * cm))
    except Exception as e:
        logger.warning("Impossible de charger l'image Collect.png: %s", e)

    elements.append(Spacer(1, 0.5 * cm))

    # Footer avec contact
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.grey,
        alignment=1,
    )
    elements.append(
        Paragraph(
            "Communauté de Communes Sud-Avesnois<br/>"
            "2 Rue du Général Raymond Chomel - 59610 FOURMIES<br/>"
            "Tél : 03 27 60 65 24 | contact@cc-sudavesnois.fr",
            footer_style,
        )
    )

    # Générer le PDF
    doc.build(elements)

    # Créer la réponse HTTP avec le PDF
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Language"] = "fr"

    view_mode = request.GET.get("view", "")
    if view_mode == "1":
        response["Content-Disposition"] = f'inline; filename="{filename}"'
    else:
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response
