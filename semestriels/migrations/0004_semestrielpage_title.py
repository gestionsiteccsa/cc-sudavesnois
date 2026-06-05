from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("semestriels", "0003_alter_semestrielpage_picture"),
    ]

    operations = [
        migrations.AddField(
            model_name="semestrielpage",
            name="title",
            field=models.CharField(
                default="Calendrier semestriel",
                max_length=200,
                verbose_name="Titre",
            ),
        ),
    ]
