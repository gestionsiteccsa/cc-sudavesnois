from django.shortcuts import render

from search.models import SearchConfigModel
from search.services import RateLimitService, SearchService


def search_view(request):
    client_ip = request.META.get("REMOTE_ADDR") or "unknown"

    if not RateLimitService.is_allowed(client_ip):
        return render(
            request,
            "home/search_results.html",
            {
                "query": "",
                "results": [],
                "count": 0,
                "page_obj": None,
                "rate_limited": True,
            },
            status=429,
        )

    config = SearchConfigModel.get_config()
    raw_query = request.GET.get("q", "")

    result = SearchService.execute(raw_query, config)

    if result is None:
        too_short = (
            bool(raw_query.strip()) and len(raw_query.strip()) < config.min_query_length
        )
        return render(
            request,
            "home/search_results.html",
            {
                "query": raw_query.strip(),
                "results": [],
                "count": 0,
                "page_obj": None,
                "too_short": too_short,
                "min_query_length": config.min_query_length,
            },
        )

    page_number = request.GET.get("page", 1)
    page_obj = result["paginator"].get_page(page_number)

    return render(
        request,
        "home/search_results.html",
        {
            "query": result["query"],
            "results": page_obj,
            "count": result["count"],
            "page_obj": page_obj,
        },
    )
