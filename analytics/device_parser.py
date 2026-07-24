import re

_DEVICE_PATTERNS: list[tuple[str, str, str, str]] = [
    (r"iPhone", "mobile", "iOS", "iPhone"),
    (r"iPad", "tablet", "iOS", "iPad"),
    (r"Android.*Mobile", "mobile", "Android", None),
    (r"Android(?!.*Mobile)", "tablet", "Android", None),
    (r"Windows Phone", "mobile", "Windows Phone", None),
    (r"CrOS", "desktop", "ChromeOS", None),
    (r"Linux.*Android", "mobile", "Android", None),
    (r"Linux", "desktop", "Linux", None),
    (r"Macintosh|Mac OS X", "desktop", "macOS", None),
    (r"Windows NT 10", "desktop", "Windows 10", None),
    (r"Windows NT 6\.3", "desktop", "Windows 8.1", None),
    (r"Windows NT 6\.[12]", "desktop", "Windows 7", None),
    (r"Windows NT 6\.0", "desktop", "Windows Vista", None),
    (r"Windows NT 5", "desktop", "Windows XP", None),
    (r"Windows", "desktop", "Windows", None),
]

_BROWSER_PATTERNS: list[tuple[str, str]] = [
    (r"Edg", "Edge"),
    (r"OPR|Opera", "Opera"),
    (r"Chrome", "Chrome"),
    (r"Firefox", "Firefox"),
    (r"Safari", "Safari"),
    (r"SamsungBrowser", "Samsung Internet"),
]

_DEVICE_BRAND: list[tuple[str, str]] = [
    (r"\biPhone\b", "Apple"),
    (r"\biPad\b", "Apple"),
    (r"\bMacintosh\b|\bMac OS X\b", "Apple"),
    (r"\bSamsung\b", "Samsung"),
    (r"\bXiaomi\b", "Xiaomi"),
    (r"\bHuawei\b", "Huawei"),
    (r"\bPixel\b", "Google"),
    (r"\bOnePlus\b", "OnePlus"),
    (r"\bOppo\b", "Oppo"),
    (r"\bVivo\b", "Vivo"),
    (r"\bNokia\b", "Nokia"),
    (r"\bLG\b", "LG"),
    (r"\bSony\b", "Sony"),
    (r"\bHTC\b", "HTC"),
    (r"\bLenovo\b", "Lenovo"),
    (r"\bMotorola\b", "Motorola"),
    (r"\b(Raspberry|Linux)\b", "Linux"),
]

_MODEL_MOBILE: list[tuple[str, str]] = [
    (r"iPhone(\d+,\d+)", "iPhone {model}"),
    (r"Samsung ([\w-]+)", "Samsung {model}"),
    (r"Pixel (\w+)", "Pixel {model}"),
    (r"SM-\w+", None),
]


def parse_user_agent(ua: str) -> dict:
    if not ua:
        return {"type": "desktop", "os": "Inconnu", "browser": "Inconnu", "brand": None}

    device_type = "desktop"
    device_os = None
    device_brand = None
    model = None

    for pattern, dtype, dos, _device_model in _DEVICE_PATTERNS:
        if re.search(pattern, ua, re.IGNORECASE):
            device_type = dtype
            device_os = dos
            break
    if device_os is None:
        device_os = "Inconnu"

    browser = "Inconnu"
    for pattern, bname in _BROWSER_PATTERNS:
        if re.search(pattern, ua, re.IGNORECASE):
            browser = bname
            break

    for pattern, bname in _DEVICE_BRAND:
        if re.search(pattern, ua, re.IGNORECASE):
            device_brand = bname
            break

    for pattern, _mlabel in _MODEL_MOBILE:
        m = re.search(pattern, ua, re.IGNORECASE)
        if m:
            model = m.group(0)
            break

    result: dict = {
        "type": device_type,
        "os": device_os,
        "browser": browser,
        "brand": device_brand,
    }
    if model:
        result["model"] = model
    return result
