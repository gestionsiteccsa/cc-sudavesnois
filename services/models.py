from django.db import models


class Service(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(verbose_name="Description")
    icon = models.TextField()

    def __str__(self):
        return f"{self.title} - {self.content}"
