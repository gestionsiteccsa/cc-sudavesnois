import json

from django.conf import settings
from django.core.management.base import BaseCommand

ANALYTICS_DIR = settings.BASE_DIR / "analytics_data"


class Command(BaseCommand):
    help = "Supprime toutes les entrees contenant une adresse IP donnee"

    def add_arguments(self, parser):
        parser.add_argument("ip", help="Adresse IP a supprimer (ex: 192.168.1.42)")

    def handle(self, *args, **options):
        target_ip = options["ip"]
        fichiers = sorted(ANALYTICS_DIR.glob("*.jsonl"))
        total_supprime = 0
        fichiers_modifies = 0

        for fpath in fichiers:
            lignes_conservees = []
            with open(fpath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if entry.get("ip") == target_ip:
                            total_supprime += 1
                        else:
                            lignes_conservees.append(line)
                    except json.JSONDecodeError:
                        lignes_conservees.append(line)

            if len(lignes_conservees) != sum(
                1 for _ in open(fpath, encoding="utf-8") if _.strip()
            ):
                with open(fpath, "w", encoding="utf-8") as f:
                    for ligne in lignes_conservees:
                        f.write(ligne + "\n")
                fichiers_modifies += 1

        if total_supprime == 0:
            self.stdout.write(
                self.style.WARNING(f"Aucune entree trouvee pour l'IP {target_ip}")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"{total_supprime} entree(s) supprimee(s) "
                    f"dans {fichiers_modifies} fichier(s) pour {target_ip}"
                )
            )
