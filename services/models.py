from django.db import models


class Service(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(verbose_name="Description")
    icon = models.TextField()
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return f"{self.title} - {self.content}"
