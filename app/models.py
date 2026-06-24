from django.db import models


class SingletonModel(models.Model):
    """
    Modèle abstrait pour implémenter un singleton Django sûr.

    - Empêche la création de plusieurs instances via une contrainte
      UniqueConstraint sur un champ sentinel.
    - Force `pk = 1` dans save() pour conserver la compat avec les
      références étrangères existantes (pk=1).
    - Expose la méthode de classe `load()` pour récupérer l'instance
      unique (la crée si nécessaire).
    - Permet la suppression normale via `delete()` (pour `clear()` ou
      suppression depuis les vues admin). La PK est libérée et pourra
      être recréée au prochain `save()`.
    """

    singleton = models.BooleanField(default=True, editable=False)

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["singleton"],
                name="%(app_label)s_%(class)s_singleton_unique",
            )
        ]

    def save(self, *args, **kwargs):
        # Garantit que la PK reste 1 (compat avec les FK et l'ORM)
        self.pk = 1
        self.singleton = True
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Récupère l'instance unique, en crée une vide si nécessaire.

        ATTENTION : si l'instance n'existe pas, une instance vide est créée
        en base. Pour une lecture seule qui ne doit pas créer, utiliser
        `cls.get_solo()`.
        """
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @classmethod
    def get_solo(cls):
        """Récupère l'instance unique, ou None si elle n'existe pas.

        Ne crée PAS d'instance vide. À utiliser dans les vues/templates
        qui ne doivent pas créer implicitement un record.
        """
        try:
            return cls.objects.get(pk=1)
        except cls.DoesNotExist:
            return None

    @classmethod
    def clear(cls):
        """Supprime l'instance unique (s'il y en a une)."""
        cls.objects.filter(pk=1).delete()

    @classmethod
    def update_or_create(cls, defaults=None, **kwargs):
        """Crée ou met à jour l'instance unique de manière atomique."""
        defaults = defaults or {}
        defaults.setdefault("pk", 1)
        return cls.objects.update_or_create(pk=1, defaults=defaults, **kwargs)
