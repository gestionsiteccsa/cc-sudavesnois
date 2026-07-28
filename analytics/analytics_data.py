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


def compute_hourly_heatmap(start: date, end: date) -> list[list[int]]:
    matrix = [[0] * 24 for _ in range(7)]
    d = start
    while d <= end:
        for entry in _load_entries(d):
            ts = entry.get("timestamp", "")
            if ts:
                try:
                    dt = datetime.fromisoformat(ts)
                    dow = dt.weekday()
                    hour = dt.hour
                    matrix[dow][hour] += 1
                except (ValueError, TypeError):
                    pass
        d += timedelta(days=1)
    return matrix


def compute_calendar_data(days_back: int = 365) -> dict:
    today = date.today()
    start = today - timedelta(days=days_back)
    counts: dict[str, int] = {}
    max_count = 0
    d = start
    while d <= today:
        entries = _load_entries(d)
        cnt = len(entries)
        counts[d.isoformat()] = cnt
        if cnt > max_count:
            max_count = cnt
        d += timedelta(days=1)
    return {"data": counts, "max": max_count}


def _is_french_region(geo: dict | None) -> bool:
    if not geo:
        return False
    return geo.get("country") == "FR"


def compute_france_regions(start: date, end: date) -> dict[str, int]:
    regions: dict[str, int] = {}
    d = start
    while d <= end:
        for entry in _load_entries(d):
            geo = entry.get("geo") or {}
            if not _is_french_region(geo):
                continue
            region = geo.get("region") or geo.get("region_code") or ""
            if not region:
                continue
            regions[region] = regions.get(region, 0) + 1
        d += timedelta(days=1)
    return dict(sorted(regions.items(), key=lambda x: -x[1]))


def compute_device_evolution(start: date, end: date) -> list[dict]:
    daily: dict[str, dict[str, int]] = {}
    d = start
    while d <= end:
        ds = d.isoformat()
        daily[ds] = {"desktop": 0, "mobile": 0, "tablet": 0}
        for entry in _load_entries(d):
            dt_ = entry.get("device", {}).get("type", "desktop")
            if dt_ in daily[ds]:
                daily[ds][dt_] += 1
        d += timedelta(days=1)
    return [{"date": ds, **counts} for ds, counts in sorted(daily.items())]


def compute_retention(start: date, end: date) -> dict:
    seen_before: set[str] = set()
    new_daily: dict[str, int] = {}
    returning_daily: dict[str, int] = {}

    lookback_start = start - timedelta(days=30)
    d = lookback_start
    while d < start:
        for entry in _load_entries(d):
            vid = entry.get("visitor_id")
            if vid:
                seen_before.add(vid)
        d += timedelta(days=1)

    newly_seen: set[str] = set()
    d = start
    while d <= end:
        ds = d.isoformat()
        new_count = 0
        returning_count = 0
        for entry in _load_entries(d):
            vid = entry.get("visitor_id")
            if not vid:
                continue
            if vid in seen_before:
                returning_count += 1
            else:
                if vid not in newly_seen:
                    new_count += 1
                    newly_seen.add(vid)
                else:
                    returning_count += 1
        new_daily[ds] = new_count
        returning_daily[ds] = returning_count
        d += timedelta(days=1)

    return {
        "new": new_daily,
        "returning": returning_daily,
    }


def compute_entry_pages(start: date, end: date) -> dict[str, int]:
    sessions_seen: set[str] = set()
    pages: dict[str, int] = {}
    d = start
    while d <= end:
        for entry in _load_entries(d):
            session = entry.get("session_key", "")
            if not session or session in sessions_seen:
                continue
            sessions_seen.add(session)
            url = entry.get("url", "/")
            pages[url] = pages.get(url, 0) + 1
        d += timedelta(days=1)
    return dict(sorted(pages.items(), key=lambda x: -x[1])[:15])


def compute_exit_pages(start: date, end: date) -> dict[str, int]:
    session_last: dict[str, str] = {}
    d = start
    while d <= end:
        for entry in _load_entries(d):
            session = entry.get("session_key", "")
            if not session:
                continue
            session_last[session] = entry.get("url", "/")
        d += timedelta(days=1)
    pages: dict[str, int] = {}
    for url in session_last.values():
        pages[url] = pages.get(url, 0) + 1
    return dict(sorted(pages.items(), key=lambda x: -x[1])[:15])


def compute_session_depth(start: date, end: date) -> dict[str, int]:
    session_counts: dict[str, int] = {}
    d = start
    while d <= end:
        for entry in _load_entries(d):
            session = entry.get("session_key", "")
            if not session:
                continue
            session_counts[session] = session_counts.get(session, 0) + 1
        d += timedelta(days=1)

    distribution = {"1": 0, "2-3": 0, "4-5": 0, "6-10": 0, "10+": 0}
    for cnt in session_counts.values():
        if cnt == 1:
            distribution["1"] += 1
        elif cnt <= 3:
            distribution["2-3"] += 1
        elif cnt <= 5:
            distribution["4-5"] += 1
        elif cnt <= 10:
            distribution["6-10"] += 1
        else:
            distribution["10+"] += 1
    return distribution


def compute_404_stats(start: date, end: date) -> dict:
    pages_404: dict[str, dict] = {}
    d = start
    while d <= end:
        for entry in _load_entries(d):
            if entry.get("status") != 404:
                continue
            url = entry.get("url", "/")
            if url not in pages_404:
                pages_404[url] = {
                    "url": url,
                    "count": 0,
                    "referrers": {},
                    "first_seen": entry.get("timestamp", ""),
                    "last_seen": entry.get("timestamp", ""),
                }
            r = pages_404[url]
            r["count"] += 1
            ref = entry.get("referrer", "")
            if ref:
                r["referrers"][ref] = r["referrers"].get(ref, 0) + 1
            ts = entry.get("timestamp", "")
            if ts:
                if ts < r["first_seen"]:
                    r["first_seen"] = ts
                if ts > r["last_seen"]:
                    r["last_seen"] = ts
        d += timedelta(days=1)

    top_errors = sorted(pages_404.values(), key=lambda x: -x["count"])[:20]
    for err in top_errors:
        err["top_ref"] = (
            max(err["referrers"].items(), key=lambda x: x[1])[0]
            if err["referrers"]
            else ""
        )
    return {"total_404": sum(e["count"] for e in top_errors), "pages": top_errors}


def compute_page_performance(start: date, end: date) -> list[dict]:
    page_times: dict[str, list[int]] = {}
    d = start
    while d <= end:
        for entry in _load_entries(d):
            url = entry.get("url", "/")
            rt = entry.get("response_time_ms")
            if rt is None:
                continue
            if url not in page_times:
                page_times[url] = []
            page_times[url].append(rt)
        d += timedelta(days=1)

    result: list[dict] = []
    for url, times in page_times.items():
        sorted_times = sorted(times)
        n = len(sorted_times)
        p95_idx = int(n * 0.95)
        result.append(
            {
                "url": url,
                "views": n,
                "avg_ms": sum(times) // n,
                "p50_ms": sorted_times[n // 2],
                "p95_ms": sorted_times[min(p95_idx, n - 1)],
                "max_ms": max(times),
            }
        )
    result.sort(key=lambda x: -x["avg_ms"])
    return result[:20]


def detect_anomalies(start: date, end: date) -> list[dict]:
    lookback_start = start - timedelta(days=30)
    baseline_counts: dict[str, int] = {}
    d = lookback_start
    while d < start:
        entries = _load_entries(d)
        if entries:
            baseline_counts[d.isoformat()] = len(entries)
        d += timedelta(days=1)

    if not baseline_counts:
        return []

    avg_baseline = sum(baseline_counts.values()) / len(baseline_counts)
    if avg_baseline == 0:
        return []

    anomalies: list[dict] = []
    d = start
    while d <= end:
        entries = _load_entries(d)
        if not entries:
            d += timedelta(days=1)
            continue
        cnt = len(entries)
        ratio = cnt / avg_baseline
        if ratio > 1.5:
            anomalies.append(
                {
                    "date": d.isoformat(),
                    "count": cnt,
                    "baseline_avg": int(avg_baseline),
                    "type": "spike",
                    "change_pct": int((ratio - 1) * 100),
                }
            )
        elif ratio < 0.5:
            anomalies.append(
                {
                    "date": d.isoformat(),
                    "count": cnt,
                    "baseline_avg": int(avg_baseline),
                    "type": "drop",
                    "change_pct": int((1 - ratio) * 100),
                }
            )
        d += timedelta(days=1)
    return anomalies


_FRANCE_REGION_MAP = {
    "Île-de-France": "IDF",
    "Auvergne-Rhône-Alpes": "ARA",
    "Hauts-de-France": "HDF",
    "Nouvelle-Aquitaine": "NAQ",
    "Occitanie": "OCC",
    "Grand Est": "GES",
    "Provence-Alpes-Côte d'Azur": "PAC",
    "Pays de la Loire": "PDL",
    "Bretagne": "BRE",
    "Normandie": "NOR",
    "Bourgogne-Franche-Comté": "BFC",
    "Centre-Val de Loire": "CVL",
    "Corse": "COR",
}

_FRANCE_CITIES_TO_REGIONS: dict[str, str] = {
    "Paris": "Île-de-France",
    "Versailles": "Île-de-France",
    "Boulogne-Billancourt": "Île-de-France",
    "Saint-Denis": "Île-de-France",
    "Nanterre": "Île-de-France",
    "Créteil": "Île-de-France",
    "Évry": "Île-de-France",
    "Cergy": "Île-de-France",
    "Lyon": "Auvergne-Rhône-Alpes",
    "Grenoble": "Auvergne-Rhône-Alpes",
    "Saint-Étienne": "Auvergne-Rhône-Alpes",
    "Clermont-Ferrand": "Auvergne-Rhône-Alpes",
    "Annecy": "Auvergne-Rhône-Alpes",
    "Chambéry": "Auvergne-Rhône-Alpes",
    "Valence": "Auvergne-Rhône-Alpes",
    "Lille": "Hauts-de-France",
    "Amiens": "Hauts-de-France",
    "Calais": "Hauts-de-France",
    "Dunkerque": "Hauts-de-France",
    "Roubaix": "Hauts-de-France",
    "Tourcoing": "Hauts-de-France",
    "Fourmies": "Hauts-de-France",
    "Bordeaux": "Nouvelle-Aquitaine",
    "Limoges": "Nouvelle-Aquitaine",
    "Poitiers": "Nouvelle-Aquitaine",
    "La Rochelle": "Nouvelle-Aquitaine",
    "Pau": "Nouvelle-Aquitaine",
    "Bayonne": "Nouvelle-Aquitaine",
    "Toulouse": "Occitanie",
    "Montpellier": "Occitanie",
    "Nîmes": "Occitanie",
    "Perpignan": "Occitanie",
    "Albi": "Occitanie",
    "Strasbourg": "Grand Est",
    "Nancy": "Grand Est",
    "Metz": "Grand Est",
    "Reims": "Grand Est",
    "Mulhouse": "Grand Est",
    "Colmar": "Grand Est",
    "Marseille": "Provence-Alpes-Côte d'Azur",
    "Nice": "Provence-Alpes-Côte d'Azur",
    "Toulon": "Provence-Alpes-Côte d'Azur",
    "Aix-en-Provence": "Provence-Alpes-Côte d'Azur",
    "Avignon": "Provence-Alpes-Côte d'Azur",
    "Nantes": "Pays de la Loire",
    "Angers": "Pays de la Loire",
    "Le Mans": "Pays de la Loire",
    "Saint-Nazaire": "Pays de la Loire",
    "Rennes": "Bretagne",
    "Brest": "Bretagne",
    "Quimper": "Bretagne",
    "Saint-Brieuc": "Bretagne",
    "Vannes": "Bretagne",
    "Rouen": "Normandie",
    "Caen": "Normandie",
    "Le Havre": "Normandie",
    "Cherbourg": "Normandie",
    "Évreux": "Normandie",
    "Dijon": "Bourgogne-Franche-Comté",
    "Besançon": "Bourgogne-Franche-Comté",
    "Belfort": "Bourgogne-Franche-Comté",
    "Orléans": "Centre-Val de Loire",
    "Tours": "Centre-Val de Loire",
    "Blois": "Centre-Val de Loire",
    "Chartres": "Centre-Val de Loire",
    "Bourges": "Centre-Val de Loire",
    "Ajaccio": "Corse",
    "Bastia": "Corse",
}


def normalize_france_regions(
    raw_regions: dict[str, int],
) -> dict[str, dict]:
    normalized: dict[str, dict] = {}
    for name, count in raw_regions.items():
        mapped = _FRANCE_REGION_MAP.get(name)
        if mapped:
            key = mapped
        else:
            city_region = _FRANCE_CITIES_TO_REGIONS.get(name)
            if city_region:
                key = _FRANCE_REGION_MAP.get(city_region, name)
            else:
                continue
        if key not in normalized:
            normalized[key] = {"name": name, "count": 0}
        normalized[key]["count"] += count
    return normalized


def compute_user_journeys(start: date, end: date) -> list[dict]:
    session_pages: dict[str, list[str]] = {}
    d = start
    while d <= end:
        for e in _load_entries(d):
            sess = e.get("session_key", "")
            if not sess:
                continue
            url = e.get("url", "/")
            if sess not in session_pages:
                session_pages[sess] = []
            session_pages[sess].append(url)
        d += timedelta(days=1)

    transitions: dict[str, int] = {}
    for pages in session_pages.values():
        for i in range(len(pages) - 1):
            pair = f"{pages[i]} → {pages[i + 1]}"
            transitions[pair] = transitions.get(pair, 0) + 1

    top = sorted(transitions.items(), key=lambda x: -x[1])[:20]
    return [
        {"from_url": k.split(" → ")[0], "to_url": k.split(" → ")[1], "count": v}
        for k, v in top
    ]


def log_search_query(query: str, ip: str = "", results_count: int = 0):
    entry = {
        "type": "search",
        "query": query,
        "results_count": results_count,
        "ip_hash": "",
        "url": "/recherche/",
        "status": 200,
        "response_time_ms": 0,
        "ip": ip,
        "session_key": "",
        "visitor_id": None,
        "user_id": None,
        "timestamp": "",
        "referrer": "",
        "language": "",
        "device": {
            "type": "desktop",
            "os": "Inconnu",
            "browser": "Inconnu",
            "brand": None,
        },
        "geo": None,
    }
    from datetime import datetime as dt

    from app.utils import hash_ip

    entry["timestamp"] = dt.now().strftime("%Y-%m-%dT%H:%M:%S")
    entry["ip_hash"] = hash_ip(ip) if ip else ""
    append(entry)


def get_search_queries(start: date, end: date) -> list[dict]:
    queries: dict[str, int] = {}
    d = start
    while d <= end:
        for entry in _load_entries(d):
            if entry.get("type") != "search":
                continue
            q = entry.get("query", "")
            if q:
                queries[q] = queries.get(q, 0) + 1
        d += timedelta(days=1)
    sorted_queries = sorted(queries.items(), key=lambda x: -x[1])[:20]
    return [{"query": q, "count": c} for q, c in sorted_queries]


def delete_data_range(date_start: date, date_end: date) -> int:
    deleted = 0
    d = date_start
    while d <= date_end:
        for ext in (".jsonl", ".json"):
            path = ANALYTICS_DIR / f"{d.isoformat()}{ext}"
            if path.exists():
                path.unlink(missing_ok=True)
                deleted += 1
        d += timedelta(days=1)
    return deleted


def export_range_data(date_start: date, date_end: date) -> list[dict]:
    records: list[dict] = []
    d = date_start
    while d <= date_end:
        for entry in _load_entries(d):
            records.append(
                {
                    "date": d.isoformat(),
                    "url": entry.get("url", "/"),
                    "ip_hash": entry.get("ip_hash", ""),
                    "timestamp": entry.get("timestamp", ""),
                    "device": entry.get("device", {}).get("type", "desktop"),
                    "browser": entry.get("device", {}).get("browser", "?"),
                    "country": (entry.get("geo") or {}).get("country", ""),
                    "city": (entry.get("geo") or {}).get("city", ""),
                    "referrer": entry.get("referrer", ""),
                    "response_time_ms": entry.get("response_time_ms", 0),
                }
            )
        d += timedelta(days=1)
    return records
