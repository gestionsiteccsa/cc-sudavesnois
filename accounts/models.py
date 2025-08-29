from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Gestionnaire personnalisé pour le modèle
    utilisateur avec email comme identifiant
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Crée et enregistre un utilisateur avec
        l'email et le mot de passe donnés
        """
        if not email:
            raise ValueError(_("L'adresse email est obligatoire"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Crée et enregistre un superutilisateur avec l'email
        et le mot de passe donnés
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Le superutilisateur doit avoir is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Le superutilisateur doit avoir is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Modèle utilisateur personnalisé qui utilise l'email comme
    identifiant unique
    """

    email = models.EmailField(_("adresse email"), unique=True)
    username = models.CharField(_("nom d'utilisateur"), max_length=150, blank=True)
    is_staff = models.BooleanField(
        _("statut staff"),
        default=False,
        help_text=_(
            "Désigne si l'utilisateur peut se connecter au site " "d'administration."
        ),
    )
    is_active = models.BooleanField(
        _("actif"),
        default=True,
        help_text=_(
            "Désigne si l'utilisateur doit être traité comme actif. "
            "Décochez cette case plutôt que de supprimer des comptes."
        ),
    )
    date_joined = models.DateTimeField(_("date d'inscription"), default=timezone.now)
    last_login = models.DateTimeField(_("dernière connexion"), null=True, blank=True)

    # Ajout des related_name pour résoudre les conflits
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name=_("groupes"),
        blank=True,
        help_text=_(
            "Les groupes auxquels appartient cet utilisateur. "
            "Un utilisateur obtiendra toutes les permissions "
            "accordées à chacun de ses groupes."
        ),
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name=_("permissions utilisateur"),
        blank=True,
        help_text=_("Permissions spécifiques pour cet utilisateur."),
        related_name="custom_user_set",
        related_query_name="custom_user",
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("utilisateur")
        verbose_name_plural = _("utilisateurs")

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.username or self.email

    def get_short_name(self):
        return self.username or self.email.split("@")[0]
