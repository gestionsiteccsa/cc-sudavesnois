import zipfile
from datetime import date, timedelta
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe

from markdown_it import MarkdownIt

from accounts.views import est_moderateur
from analytics.analytics_data import (
    ANALYTICS_DIR,
    count_recent_ips,
    is_bot_url,
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

    def _inc(d: dict, key):
        if key:
            d[key] = d.get(key, 0) + 1

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
    city_details: dict[str, dict] = {}
    regions_agg: dict[str, int] = {}
    countries_agg: dict[str, int] = {}
    bot_countries: dict[str, int] = {}
    bot_regions: dict[str, int] = {}
    bot_cities: dict[str, int] = {}

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
            if is_bot_url(u):
                continue
            device = e.get("device", {})
            geo = e.get("geo") or {}
            timestamp = e.get("timestamp", "")
            ip_h = e.get("ip_hash", "")
            _inc(pages_agg, u)
            _inc(day_pages, u)
            _inc(browsers_agg, device.get("browser"))
            _inc(os_agg, device.get("os"))
            _inc(devices_agg, device.get("type"))
            _inc(languages_agg, e.get("language", "").split(",")[0].split(";")[0])
            city = geo.get("city", "")
            cc = geo.get("country", "")
            is_bot = cc == "US" or (
                not cc and device.get("browser", "") in ("Inconnu", "")
            )
            geo_target_cities = bot_cities if is_bot else cities_agg
            geo_target_regions = bot_regions if is_bot else regions_agg
            geo_target_countries = bot_countries if is_bot else countries_agg
            _inc(geo_target_cities, city)
            if city:
                lat = geo.get("lat")
                lon = geo.get("lon")
                if city not in city_details:
                    city_details[city] = {
                        "city": city,
                        "country": cc,
                        "lat": lat,
                        "lon": lon,
                        "count": 0,
                    }
                city_details[city]["count"] += 1
                if lat is not None and city_details[city]["lat"] is None:
                    city_details[city]["lat"] = lat
                if lon is not None and city_details[city]["lon"] is None:
                    city_details[city]["lon"] = lon
            _inc(geo_target_regions, geo.get("region"))
            _inc(geo_target_countries, cc)

            ref = e.get("referrer", "")
            if ref:
                try:
                    _inc(referrers_agg, ref.split("/")[2])
                except IndexError:
                    pass

            if ip_h not in ip_details:
                ip_details[ip_h] = {
                    "ip": e.get("ip", ""),
                    "ip_hash": ip_h,
                    "country": cc,
                    "country_name": geo.get("country_name"),
                    "probable_bot": is_bot,
                    "pages": 0,
                    "pages_list": {},
                }
            ip_details[ip_h]["pages"] += 1
            if u not in ip_details[ip_h]["pages_list"]:
                ip_details[ip_h]["pages_list"][u] = {
                    "url": u,
                    "count": 0,
                    "browser": device.get("browser", "?"),
                    "os": device.get("os", "?"),
                    "last_seen": timestamp,
                    "referrer": ref,
                }
            else:
                if ref:
                    ip_details[ip_h]["pages_list"][u]["referrer"] = ref
            ip_details[ip_h]["pages_list"][u]["count"] += 1
            ip_details[ip_h]["pages_list"][u]["last_seen"] = max(
                ip_details[ip_h]["pages_list"][u]["last_seen"], timestamp
            )

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
    max_city_count = top_cities[0][1] if top_cities else 0
    top_cities_details = [
        {
            "name": name,
            "count": count,
            "country": city_details.get(name, {}).get("country", ""),
        }
        for name, count in top_cities
    ]
    top_regions = sorted(regions_agg.items(), key=lambda x: -x[1])[:10]
    top_countries = sorted(countries_agg.items(), key=lambda x: -x[1])[:15]
    bot_cities_list = sorted(bot_cities.items(), key=lambda x: -x[1])[:15]
    bot_regions_list = sorted(bot_regions.items(), key=lambda x: -x[1])[:10]
    bot_countries_list = sorted(bot_countries.items(), key=lambda x: -x[1])[:15]

    top_ips = sorted(ip_details.values(), key=lambda x: -x["pages"])[:50]
    for ip in top_ips:
        ip["pages_list"] = sorted(ip["pages_list"].values(), key=lambda x: -x["count"])
    visitor_ips = [ip for ip in top_ips if not ip.get("probable_bot")]
    bot_ips = [ip for ip in top_ips if ip.get("probable_bot")]

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
        "bot_cities_list": [{"name": n, "count": c} for n, c in bot_cities_list],
        "bot_regions_list": [{"name": n, "count": c} for n, c in bot_regions_list],
        "bot_countries_list": [{"name": n, "count": c} for n, c in bot_countries_list],
        "period": period,
        "selected_date": selected_date,
        "available_dates": available,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "top_ips": top_ips,
        "visitor_ips": visitor_ips,
        "bot_ips": bot_ips,
        "has_bots": len(bot_ips) > 0,
        "top_cities_details": top_cities_details,
        "max_city_count": max_city_count,
        "active_visitors": count_recent_ips(),
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


@login_required
@user_passes_test(lambda u: est_moderateur(u))
def delete_day_stats(request, day_str):
    if request.method != "POST":
        return HttpResponse("Methode non autorisee", status=405)
    try:
        date.fromisoformat(day_str)
    except ValueError:
        return HttpResponse("Date invalide", status=400)

    deleted = False
    for ext in (".jsonl", ".json"):
        path = ANALYTICS_DIR / f"{day_str}{ext}"
        if path.exists():
            path.unlink()
            deleted = True

    if not deleted:
        messages.warning(request, f"Aucune donnee trouvee pour le {day_str}")
    else:
        messages.success(request, f"Statistiques du {day_str} supprimees")

    return redirect("analytics:admin_stats")
