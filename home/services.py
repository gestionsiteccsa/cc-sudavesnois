"""
Services pour la gestion des emails et autres fonctionnalités métier.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

# Destinataires par défaut (surchargeables via settings/env)
DEFAULT_PLUI_TO_EMAILS = ["contact@cc-sudavesnois.fr"]
DEFAULT_PLUI_BCC_EMAILS: List[str] = []  # à définir en settings/env si besoin


class EmailService:
    """Service pour la gestion des emails."""

    @staticmethod
    def send_plui_modification_request(
        form_data: Dict[str, Any],
        to_emails: Optional[Union[str, List[str]]] = None,
        bcc_emails: Optional[Union[str, List[str]]] = None,
    ) -> bool:
        """
        Envoie un email de demande de modification PLUi.

        Args:
            form_data: Données du formulaire (dict cleaned_data).
            to_emails: Liste des destinataires principaux (str ou list).
                Défaut : ``settings.PLUI_TO_EMAILS`` ou ``DEFAULT_PLUI_TO_EMAILS``.
            bcc_emails: Liste des copies cachées (str ou list).
                Défaut : ``settings.PLUI_BCC_EMAILS`` ou ``DEFAULT_PLUI_BCC_EMAILS``.

        Returns:
            True si l'envoi a réussi, False sinon.
        """
        if to_emails is None:
            to_emails = getattr(settings, "PLUI_TO_EMAILS", DEFAULT_PLUI_TO_EMAILS)
        elif isinstance(to_emails, str):
            to_emails = [to_emails]

        if bcc_emails is None:
            bcc_emails = getattr(settings, "PLUI_BCC_EMAILS", DEFAULT_PLUI_BCC_EMAILS)
        elif isinstance(bcc_emails, str):
            bcc_emails = [bcc_emails]

        try:
            context = {
                "nom_prenom": form_data.get("nom_prenom", ""),
                "adresse": form_data.get("adresse", ""),
                "email": form_data.get("email", ""),
                "telephone": form_data.get("telephone", ""),
                "parcelles": form_data.get("parcelles", ""),
                "commune": form_data.get("commune", ""),
                "demande": form_data.get("demande", ""),
                "date_demande": datetime.now().strftime("%d/%m/%Y à %H:%M"),
            }

            html_content = render_to_string("home/email_plui_demande.html", context)
            text_content = EmailService._generate_text_content(context)

            subject = (
                f"Demande de modification PLUi - "
                f"{context['nom_prenom']} ({context['commune']})"
            )
            from_email = settings.DEFAULT_FROM_EMAIL
            reply_to = [context["email"]] if context["email"] else None
            msg = EmailMultiAlternatives(
                subject,
                text_content,
                from_email,
                to_emails,
                bcc=bcc_emails,
                reply_to=reply_to,
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            logger.info(
                "Email PLUi envoyé avec succès pour %s (%s) vers %s (cci: %s)",
                context["nom_prenom"],
                context["commune"],
                ", ".join(to_emails) if to_emails else "(aucun)",
                ", ".join(bcc_emails) if bcc_emails else "(aucun)",
            )
            return True

        except Exception as e:
            # Catch large: smtplib/SMTPException, socket.gaierror, ConnectionError...
            logger.error(
                "Erreur lors de l'envoi de l'email PLUi pour %s: %s",
                form_data.get("nom_prenom", "N/A"),
                e,
                exc_info=True,
            )
            return False

    @staticmethod
    def _generate_text_content(context: Dict[str, Any]) -> str:
        """Génère le contenu texte de l'email."""
        return f"""
NOUVELLE DEMANDE DE MODIFICATION PLUi
Reçue le {context["date_demande"]}

DEMANDEUR:
- Nom et Prénom: {context["nom_prenom"]}
- Adresse: {context["adresse"]}
- Email: {context["email"]}
- Téléphone: {context["telephone"]}

PARCELLES CONCERNÉES:
- Numéros de parcelles: {context["parcelles"]}
- Commune: {context["commune"]}

DEMANDE:
{context["demande"]}

---
Cette demande a été envoyée via le formulaire en ligne du site
de la Communauté de Communes Sud-Avesnois.
Merci de traiter cette demande dans les plus brefs délais.
        """

