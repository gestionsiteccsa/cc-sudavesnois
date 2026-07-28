import json
import logging
from datetime import date, timedelta
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

ANALYTICS_DIR = settings.BASE_DIR / "analytics_data"


def ensure_dir():
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)


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
    if not path.exists():
        return []
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
    files = sorted(ANALYTICS_DIR.glob("*.jsonl"))
    seen: set[str] = set()
    dates: list[str] = []
    for f in files:
        stem = f.stem
        if stem not in seen:
            seen.add(stem)
            dates.append(stem)
    dates.sort(reverse=True)
    return dates


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
