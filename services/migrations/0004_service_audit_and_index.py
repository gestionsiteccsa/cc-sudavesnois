import datetime

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("services", "0003_alter_service_options_service_order"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=datetime.datetime(2026, 1, 1, 0, 0, 0),
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="service",
            name="updated_at",
            field=models.DateTimeField(
                auto_now=True, default=datetime.datetime(2026, 1, 1, 0, 0, 0)
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="service",
            name="order",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Position dans la liste (gérée automatiquement).",
                verbose_name="Ordre d'affichage",
            ),
        ),
        migrations.AddIndex(
            model_name="service",
            index=models.Index(
                fields=["order", "title"], name="service_order_title_idx"
            ),
        ),
    ]
