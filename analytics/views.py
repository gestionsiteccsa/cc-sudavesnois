import zipfile
from datetime import date, timedelta
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe

from markdown_it import MarkdownIt

from accounts.views import est_moderateur
from analytics.analytics_data import (
    ANALYTICS_DIR,
    list_available_dates,
    load_day,
    load_range,
    run_diagnostics,
)


@login_required
@user_passes_test(lambda u: est_moderateur(u))
def admin_stats(request):
    available = list_available_dates()
    today = date.today()
    selected_date = request.GET.get("date", "")

    if selected_date:
        try:
            d = date.fromisoformat(selected_date)
            entries, _summary = load_day(d)
            raw = {d.isoformat(): entries} if entries else {}
            start = end = d
            period = "1"
        except (ValueError, TypeError):
            selected_date = ""
            raw = {}
            start = end = today
            period = "1"
    else:
        selected_date = ""
        period = request.GET.get("period", "7")
        days = int(period) if period.isdigit() else 7
        start = today - timedelta(days=days - 1)
        end = today
        raw = load_range(start, end)

    daily: list[dict] = []
    total_views = 0
    unique_visitors: set[str] = set()
    unique_ips: set[str] = set()
    ip_details: dict[str, dict] = {}
    pages_agg: dict[str, int] = {}
    browsers_agg: dict[str, int] = {}
    os_agg: dict[str, int] = {}
    devices_agg: dict[str, int] = {}
    languages_agg: dict[str, int] = {}
    referrers_agg: dict[str, int] = {}
    cities_agg: dict[str, int] = {}
    regions_agg: dict[str, int] = {}
    countries_agg: dict[str, int] = {}

    for day_str, entries in sorted(raw.items()):
        day_total = len(entries)
        total_views += day_total
        day_ips = {e.get("ip_hash", "") for e in entries if e.get("ip_hash")}
        unique_ips.update(day_ips)
        day_visitors = {e.get("visitor_id", "") for e in entries if e.get("visitor_id")}
        unique_visitors.update(day_visitors)

        day_pages: dict[str, int] = {}
        for e in entries:
            u = e.get("url", "/")
            pages_agg[u] = pages_agg.get(u, 0) + 1
            day_pages[u] = day_pages.get(u, 0) + 1
            d = e.get("device", {})
            br = d.get("browser", "Inconnu")
            browsers_agg[br] = browsers_agg.get(br, 0) + 1
            os_name = d.get("os", "Inconnu")
            os_agg[os_name] = os_agg.get(os_name, 0) + 1
            dt = d.get("type", "desktop")
            devices_agg[dt] = devices_agg.get(dt, 0) + 1
            lang = e.get("language", "").split(",")[0].split(";")[0]
            if lang:
                languages_agg[lang] = languages_agg.get(lang, 0) + 1
            geo = e.get("geo") or {}
            ip_h = e.get("ip_hash", "")
            if ip_h not in ip_details:
                ip_details[ip_h] = {
                    "ip": e.get("ip", ""),
                    "ip_hash": ip_h,
                    "country": geo.get("country"),
                    "country_name": geo.get("country_name"),
                    "pages": 1,
                }
            else:
                ip_details[ip_h]["pages"] += 1
            c = geo.get("city")
            if c:
                cities_agg[c] = cities_agg.get(c, 0) + 1
            r = geo.get("region")
            if r:
                regions_agg[r] = regions_agg.get(r, 0) + 1
            cc = geo.get("country")
            if cc:
                countries_agg[cc] = countries_agg.get(cc, 0) + 1
            ref = e.get("referrer", "")
            if ref:
                try:
                    domain = ref.split("/")[2]
                    referrers_agg[domain] = referrers_agg.get(domain, 0) + 1
                except IndexError:
                    pass

        top_day = sorted(day_pages.items(), key=lambda x: -x[1])[:5]
        daily.append(
            {
                "date": day_str,
                "views": day_total,
                "unique": len(day_ips),
                "visitors": len(day_visitors),
                "top_pages": [{"url": u, "count": c} for u, c in top_day],
            }
        )

    top_pages = sorted(pages_agg.items(), key=lambda x: -x[1])[:50]
    top_browsers = sorted(browsers_agg.items(), key=lambda x: -x[1])
    top_os = sorted(os_agg.items(), key=lambda x: -x[1])
    top_devices = sorted(devices_agg.items(), key=lambda x: -x[1])
    top_languages = sorted(languages_agg.items(), key=lambda x: -x[1])
    top_referrers = sorted(referrers_agg.items(), key=lambda x: -x[1])[:20]
    top_cities = sorted(cities_agg.items(), key=lambda x: -x[1])[:15]
    top_regions = sorted(regions_agg.items(), key=lambda x: -x[1])[:10]
    top_countries = sorted(countries_agg.items(), key=lambda x: -x[1])[:15]

    top_ips = sorted(ip_details.values(), key=lambda x: -x["pages"])[:50]

    response_time_avg = 0
    count_with_time = 0
    for entries in raw.values():
        for e in entries:
            rt = e.get("response_time_ms")
            if rt is not None:
                response_time_avg += rt
                count_with_time += 1
    if count_with_time:
        response_time_avg //= count_with_time

    context = {
        "daily": daily,
        "total_views": total_views,
        "total_unique": len(unique_ips),
        "total_visitors": len(unique_visitors),
        "top_pages": [{"url": u, "count": c} for u, c in top_pages],
        "top_browsers": dict(top_browsers),
        "top_os": dict(top_os),
        "top_devices": dict(top_devices),
        "top_languages": dict(top_languages),
        "top_referrers": [{"source": s, "count": c} for s, c in top_referrers],
        "top_cities": [{"name": n, "count": c} for n, c in top_cities],
        "top_regions": [{"name": n, "count": c} for n, c in top_regions],
        "top_countries": [{"name": n, "count": c} for n, c in top_countries],
        "period": period,
        "selected_date": selected_date,
        "available_dates": available,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "top_ips": top_ips,
        "response_time_avg": response_time_avg,
        "diagnostics": run_diagnostics() if request.GET.get("debug") == "1" else None,
    }
    return render(request, "analytics/admin_stats.html", context)


@login_required
@user_passes_test(lambda u: est_moderateur(u))
def download_day_json(request, day_str: str):
    try:
        d = date.fromisoformat(day_str)
    except ValueError:
        return HttpResponse("Date invalide", status=400)
    entries, _summary = load_day(d)
    return JsonResponse(
        entries, safe=False, json_dumps_params={"ensure_ascii": False, "indent": 2}
    )


@login_required
@user_passes_test(lambda u: est_moderateur(u))
def download_all_json(request):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for fpath in sorted(ANALYTICS_DIR.glob("*.json*")):
            if ".summary" in fpath.stem:
                continue
            rel_name = fpath.name
            zf.write(fpath, rel_name)
    buffer.seek(0)
    return HttpResponse(
        buffer.getvalue(),
        content_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=analytics_data.zip"},
    )


@login_required
@user_passes_test(lambda u: est_moderateur(u))
def admin_changelog(request):
    changelog_path = Path(settings.BASE_DIR / "CHANGELOG.md")
    raw = changelog_path.read_text(encoding="utf-8")

    md = MarkdownIt(
        "commonmark",
        {"html": True, "linkify": True, "typographer": True},
    )
    html = md.render(raw)

    return render(
        request,
        "analytics/admin_changelog.html",
        {"changelog_html": mark_safe(html)},
    )
