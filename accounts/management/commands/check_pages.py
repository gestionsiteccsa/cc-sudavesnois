import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse


class Command(BaseCommand):
    help = "Vérifie le statut HTTP de toutes les pages du site"

    def add_arguments(self, parser):
        parser.add_argument(
            "--all", action="store_true", help="Affiche toutes les pages (y compris OK)"
        )
        parser.add_argument(
            "--timeout", type=int, default=8, help="Timeout par requête en secondes (défaut: 8)"
        )
        parser.add_argument(
            "--workers", type=int, default=10, help="Nombre de threads simultanés (défaut: 10)"
        )
        parser.add_argument(
            "--base-url",
            help="URL de base du site (ex: https://cc-sudavesnois.fr). "
                 "Par défaut déduit de ALLOWED_HOSTS.",
        )

    def handle(self, *args, **options):
        base_url = self._resolve_base_url(options["base_url"])
        timeout = options["timeout"]
        workers = options["workers"]
        show_all = options["all"]
        pages = self._get_pages()

        self.stdout.write(f"\nVérification de {len(pages)} pages sur {base_url}\n")

        errors = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {}
            for name, path in pages:
                url = f"{base_url}{path}"
                futures[executor.submit(self._check_page, url, name, timeout)] = (name, path)

            for future in as_completed(futures):
                result = future.result()
                errors.append(result)

                if result["status"] != "ok" or show_all:
                    self._print_result(result, base_url)

        errors.sort(key=lambda r: r["path"])

        total = len(errors)
        ok_count = sum(1 for r in errors if r["status"] == "ok")
        warning_count = sum(1 for r in errors if r["status"] == "warning")
        error_count = sum(1 for r in errors if r["status"] == "error")

        self.stdout.write("\n" + "=" * 50)
        label = f" {total} pages | {ok_count} OK | {warning_count} redirections | {error_count} erreurs "
        if error_count:
            self.stdout.write(self.style.ERROR(label))
        elif warning_count:
            self.stdout.write(self.style.WARNING(label))
        else:
            self.stdout.write(self.style.SUCCESS(label))
        self.stdout.write("=" * 50)

    def _resolve_base_url(self, provided):
        if provided:
            return provided.rstrip("/")
        for host in settings.ALLOWED_HOSTS:
            host = host.strip()
            if host and host != ".":
                scheme = "http" if "localhost" in host or "127.0.0.1" in host else "https"
                return f"{scheme}://{host}"
        return "http://localhost:8000"

    def _get_pages(self):
        pages = []

        static_names = [
            ("Accueil", "home"),
            ("Élus", "bureau-communautaire:elus"),
            ("Conseil communautaire", "conseil_communautaire:conseil"),
            ("Comptes rendus", "comptes_rendus:comptes_rendus"),
            ("Procès-verbaux", "comptes_rendus:proces_verbaux"),
            ("Présentation", "presentation"),
            ("Compétences", "competences:competences"),
            ("Journal", "journal:journal"),
            ("Commissions", "commissions:commissions"),
            ("Marchés publics", "marches_publics"),
            ("Mobilité", "mobilite"),
            ("Habitat", "habitat"),
            ("Collecte des déchets", "collecte_dechets"),
            ("Encombrants", "encombrants"),
            ("Déchetteries", "dechetteries"),
            ("Maisons de santé", "maisons_sante"),
            ("Mutuelle", "mutuelle"),
            ("Contrat local de santé", "contrat_local_sante"),
            ("PLUi", "plui"),
            ("Guide des services", "equipe"),
            ("Semestriels", "semestriels:semestriel"),
            ("Rapports d'activité", "rapports_activite:rapports_activite"),
            ("Mentions légales", "mentions_legales"),
            ("Politique de confidentialité", "politique_confidentialite"),
            ("Politique des cookies", "cookies"),
            ("Plan du site", "plan_du_site"),
            ("Accessibilité", "accessibilite"),
            ("Médi@'pass", "mediapass"),
            ("CTG", "ctg"),
            ("Guide éco-citoyen", "guide_eco_citoyen"),
            ("CLÉA", "clea"),
            ("Développement économique", "dev_eco"),
            ("Kit logos", "kit_logos"),
            ("Liens utiles", "linktree:linktree_page"),
            ("Communes membres", "communes-membres:list"),
            ("Partenaires", "partenaires:partenaires"),
        ]

        for name, url_name in static_names:
            try:
                path = reverse(url_name)
                pages.append((name, path))
            except Exception:
                pass

        try:
            from conseil_communautaire.models import ConseilVille

            for ville in ConseilVille.objects.all():
                try:
                    path = reverse("communes-membres:commune", kwargs={"slug": ville.slug})
                    pages.append((f"Commune : {ville.city_name}", path))
                except Exception:
                    pass
        except Exception:
            pass

        try:
            from journal.models import Journal

            for journal in Journal.objects.all():
                try:
                    path = reverse("journal:journal_detail", kwargs={"id": journal.id})
                    pages.append((f"Journal : {journal.title}", path))
                except Exception:
                    pass
        except Exception:
            pass

        return pages

    def _check_page(self, url, name, timeout):
        start = time.time()
        try:
            resp = requests.get(url, timeout=timeout)
            code = resp.status_code
            elapsed = round(time.time() - start, 2)
        except requests.exceptions.SSLError:
            try:
                resp = requests.get(url, timeout=timeout, verify=False)
                code = resp.status_code
                elapsed = round(time.time() - start, 2)
            except requests.exceptions.RequestException as e:
                return {
                    "name": name, "path": url, "status_code": None,
                    "status": "error", "response_time": round(time.time() - start, 2),
                    "error": str(e),
                }
        except requests.exceptions.RequestException as e:
            return {
                "name": name, "path": url, "status_code": None,
                "status": "error", "response_time": round(time.time() - start, 2),
                "error": str(e),
            }
        except Exception as e:
            return {
                "name": name, "path": url, "status_code": None,
                "status": "error", "response_time": round(time.time() - start, 2),
                "error": str(e),
            }

        if code == 200:
            status = "ok"
        elif 300 <= code < 400:
            status = "warning"
        else:
            status = "error"

        return {
            "name": name, "path": url,
            "status_code": code, "status": status,
            "response_time": elapsed, "error": None,
        }

    def _print_result(self, result, base_url):
        name = result["name"]
        path = result["path"].replace(base_url, "") if result["path"] else "?"
        code = result["status_code"] or "---"
        elapsed = result.get("response_time", "?")

        if result["status"] == "ok":
            style = self.style.SUCCESS
            symbol = "[OK]"
        elif result["status"] == "warning":
            style = self.style.WARNING
            symbol = "[>>]"
        else:
            style = self.style.ERROR
            symbol = "[!!]"

        extra = f"  ({elapsed}s)" if elapsed else ""
        if result.get("error"):
            line = f"  {symbol} {name:35s}  {path}  {code}  {result['error']}"
        else:
            line = f"  {symbol} {name:35s}  {code}  {extra}"

        self.stdout.write(line, style_func=style)
