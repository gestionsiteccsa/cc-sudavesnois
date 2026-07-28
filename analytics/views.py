import json
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
    compute_404_stats,
    compute_calendar_data,
    compute_device_evolution,
    compute_entry_pages,
    compute_exit_pages,
    compute_france_regions,
    compute_hourly_heatmap,
    compute_page_performance,
    compute_retention,
    compute_session_depth,
    compute_user_journeys,
    count_recent_ips,
    delete_data_range,
    detect_anomalies,
    export_range_data,
    get_search_queries,
    is_bot_url,
    list_available_dates,
    load_day,
    load_range,
    normalize_france_regions,
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

    # --- Tendances (vs période précédente) ---
    period_days = (end - start).days + 1
    prev_start = start - timedelta(days=period_days)
    prev_end = start - timedelta(days=1)
    prev_raw = load_range(prev_start, prev_end)
    prev_total = sum(len(entries) for entries in prev_raw.values()) if prev_raw else 1
    prev_ips: set[str] = set()
    prev_visitors: set[str] = set()
    prev_rt_total = 0
    prev_rt_count = 0
    for entries in prev_raw.values():
        for e_ in entries:
            ip_h = e_.get("ip_hash", "")
            if ip_h:
                prev_ips.add(ip_h)
            vid = e_.get("visitor_id", "")
            if vid:
                prev_visitors.add(vid)
            rt_ = e_.get("response_time_ms")
            if rt_ is not None:
                prev_rt_total += rt_
                prev_rt_count += 1
    prev_rt_avg = prev_rt_total // prev_rt_count if prev_rt_count else 0

    def _trend(curr: int, prev: int) -> dict:
        if not prev:
            return {"pct": None, "up": None}
        pct = int(round((curr - prev) / prev * 100))
        return {"pct": abs(pct), "up": pct > 0, "neutral": pct == 0}

    trends = {
        "views": _trend(total_views, prev_total),
        "ips": _trend(len(unique_ips), len(prev_ips)),
        "visitors": _trend(len(unique_visitors), len(prev_visitors)),
        "response_time": _trend(response_time_avg, prev_rt_avg),
    }

    # --- Mode comparaison ---
    show_compare = request.GET.get("compare") == "on"
    comparison = None
    if show_compare and prev_raw:
        comp_total = prev_total
        comp_ips = len(prev_ips)
        comp_visitors = len(prev_visitors)
        comp_daily: list[dict] = []
        comp_pages: dict[str, int] = {}
        d = prev_start
        while d <= prev_end:
            entries = prev_raw.get(d.isoformat(), [])
            comp_daily.append(
                {
                    "date": d.isoformat(),
                    "views": len(entries),
                    "unique": len(
                        {e.get("ip_hash") for e in entries if e.get("ip_hash")}
                    ),
                }
            )
            for e in entries:
                u = e.get("url", "/")
                comp_pages[u] = comp_pages.get(u, 0) + 1
            d += timedelta(days=1)
        comp_top_pages = sorted(comp_pages.items(), key=lambda x: -x[1])[:10]
        comparison = {
            "total": comp_total,
            "unique_ips": comp_ips,
            "visitors": comp_visitors,
            "daily": comp_daily,
            "top_pages": [{"url": u, "count": c} for u, c in comp_top_pages],
            "start": prev_start.isoformat(),
            "end": prev_end.isoformat(),
        }

    # --- Données Chart.js (évolution) ---
    chart_labels = [d_["date"] for d_ in daily]
    chart_views = [d_["views"] for d_ in daily]
    chart_unique = [d_["unique"] for d_ in daily]
    chart_visitors = [d_["visitors"] for d_ in daily]
    comparison_views = [d_["views"] for d_ in comparison["daily"]] if comparison else []
    comparison_labels = [d_["date"] for d_ in comparison["daily"]] if comparison else []

    # --- Heatmap horaire ---
    heatmap = compute_hourly_heatmap(start, end)
    heatmap_labels = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

    # --- Calendrier annuel ---
    calendar = compute_calendar_data()

    # --- Régions France ---
    raw_france = compute_france_regions(start, end)
    france_regions = normalize_france_regions(raw_france)

    # --- Évolution appareils ---
    device_evo = compute_device_evolution(start, end)

    # --- Rétention ---
    retention = compute_retention(start, end)

    # --- Pages entrée/sortie ---
    entry_pages = compute_entry_pages(start, end)
    exit_pages = compute_exit_pages(start, end)

    # --- Profondeur de session ---
    session_depth = compute_session_depth(start, end)

    # --- Erreurs 404 ---
    error_stats = compute_404_stats(start, end)

    # --- Performance par page ---
    page_perf = compute_page_performance(start, end)

    # --- Anomalies ---
    anomalies = detect_anomalies(start, end)

    active_visitors = count_recent_ips()

    # --- Tableau de classement des referrers ---
    referrer_categories = {
        "Moteurs de recherche": 0,
        "Réseaux sociaux": 0,
        "Accès direct": 0,
        "Sites externes": 0,
    }
    se_domains = frozenset(
        {
            "www.google.",
            "google.",
            "www.bing.",
            "bing.",
            "search.yahoo.",
            "duckduckgo.",
            "www.qwant.",
            "qwant.",
            "www.ecosia.",
            "ecosia.",
        }
    )
    social_domains = frozenset(
        {
            "facebook.",
            "www.facebook.",
            "twitter.",
            "www.twitter.",
            "x.com",
            "linkedin.",
            "www.linkedin.",
            "instagram.",
            "www.instagram.",
            "t.co",
        }
    )
    for ref in top_referrers:
        source, count = ref
        is_se = any(source.startswith(d) for d in se_domains)
        is_social = any(source.startswith(d) for d in social_domains)
        if is_se:
            referrer_categories["Moteurs de recherche"] += count
        elif is_social:
            referrer_categories["Réseaux sociaux"] += count
        else:
            referrer_categories["Sites externes"] += count
    direct_est = max(0, total_views - sum(r[1] for r in top_referrers))
    referrer_categories["Accès direct"] = direct_est

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
        "referrer_categories": referrer_categories,
        "referrer_categories_json": json.dumps(referrer_categories),
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
        "active_visitors": active_visitors,
        "response_time_avg": response_time_avg,
        "diagnostics": run_diagnostics() if request.GET.get("debug") == "1" else None,
        # --- Nouvelles données ---
        "trends": trends,
        "show_compare": show_compare,
        "comparison": comparison,
        "chart_labels": json.dumps(chart_labels),
        "chart_views": json.dumps(chart_views),
        "chart_unique": json.dumps(chart_unique),
        "chart_visitors": json.dumps(chart_visitors),
        "comparison_views": json.dumps(comparison_views),
        "comparison_labels": json.dumps(comparison_labels),
        "heatmap": json.dumps(heatmap),
        "heatmap_labels": json.dumps(heatmap_labels),
        "calendar": calendar,
        "france_regions": france_regions,
        "france_regions_json": json.dumps(
            dict(sorted(france_regions.items(), key=lambda x: -x[1]["count"]))
        ),
        "device_evo": json.dumps(device_evo),
        "retention": json.dumps(retention),
        "entry_pages": [
            (u, c) for u, c in sorted(entry_pages.items(), key=lambda x: -x[1])
        ][:10],
        "exit_pages": [
            (u, c) for u, c in sorted(exit_pages.items(), key=lambda x: -x[1])
        ][:10],
        "session_depth": session_depth,
        "session_depth_json": json.dumps(session_depth),
        "error_stats": error_stats,
        "page_perf": page_perf,
        "anomalies": anomalies,
        "journeys": compute_user_journeys(start, end),
        "search_queries": get_search_queries(start, end),
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


@login_required
@user_passes_test(lambda u: est_moderateur(u))
def live_stats(request):
    active = count_recent_ips(minutes=5)
    active_15 = count_recent_ips(minutes=15)
    today = date.today()
    entries = _load_entries_public(today)
    total_today = len(entries)
    recent = entries[-10:] if len(entries) > 10 else entries

    def _safe(e: dict) -> dict:
        return {
            "url": e.get("url", "/"),
            "timestamp": e.get("timestamp", ""),
            "browser": e.get("device", {}).get("browser", "?"),
            "city": (e.get("geo") or {}).get("city", "") or "-",
        }

    return JsonResponse(
        {
            "active_5m": active,
            "active_15m": active_15,
            "total_today": total_today,
            "recent": [_safe(e) for e in recent],
        }
    )


def _load_entries_public(d: date) -> list[dict]:
    from analytics.analytics_data import _load_entries as _le

    return _le(d)


@login_required
@user_passes_test(lambda u: est_moderateur(u))
def export_pdf(request):
    period_ = request.GET.get("period", "7")
    days = int(period_) if period_.isdigit() else 7
    today = date.today()
    start = today - timedelta(days=days - 1)
    end = today

    from django.template.loader import render_to_string

    html = render_to_string(
        "analytics/stats_pdf.html",
        {"start": start, "end": end, "generated": today},
    )
    try:
        from weasyprint import HTML

        pdf_bytes = HTML(string=html).write_pdf()
    except ImportError:
        return HttpResponse(
            "WeasyPrint non installe. pip install weasyprint",
            status=500,
        )
    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    filename = f"statistiques_{start.isoformat()}_{end.isoformat()}.pdf"
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp


@login_required
@user_passes_test(lambda u: est_moderateur(u))
def batch_delete(request):
    if request.method != "POST":
        return HttpResponse("Methode non autorisee", status=405)

    date_start = request.POST.get("date_start", "")
    date_end = request.POST.get("date_end", "")

    try:
        start = date.fromisoformat(date_start) if date_start else date.today()
        end = date.fromisoformat(date_end) if date_end else date.today()
    except (ValueError, TypeError):
        messages.error(request, "Dates invalides")
        return redirect("analytics:admin_stats")

    deleted = delete_data_range(start, end)
    if deleted:
        messages.success(
            request,
            f"{deleted} fichier(s) supprime(s) "
            f"du {start.isoformat()} au {end.isoformat()}",
        )
    else:
        messages.warning(request, "Aucune donnee trouvee pour cette periode")
    return redirect("analytics:admin_stats")


@login_required
@user_passes_test(lambda u: est_moderateur(u))
def batch_export(request):
    date_start = request.GET.get("date_start", "")
    date_end = request.GET.get("date_end", "")
    fmt = request.GET.get("format", "json")

    try:
        start = date.fromisoformat(date_start) if date_start else date.today()
        end = date.fromisoformat(date_end) if date_end else date.today()
    except (ValueError, TypeError):
        return HttpResponse("Dates invalides", status=400)

    records = export_range_data(start, end)

    if fmt == "csv":
        import csv
        from io import StringIO

        buf = StringIO()
        if records:
            writer = csv.DictWriter(buf, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
        csv_data = buf.getvalue()
        filename = f"statistiques_{start.isoformat()}_{end.isoformat()}.csv"
        resp = HttpResponse(csv_data, content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp

    if fmt == "zip":
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            d = start
            while d <= end:
                for ext in (".jsonl", ".json"):
                    fpath = ANALYTICS_DIR / f"{d.isoformat()}{ext}"
                    if fpath.exists():
                        zf.write(fpath, fpath.name)
                d += timedelta(days=1)
        buffer.seek(0)
        filename = f"analytics_{start.isoformat()}_{end.isoformat()}.zip"
        resp = HttpResponse(buffer.getvalue(), content_type="application/zip")
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp

    return JsonResponse(
        records, safe=False, json_dumps_params={"ensure_ascii": False, "indent": 2}
    )


@login_required
@user_passes_test(lambda u: est_moderateur(u))
def send_email_report(request):
    if request.method != "POST":
        return HttpResponse("Methode non autorisee", status=405)

    period_ = request.POST.get("period", "7")
    email_to = request.POST.get("email", "")

    try:
        days = int(period_)
    except ValueError:
        days = 7

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

    from django.core.mail import send_mail
    from django.template.loader import render_to_string

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

    if email_to:
        try:
            send_mail(
                subject=(
                    f"[CCSA] Rapport statistiques — "
                    f"{start.isoformat()} au {end.isoformat()}"
                ),
                message="",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_to],
                html_message=html_body,
                fail_silently=False,
            )
            messages.success(request, f"Rapport envoye a {email_to}")
        except Exception as exc:
            messages.error(request, f"Erreur d'envoi : {exc}")
    else:
        messages.warning(request, "Aucune adresse email fournie")

    return redirect("analytics:admin_stats")
