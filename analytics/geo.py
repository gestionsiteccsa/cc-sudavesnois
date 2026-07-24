from django.conf import settings

GEOIP_DB = settings.BASE_DIR / "geoip" / "GeoLite2-City.mmdb"
_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        import geoip2.database

        if GEOIP_DB.exists():
            _reader = geoip2.database.Reader(str(GEOIP_DB))
    return _reader


def lookup(ip: str) -> dict | None:
    if not ip or ip == "unknown":
        return None
    reader = _get_reader()
    if reader is None:
        return None
    try:
        response = reader.city(ip)
        result: dict = {}
        if response.country and response.country.iso_code:
            result["country"] = response.country.iso_code
        if response.country and response.country.name:
            result["country_name"] = response.country.name
        if response.subdivisions and len(response.subdivisions) > 0:
            result["region"] = response.subdivisions[0].name
            result["region_code"] = response.subdivisions[0].iso_code
        if response.city and response.city.name:
            result["city"] = response.city.name
        if response.postal and response.postal.code:
            result["postal"] = response.postal.code
        if response.location:
            if response.location.latitude:
                result["lat"] = round(response.location.latitude, 4)
            if response.location.longitude:
                result["lon"] = round(response.location.longitude, 4)
            if response.location.time_zone:
                result["timezone"] = response.location.time_zone
        return result if result else None
    except Exception:
        return None
