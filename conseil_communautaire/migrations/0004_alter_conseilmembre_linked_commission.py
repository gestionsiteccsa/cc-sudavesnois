# Generated manually for FK -> M2M migration

from django.db import migrations, models


def migrate_fk_to_m2m(apps, schema_editor):
    """Migrate existing ForeignKey data to ManyToManyField."""
    ConseilMembre = apps.get_model('conseil_communautaire', 'ConseilMembre')
    Commission = apps.get_model('commissions', 'Commission')
    
    # For each member with a linked commission, add it to the M2M relation
    for membre in ConseilMembre.objects.all():
        # The old FK data is accessible via the temporary column
        # We need to check if there's an old linked_commission_id
        old_commission_id = getattr(membre, '_old_linked_commission_id', None)
        if old_commission_id:
            try:
                commission = Commission.objects.get(id=old_commission_id)
                membre.linked_commission.add(commission)
            except Commission.DoesNotExist:
                pass


class Migration(migrations.Migration):
    dependencies = [
        ("conseil_communautaire", "0003_alter_conseilmembre_unique_together"),
        ("commissions", "0002_alter_commission_icon"),
    ]

    operations = [
        # Step 1: Rename old FK column to preserve data
        migrations.RenameField(
            model_name='conseilmembre',
            old_name='linked_commission',
            new_name='_old_linked_commission',
        ),
        # Step 2: Add new ManyToManyField
        migrations.AddField(
            model_name='conseilmembre',
            name='linked_commission',
            field=models.ManyToManyField(
                blank=True,
                related_name='membres',
                to='commissions.commission',
                help_text="Sélectionnez jusqu'à 5 commissions pour ce membre.",
            ),
        ),
        # Step 3: Migrate data
        migrations.RunPython(migrate_fk_to_m2m, migrations.RunPython.noop),
        # Step 4: Remove old FK field
        migrations.RemoveField(
            model_name='conseilmembre',
            name='_old_linked_commission',
        ),
    ]
