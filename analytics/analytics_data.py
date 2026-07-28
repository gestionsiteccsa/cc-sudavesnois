import json
import logging
import os
from datetime import date, datetime, timedelta
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

ANALYTICS_DIR = settings.BASE_DIR / "analytics_data"
RETENTION_DAYS = 365
BOT_URL_PREFIXES = frozenset(
    {
        "/wp-",
        "/wordpress",
        "/xmlrpc",
        "/wp-login",
        "/wp-admin",
        "/wp-content",
        "/wp-includes",
        "/wp-json",
    }
)


def is_bot_url(url: str) -> bool:
    for prefix in BOT_URL_PREFIXES:
        if url.startswith(prefix):
            return True
    return False


def ensure_dir():
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    purge_old_data()


def purge_old_data():
    limite = date.today() - timedelta(days=RETENTION_DAYS)
    for f in sorted(ANALYTICS_DIR.glob("*.json*")):
        if ".summary" in f.stem:
            continue
        try:
            d = date.fromisoformat(f.stem)
            if d < limite:
                f.unlink(missing_ok=True)
        except (ValueError, OSError):
            pass


def count_recent_ips(minutes: int = 15) -> int:
    """Nombre d'IP uniques ayant visité le site dans les N dernières minutes."""
    depuis = (datetime.now() - timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%S")
    path = _today_path()
    if not path.exists():
        return 0
    ips: set[str] = set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                    if e.get("timestamp", "") >= depuis:
                        ip = e.get("ip", "")
                        if ip:
                            ips.add(ip)
                except json.JSONDecodeError:
                    continue
    except OSError:
        pass
    return len(ips)


def _today_path() -> Path:
    return ANALYTICS_DIR / f"{date.today().isoformat()}.jsonl"


def append(entry: dict):
    ensure_dir()
    path = _today_path()
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        logger.error("Erreur écriture analytics: %s", e)


def _load_entries(d: date) -> list[dict]:
    path = ANALYTICS_DIR / f"{d.isoformat()}.jsonl"
    if path.exists():
        entries: list[dict] = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except OSError as e:
            logger.error("Erreur lecture analytics: %s", e)
        return entries
    legacy_path = ANALYTICS_DIR / f"{d.isoformat()}.json"
    if legacy_path.exists():
        try:
            with open(legacy_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except (OSError, json.JSONDecodeError) as e:
            logger.error("Erreur lecture analytics (legacy): %s", e)
    return []


def _compute_summary(entries: list[dict]) -> dict | None:
    if not entries:
        return None

    total = len(entries)
    sessions = len({e.get("session_key") for e in entries if e.get("session_key")})
    ip_hashes = len({e.get("ip_hash") for e in entries if e.get("ip_hash")})
    visitors = len({e.get("visitor_id") for e in entries if e.get("visitor_id")})

    pages: dict[str, int] = {}
    browsers: dict[str, int] = {}
    oss: dict[str, int] = {}
    device_types: dict[str, int] = {}
    languages: dict[str, int] = {}
    referrers: dict[str, int] = {}
    cities: dict[str, int] = {}
    regions: dict[str, int] = {}
    countries: dict[str, int] = {}

    for e in entries:
        url = e.get("url", "/")
        pages[url] = pages.get(url, 0) + 1
        device = e.get("device", {})
        br = device.get("browser", "Inconnu")
        browsers[br] = browsers.get(br, 0) + 1
        os_name = device.get("os", "Inconnu")
        oss[os_name] = oss.get(os_name, 0) + 1
        dt = device.get("type", "desktop")
        device_types[dt] = device_types.get(dt, 0) + 1
        lang = e.get("language", "")
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
        ref = e.get("referrer", "")
        if ref:
            domain = ref.split("/")[2] if "//" in ref else ref
            referrers[domain] = referrers.get(domain, 0) + 1
        geo = e.get("geo") or {}
        city = geo.get("city")
        if city:
            cities[city] = cities.get(city, 0) + 1
        region = geo.get("region")
        if region:
            regions[region] = regions.get(region, 0) + 1
        country = geo.get("country")
        if country:
            countries[country] = countries.get(country, 0) + 1

    return {
        "total": total,
        "unique_sessions": sessions,
        "unique_ips": ip_hashes,
        "unique_visitors": visitors,
        "top_pages": [
            {"url": u, "count": c}
            for u, c in sorted(pages.items(), key=lambda x: -x[1])[:20]
        ],
        "browsers": dict(sorted(browsers.items(), key=lambda x: -x[1])[:10]),
        "os": dict(sorted(oss.items(), key=lambda x: -x[1])[:10]),
        "device_types": dict(device_types),
        "languages": dict(languages),
        "referrers": dict(sorted(referrers.items(), key=lambda x: -x[1])[:10]),
        "geo": {
            "cities": [
                {"name": n, "count": c}
                for n, c in sorted(cities.items(), key=lambda x: -x[1])[:10]
            ],
            "regions": [
                {"name": n, "count": c}
                for n, c in sorted(regions.items(), key=lambda x: -x[1])[:10]
            ],
            "countries": [
                {"code": n, "count": c}
                for n, c in sorted(countries.items(), key=lambda x: -x[1])[:10]
            ],
        },
    }


def load_day(d: date) -> tuple[list[dict], dict | None]:
    entries = _load_entries(d)
    summary = _compute_summary(entries)
    return entries, summary


def load_range(start: date, end: date) -> dict:
    data: dict[str, list[dict]] = {}
    d = start
    while d <= end:
        entries = _load_entries(d)
        if entries:
            data[d.isoformat()] = entries
        d += timedelta(days=1)
    return data


def list_available_dates() -> list[str]:
    ensure_dir()
    files = sorted(ANALYTICS_DIR.glob("*.json*"))
    seen: set[str] = set()
    dates: list[str] = []
    for f in files:
        if ".summary" in f.stem:
            continue
        stem = f.stem
        if stem not in seen:
            seen.add(stem)
            dates.append(stem)
    dates.sort(reverse=True)
    return dates


def run_diagnostics() -> dict:
    checks: list[dict] = []

    checks.append(
        {
            "label": "Dossier analytics_data",
            "status": "ok" if ANALYTICS_DIR.exists() else "error",
            "detail": str(ANALYTICS_DIR)
            if ANALYTICS_DIR.exists()
            else f"Introuvable : {ANALYTICS_DIR}",
        }
    )
    if ANALYTICS_DIR.exists():
        writable = os.access(str(ANALYTICS_DIR), os.W_OK)
        checks.append(
            {
                "label": "Dossier accessible en ecriture",
                "status": "ok" if writable else "error",
                "detail": "",
            }
        )

    files = sorted(ANALYTICS_DIR.glob("*.json*"))
    data_files = [f for f in files if ".summary" not in f.stem]
    names = ", ".join(f.name for f in data_files[:10])
    if data_files:
        detail = f"{len(data_files)} fichier(s) : {names}"
        if len(data_files) > 10:
            detail += "..."
    else:
        detail = "Aucun fichier de donnees"
    checks.append(
        {
            "label": "Fichiers de donnees trouves",
            "status": "ok" if data_files else "warning",
            "detail": detail,
        }
    )

    total_entries = 0
    for f in data_files:
        try:
            if f.suffix == ".jsonl":
                total_entries += sum(1 for _ in open(f, encoding="utf-8") if _.strip())
            else:
                with open(f, encoding="utf-8") as fh:
                    data = json.load(fh)
                    if isinstance(data, list):
                        total_entries += len(data)
        except Exception:
            pass
    checks.append(
        {"label": "Entrees totales", "status": "ok", "detail": str(total_entries)}
    )

    checks.append(
        {
            "label": "Middleware actif",
            "status": "ok",
            "detail": "PageTrackingMiddleware",
        }
    )

    try:
        from analytics.device_parser import parse_user_agent
        from analytics.geo import is_available as geo_available
        from analytics.geo import lookup as geo_lookup
        from app.utils import hash_ip

        checks.append(
            {
                "label": "geoip2 installe",
                "status": "ok" if geo_available() else "warning",
                "detail": "Base GeoIP absente ou paquet manquant"
                if not geo_available()
                else "OK",
            }
        )

        ua_test = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120"
        )
        device = parse_user_agent(ua_test)
        checks.append(
            {
                "label": "parse_user_agent fonctionne",
                "status": "ok" if device.get("browser") == "Chrome" else "error",
                "detail": f"browser={device.get('browser')}",
            }
        )

        ip_test = geo_lookup("8.8.8.8")
        checks.append(
            {
                "label": "geo_lookup fonctionne",
                "status": "ok" if ip_test is not None else "warning",
                "detail": "GeoIP non resolvable (pas de base ou IP privée)"
                if ip_test is None
                else f"pays={ip_test.get('country', '?')}",
            }
        )

        hash_test = hash_ip("192.168.1.1")
        checks.append(
            {
                "label": "hash_ip fonctionne",
                "status": "ok" if hash_test else "error",
                "detail": hash_test[:16] + "..." if hash_test else "vide",
            }
        )
    except Exception as e:
        checks.append(
            {
                "label": "Pipeline middleware",
                "status": "error",
                "detail": f"Exception: {e}",
            }
        )

    test_entry = {"url": "/__diag__", "ip_hash": "diag", "timestamp": "now"}
    try:
        append(test_entry)
        path = ANALYTICS_DIR / f"{date.today().isoformat()}.jsonl"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                lines = [ln for ln in f if "__diag__" in ln]
            if lines:
                checks.append(
                    {"label": "Ecriture de test reussie", "status": "ok", "detail": ""}
                )
            else:
                checks.append(
                    {
                        "label": "Ecriture de test",
                        "status": "error",
                        "detail": "Entree de test introuvable apres ecriture",
                    }
                )
        else:
            checks.append(
                {
                    "label": "Ecriture de test",
                    "status": "error",
                    "detail": f"Fichier {path.name} non cree",
                }
            )
    except Exception as e:
        checks.append(
            {"label": "Ecriture de test", "status": "error", "detail": str(e)}
        )

    today_str = date.today().isoformat()
    for p in ANALYTICS_DIR.glob(f"{today_str}.*"):
        try:
            with open(p, encoding="utf-8") as f:
                content = f.read()
            cleaned = content.replace("__diag__", "")
            with open(p, "w", encoding="utf-8") as f:
                f.write(cleaned)
        except Exception:
            pass

    return checks


def compute_summary_for_dashboard() -> dict:
    ensure_dir()
    today = date.today()
    today_entries, today_metrics = load_day(today)

    total_today = today_metrics["total"] if today_metrics else len(today_entries)
    unique_today = today_metrics["unique_ips"] if today_metrics else 0
    unique_visitors_today = (
        today_metrics.get("unique_visitors", 0) if today_metrics else 0
    )

    total_30d = 0
    top_pages_30d: dict[str, int] = {}
    d = today
    for _ in range(30):
        entries = _load_entries(d)
        if entries:
            total_30d += len(entries)
            for e in entries:
                url = e.get("url", "/")
                top_pages_30d[url] = top_pages_30d.get(url, 0) + 1
        d -= timedelta(days=1)

    top = sorted(top_pages_30d.items(), key=lambda x: -x[1])[:5]

    today_top = today_metrics.get("top_pages", [])[:3] if today_metrics else []

    return {
        "today": total_today,
        "today_unique": unique_today,
        "today_visitors": unique_visitors_today,
        "month": total_30d,
        "top_pages": [{"url": u, "count": c} for u, c in top],
        "today_top": today_top,
    }
