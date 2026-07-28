import sys
from datetime import date, timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from analytics.analytics_data import load_range


class Command(BaseCommand):
    help = "Envoie un rapport de statistiques par email"

    def add_arguments(self, parser):
        parser.add_argument(
            "--period",
            choices=["weekly", "monthly"],
            default="weekly",
            help="Periode du rapport (weekly=7j, monthly=30j)",
        )
        parser.add_argument(
            "--email",
            default="",
            help="Adresse email du destinataire",
        )

    def handle(self, *args, **options):
        period = options["period"]
        email_to = options["email"]

        if not email_to:
            email_to = getattr(settings, "ADMIN_EMAIL", "")
        if not email_to:
            self.stderr.write(
                "Aucune adresse email. Utilisez --email ou definissez "
                "ADMIN_EMAIL dans settings.py"
            )
            sys.exit(1)

        days = 7 if period == "weekly" else 30
        today = date.today()
        start = today - timedelta(days=days - 1)
        end = today

        raw = load_range(start, end)
        total = sum(len(entries) for entries in raw.values())
        unique_ips = len(
            {
                e.get("ip_hash")
                for entries in raw.values()
                for e in entries
                if e.get("ip_hash")
            }
        )

        pages: dict[str, int] = {}
        for entries in raw.values():
            for e in entries:
                u = e.get("url", "/")
                pages[u] = pages.get(u, 0) + 1
        top_pages = sorted(pages.items(), key=lambda x: -x[1])[:5]

        html_body = render_to_string(
            "analytics/email_report.html",
            {
                "period_days": days,
                "start": start,
                "end": end,
                "total_views": total,
                "unique_ips": unique_ips,
                "top_pages": [{"url": u, "count": c} for u, c in top_pages],
            },
        )

        try:
            send_mail(
                subject=(
                    f"[CCSA] Rapport statistiques ({period}) — "
                    f"{start.isoformat()} au {end.isoformat()}"
                ),
                message="",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_to],
                html_message=html_body,
                fail_silently=False,
            )
            self.stdout.write(
                f"Rapport {period} envoye a {email_to} "
                f"({total} vues, {unique_ips} IP uniques)"
            )
        except Exception as exc:
            self.stderr.write(f"Erreur d'envoi : {exc}")
            sys.exit(1)
