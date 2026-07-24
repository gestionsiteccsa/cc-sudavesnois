import tarfile
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import requests

GEOIP_DIR = settings.BASE_DIR / "geoip"
GEOIP_DB = GEOIP_DIR / "GeoLite2-City.mmdb"
DOWNLOAD_URL = (
    "https://download.maxmind.com/app/geoip_download"
    "?edition_id=GeoLite2-City&license_key={key}&suffix=tar.gz"
)
MIRROR_URL = "https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb"


class Command(BaseCommand):
    help = "Télécharge la base GeoLite2-City pour la géolocalisation IP"

    def add_arguments(self, parser):
        parser.add_argument(
            "--license-key",
            help=(
                "Clé de licence MaxMind (gratuite sur "
                "https://www.maxmind.com/en/geolite2/signup)"
            ),
        )
        parser.add_argument(
            "--mirror",
            action="store_true",
            help="Utiliser le miroir GitHub (pas de clé requise)",
        )

    def handle(self, *args, **options):
        GEOIP_DIR.mkdir(parents=True, exist_ok=True)

        if options.get("mirror"):
            url = MIRROR_URL
            self.stdout.write("Téléchargement depuis le miroir GitHub...")
        elif options.get("license_key"):
            url = DOWNLOAD_URL.format(key=options["license_key"])
            self.stdout.write("Téléchargement depuis MaxMind...")
        else:
            raise CommandError(
                "Utilisez --mirror ou --license-key LICENSE_KEY\n"
                "Obtenez une clé gratuite sur "
                "https://www.maxmind.com/en/geolite2/signup"
            )

        try:
            resp = requests.get(url, stream=True, timeout=120)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise CommandError(f"Échec du téléchargement : {e}")

        if options.get("mirror"):
            with open(GEOIP_DB, "wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
            self.stdout.write(self.style.SUCCESS(f"Base téléchargée : {GEOIP_DB}"))
        else:
            with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        tmp.write(chunk)
                tmp_path = tmp.name

            try:
                with tarfile.open(tmp_path, "r:gz") as tar:
                    mmdb_member = None
                    for member in tar.getmembers():
                        if member.name.endswith(".mmdb"):
                            mmdb_member = member
                            break
                    if mmdb_member is None:
                        raise CommandError("Aucun fichier .mmdb trouvé dans l'archive")
                    src = tar.extractfile(mmdb_member)
                    if src is None:
                        raise CommandError("Impossible d'extraire la base")
                    with open(GEOIP_DB, "wb") as f:
                        f.write(src.read())
                self.stdout.write(self.style.SUCCESS(f"Base téléchargée : {GEOIP_DB}"))
            finally:
                Path(tmp_path).unlink(missing_ok=True)

        size = GEOIP_DB.stat().st_size
        self.stdout.write(f"Taille : {size / 1024 / 1024:.1f} Mo")
