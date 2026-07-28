import json

from django.core.management.base import BaseCommand

from analytics.analytics_data import ANALYTICS_DIR
from analytics.geo import is_available as geo_available
from analytics.geo import lookup as geo_lookup


class Command(BaseCommand):
    help = "Ajoute la geolocalisation aux entrees existantes sans geo"

    def handle(self, *args, **options):
        if not geo_available():
            self.stdout.write(
                self.style.WARNING(
                    "Base GeoIP indisponible. Lancez d'abord : "
                    "python manage.py update_geoip_db --mirror"
                )
            )
            return

        fichiers = sorted(ANALYTICS_DIR.glob("*.jsonl"))
        total_modifie = 0
        total_vide = 0

        for fpath in fichiers:
            lignes: list[str] = []
            modifie = False

            with open(fpath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        ip = entry.get("ip", "")
                        geo = entry.get("geo")
                        if ip and not geo:
                            nouveau_geo = geo_lookup(ip)
                            if nouveau_geo:
                                entry["geo"] = nouveau_geo
                                modifie = True
                                total_modifie += 1
                            else:
                                total_vide += 1
                        lignes.append(json.dumps(entry, ensure_ascii=False))
                    except json.JSONDecodeError:
                        lignes.append(line)

            if modifie:
                with open(fpath, "w", encoding="utf-8") as f:
                    for ligne in lignes:
                        f.write(ligne + "\n")
                self.stdout.write(f"  mis a jour : {fpath.name}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Termine : {total_modifie} entree(s) geolocalisee(s), "
                f"{total_vide} sans resultat (IP privee ou inconnue)"
            )
        )
