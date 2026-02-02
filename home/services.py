"""
Services pour la gestion des emails et autres fonctionnalités métier.
"""
import logging
from datetime import datetime
from typing import Dict, Any

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class EmailService:
    """Service pour la gestion des emails."""

    @staticmethod
    def send_plui_modification_request(
        form_data: Dict[str, Any],
        recipient_email: str = 'j.brechoire@cc-sudavesnois.fr'
    ) -> bool:
        """
        Envoie un email de demande de modification PLUi.

        Args:
            form_data: Données du formulaire
            recipient_email: Email du destinataire

        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        try:
            # Préparation du contexte
            context = {
                'nom_prenom': form_data.get('nom_prenom', ''),
                'adresse': form_data.get('adresse', ''),
                'email': form_data.get('email', ''),
                'telephone': form_data.get('telephone', ''),
                'parcelles': form_data.get('parcelles', ''),
                'commune': form_data.get('commune', ''),
                'demande': form_data.get('demande', ''),
                'date_demande': datetime.now().strftime("%d/%m/%Y à %H:%M"),
            }

            # Rendu du template HTML
            html_content = render_to_string(
                'home/email_plui_demande.html', context
            )

            # Contenu texte de l'email
            text_content = EmailService._generate_text_content(context)

            # Création et envoi de l'email
            subject = (
                f"Demande de modification PLUi - "
                f"{context['nom_prenom']} ({context['commune']})"
            )
            from_email = context['email']
            to_email = [recipient_email]

            msg = EmailMultiAlternatives(
                subject, text_content, from_email, to_email
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            logger.info(
                "Email PLUi envoyé avec succès pour %s (%s) vers %s",
                context['nom_prenom'],
                context['commune'],
                recipient_email
            )
            return True

        except (OSError, ValueError, RuntimeError) as e:
            logger.error(
                "Erreur lors de l'envoi de l'email PLUi pour %s: %s",
                form_data.get('nom_prenom', 'N/A'),
                str(e)
            )
            return False

    @staticmethod
    def _generate_text_content(context: Dict[str, Any]) -> str:
        """Génère le contenu texte de l'email."""
        return f"""
NOUVELLE DEMANDE DE MODIFICATION PLUi
Reçue le {context['date_demande']}

DEMANDEUR:
- Nom et Prénom: {context['nom_prenom']}
- Adresse: {context['adresse']}
- Email: {context['email']}
- Téléphone: {context['telephone']}

PARCELLES CONCERNÉES:
- Numéros de parcelles: {context['parcelles']}
- Commune: {context['commune']}

DEMANDE:
{context['demande']}

---
Cette demande a été envoyée via le formulaire en ligne du site
de la Communauté de Communes Sud-Avesnois.
Merci de traiter cette demande dans les plus brefs délais.
        """


class PLUiService:
    """Service pour la gestion des demandes PLUi."""

    @staticmethod
    def validate_form_data(form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide les données du formulaire PLUi.

        Args:
            form_data: Données du formulaire

        Returns:
            Dict contenant les erreurs de validation
        """
        errors = {}

        # Validation des champs obligatoires
        required_fields = [
            'nom_prenom', 'adresse', 'email', 'telephone',
            'parcelles', 'commune', 'demande'
        ]

        for field in required_fields:
            if not form_data.get(field, '').strip():
                errors[field] = f'Le champ {field} est obligatoire.'

        # Validation spécifique de l'email
        email = form_data.get('email', '')
        if email and '@' not in email:
            errors['email'] = 'Veuillez saisir une adresse email valide.'

        # Validation de la longueur de la demande
        demande = form_data.get('demande', '')
        if demande and len(demande.strip()) < 10:
            errors['demande'] = 'La description doit contenir au moins 10 caractères.'

        return errors
