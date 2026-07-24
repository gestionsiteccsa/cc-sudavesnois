import json
import logging
import threading
from datetime import date, timedelta
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

ANALYTICS_DIR = settings.BASE_DIR / "analytics_data"
FLUSH_EVERY = 10
_buffer: list[dict] = []
_buffer_lock = threading.Lock()
_request_count = 0


def _today_path() -> Path:
    return ANALYTICS_DIR / f"{date.today().isoformat()}.json"


def _summary_path(d: date | None = None) -> Path:
    d = d or date.today()
    return ANALYTICS_DIR / f"{d.isoformat()}.summary.json"


def ensure_dir():
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)


def append(entry: dict):
    global _request_count
    with _buffer_lock:
        _buffer.append(entry)
        _request_count += 1
        if _request_count >= FLUSH_EVERY:
            _flush_locked()
            _request_count = 0


def flush():
    with _buffer_lock:
        if _buffer:
            _flush_locked()


def _flush_locked():
    if not _buffer:
        return
    ensure_dir()
    path = _today_path()
    try:
        existing = []
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                try:
                    existing = json.load(f)
                except json.JSONDecodeError:
                    existing = []
        all_entries = existing + _buffer
        with open(path, "w", encoding="utf-8") as f:
            json.dump(all_entries, f, ensure_ascii=False, indent=None)
        _update_summary(all_entries)
        _buffer.clear()
    except OSError as e:
        logger.error("Erreur écriture analytics: %s", e)


def _update_summary(entries: list[dict]):
    if not entries:
        return
    total = len(entries)
    sessions = len({e.get("session_key") for e in entries if e.get("session_key")})
    ip_hashes = len({e.get("ip_hash") for e in entries if e.get("ip_hash")})
    pages: dict[str, int] = {}
    browsers: dict[str, int] = {}
    oss: dict[str, int] = {}
    device_types: dict[str, int] = {}
    languages: dict[str, int] = {}
    referrers: dict[str, int] = {}

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

    top_pages = sorted(pages.items(), key=lambda x: -x[1])[:20]
    top_browsers = sorted(browsers.items(), key=lambda x: -x[1])[:10]
    top_os = sorted(oss.items(), key=lambda x: -x[1])[:10]
    top_refs = sorted(referrers.items(), key=lambda x: -x[1])[:10]

    summary = {
        "total": total,
        "unique_sessions": sessions,
        "unique_ips": ip_hashes,
        "top_pages": [{"url": u, "count": c} for u, c in top_pages],
        "browsers": dict(top_browsers),
        "os": dict(top_os),
        "device_types": dict(device_types),
        "languages": dict(languages),
        "referrers": dict(top_refs),
    }
    try:
        with open(_summary_path(), "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
    except OSError as e:
        logger.error("Erreur écriture summary analytics: %s", e)


def load_day(d: date) -> tuple[list[dict], dict | None]:
    path = ANALYTICS_DIR / f"{d.isoformat()}.json"
    summary_path = _summary_path(d)
    entries: list[dict] = []
    summary: dict | None = None
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            try:
                entries = json.load(f)
            except json.JSONDecodeError:
                entries = []
    if summary_path.exists():
        with open(summary_path, "r", encoding="utf-8") as f:
            try:
                summary = json.load(f)
            except json.JSONDecodeError:
                pass
    return entries, summary


def load_range(start: date, end: date) -> dict:
    data: dict[str, list[dict]] = {}
    d = start
    while d <= end:
        entries, _summary = load_day(d)
        if entries:
            data[d.isoformat()] = entries
        d += timedelta(days=1)
    return data


def list_available_dates() -> list[str]:
    ensure_dir()
    files = sorted(ANALYTICS_DIR.glob("*.json"))
    seen: set[str] = set()
    dates: list[str] = []
    for f in files:
        stem = f.stem
        if stem.endswith(".summary"):
            continue
        if stem not in seen:
            seen.add(stem)
            dates.append(stem)
    dates.sort(reverse=True)
    return dates


def compute_summary_for_dashboard() -> dict:
    ensure_dir()
    today = date.today()
    today_entries, today_summary = load_day(today)

    total_today = today_summary["total"] if today_summary else len(today_entries)
    unique_today = today_summary["unique_ips"] if today_summary else 0

    total_30d = 0
    top_pages_30d: dict[str, int] = {}
    d = today
    for _ in range(30):
        _, s = load_day(d)
        if s:
            total_30d += s["total"]
            for p in s.get("top_pages", []):
                url = p["url"]
                top_pages_30d[url] = top_pages_30d.get(url, 0) + p["count"]
        d -= timedelta(days=1)

    top = sorted(top_pages_30d.items(), key=lambda x: -x[1])[:5]

    today_top = []
    if today_summary:
        today_top = today_summary.get("top_pages", [])[:3]

    return {
        "today": total_today,
        "today_unique": unique_today,
        "month": total_30d,
        "top_pages": [{"url": u, "count": c} for u, c in top],
        "today_top": today_top,
    }
