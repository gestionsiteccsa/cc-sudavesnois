from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe
import re


def validate_taille_fichier(value):
    max_upload_size = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
    if value.size > max_upload_size:
        raise ValidationError(
            "Le fichier dépasse la taille maximale autorisée (60 Mo)."
        )


class CategoriePartenaire(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    ordre = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    active = models.BooleanField(default=True, verbose_name="Actif")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = "Catégorie de partenaire"
        verbose_name_plural = "Catégories de partenaires"

    def __str__(self):
        return self.nom


class Partenaire(models.Model):
    TYPE_LIEN_CHOICES = [
        ('externe', 'Lien externe (URL)'),
        ('interne', 'Lien interne (page du site)'),
    ]

    COULEUR_FOND_CHOICES = [
        ('#f3f4f6', 'Gris très clair (par défaut)'),
        ('#ffffff', 'Blanc'),
        ('#e5e7eb', 'Gris clair'),
        ('#9ca3af', 'Gris'),
        ('#4b5563', 'Gris foncé'),
        ('#dbeafe', 'Bleu très clair'),
    ]

    # Liste des URLs internes disponibles (excluant les admin)
    LIENS_INTERNES_CHOICES = [
        # Pages principales
        ('home', 'Accueil'),
        ('presentation', 'Présentation'),
        ('equipe', 'Équipe'),
        
        # Thématiques
        ('mobilite', 'Mobilité'),
        ('habitat', 'Habitat'),
        ('dev_eco', 'Développement économique'),
        ('tourisme', 'Tourisme'),
        ('pnra', 'Parc Naturel Régional'),
        ('maisons_sante', 'Maisons de santé'),
        ('mutuelle', 'Mutuelle intercommunautaire'),
        ('contrat_local_sante', 'Contrat local santé'),
        ('mediapass', 'Médi@\'pass'),
        
        # Documents et informations
        ('plui', 'PLUi'),
        ('projet_plui', 'Projet PLUi'),
        ('documents_plui', 'Documents PLUi'),
        ('marches_publics', 'Marchés publics'),
        ('mentions_legales', 'Mentions légales'),
        ('politique_confidentialite', 'Politique de confidentialité'),
        ('cookies', 'Politique de cookies'),
        ('plan_du_site', 'Plan du site'),
        ('accessibilite', 'Accessibilité'),
        ('kit_logos', 'Kit de logos'),
        ('guide_eco_citoyen', 'Guide éco-citoyen'),
        
        # Collecte et déchets
        ('collecte_dechets', 'Collecte des déchets'),
        ('encombrants', 'Encombrants'),
        ('dechetteries', 'Déchèteries'),
        
        # Communes et institutions
        ('communes-membres:commune', 'Page commune (nécessite un slug)'),
        ('commissions:commissions', 'Commissions'),
        ('competences:competences', 'Compétences'),
        ('comptes_rendus:comptes_rendus', 'Comptes rendus'),
        ('bureau-communautaire:elus', 'Élus du bureau communautaire'),
        ('journal:journal_list', 'Journal'),
        ('partenaires:partenaires', 'Partenaires'),
        ('linktree:linktree', 'Liens utiles'),
    ]

    nom = models.CharField(max_length=200, verbose_name="Nom")
    categorie = models.ForeignKey(
        CategoriePartenaire,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Catégorie"
    )
    description = models.TextField(verbose_name="Description")
    
    # Gestion des liens
    type_lien = models.CharField(
        max_length=10,
        choices=TYPE_LIEN_CHOICES,
        default='externe',
        verbose_name="Type de lien"
    )
    site_web = models.URLField(blank=True, verbose_name="Site web (URL externe)")
    lien_interne = models.CharField(
        max_length=50,
        choices=LIENS_INTERNES_CHOICES,
        blank=True,
        verbose_name="Page interne"
    )
    
    logo = models.ImageField(
        upload_to="partenaires/logos/",
        blank=True,
        null=True,
        validators=[
            validate_taille_fichier,
            FileExtensionValidator(
                allowed_extensions=["png", "jpg", "jpeg", "webp", "svg"]
            ),
        ],
        verbose_name="Logo"
    )
    couleur_fond = models.CharField(
        max_length=7,
        choices=COULEUR_FOND_CHOICES,
        default='#f3f4f6',
        verbose_name="Couleur de fond du logo"
    )
    ordre = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    active = models.BooleanField(default=True, verbose_name="Actif")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['categorie__ordre', 'ordre', 'nom']
        verbose_name = "Partenaire"
        verbose_name_plural = "Partenaires"

    def __str__(self):
        return self.nom

    def get_logo_url(self):
        """Retourne l'URL du logo ou None si absent."""
        if self.logo:
            return self.logo.url
        return None

    def get_url(self):
        """Retourne l'URL du partenaire (externe ou interne)."""
        if self.type_lien == 'interne' and self.lien_interne:
            try:
                return reverse(self.lien_interne)
            except Exception:
                return None
        elif self.type_lien == 'externe' and self.site_web:
            return self.site_web
        return None

    def is_external_link(self):
        """Retourne True si le lien est externe."""
        return self.type_lien == 'externe' and bool(self.site_web)

    def delete_logo_file(self):
        """Supprime le fichier logo du système de fichiers."""
        if self.logo:
            try:
                import os
                if os.path.exists(self.logo.path):
                    os.remove(self.logo.path)
            except (OSError, ValueError):
                pass

    def save(self, *args, **kwargs):
        """Sauvegarde avec gestion du remplacement de logo."""
        if self.pk:
            try:
                old_instance = Partenaire.objects.get(pk=self.pk)
                if old_instance.logo and self.logo != old_instance.logo:
                    old_instance.delete_logo_file()
            except Partenaire.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Supprime l'instance et son logo associé."""
        self.delete_logo_file()
        super().delete(*args, **kwargs)

    def clean(self):
        """Validation des champs."""
        super().clean()
        if self.type_lien == 'externe' and not self.site_web:
            raise ValidationError(
                {"site_web": "Le site web est obligatoire pour un lien externe."}
            )
        if self.type_lien == 'interne' and not self.lien_interne:
            raise ValidationError(
                {"lien_interne": "La page interne est obligatoire pour un lien interne."}
            )

    def get_description_html(self):
        """Convertit la description markdown en HTML."""
        if not self.description:
            return ""
        
        try:
            import markdown
            # Configuration markdown : activation des liens uniquement
            md = markdown.Markdown(extensions=['nl2br'])
            html = md.convert(str(self.description))
            
            # Ajouter target="_blank" et rel="noopener noreferrer" aux liens externes
            html = re.sub(
                r'<a href="(http[^"]+)"',
                r'<a href="\1" target="_blank" rel="noopener noreferrer"',
                html
            )
            
            return mark_safe(html)
        except ImportError:
            # Fallback si markdown n'est pas disponible
            return mark_safe(str(self.description).replace('\n', '<br>'))
