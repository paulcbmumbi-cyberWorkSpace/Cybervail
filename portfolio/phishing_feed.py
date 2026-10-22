import logging
from datetime import datetime, timezone
from urllib.error import URLError
from urllib.request import Request, urlopen
from urllib.parse import urlsplit

from django.core.cache import cache


logger = logging.getLogger(__name__)

FEED_URL = "https://raw.githubusercontent.com/openphish/public_feed/refs/heads/main/feed.txt"
CACHE_KEY = "portfolio:zambia-phishing-feed"
STALE_CACHE_KEY = "portfolio:zambia-phishing-feed:last-success"
CACHE_SECONDS = 15 * 60
MAX_FEED_BYTES = 4 * 1024 * 1024
ZAMBIA_INDICATORS = {
    "zambia": "Zambia keyword",
    "zanaco": "Zanaco keyword",
    "zamtel": "Zamtel keyword",
    "mtnzambia": "MTN Zambia keyword",
    "airtelzambia": "Airtel Zambia keyword",
    "zra": "ZRA keyword",
}


def _zambia_indicator(hostname):
    hostname = hostname.lower().rstrip(".")

    if hostname.endswith(".zm"):
        return ".zm domain"

    for indicator, label in ZAMBIA_INDICATORS.items():
        if indicator in hostname:
            return label

    return None


def _defang_host(hostname):
    return hostname.replace(".", "[.]").replace(":", "[:]")


def _fetch_feed():
    request = Request(
        FEED_URL,
        headers={"User-Agent": "Cybervail-Zambia-Awareness/1.0"},
    )

    with urlopen(request, timeout=12) as response:
        content = response.read(MAX_FEED_BYTES + 1)

    if len(content) > MAX_FEED_BYTES:
        raise ValueError("The phishing feed exceeded the maximum accepted size.")

    lines = content.decode("utf-8").splitlines()
    if not lines:
        raise ValueError("The phishing feed returned no entries.")

    entries = []
    seen_hosts = set()

    for line in lines:
        try:
            parsed = urlsplit(line.strip())
            if parsed.scheme not in {"http", "https"} or not parsed.hostname:
                continue
            hostname = parsed.hostname.encode("idna").decode("ascii").lower()
        except (UnicodeError, ValueError):
            continue

        indicator = _zambia_indicator(hostname)
        if not indicator or hostname in seen_hosts:
            continue

        seen_hosts.add(hostname)
        entries.append(
            {
                "domain": _defang_host(hostname),
                "indicator": indicator,
            }
        )

    return {
        "status": "live",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "source": "OpenPhish community feed",
        "source_url": FEED_URL,
        "feed_entries_scanned": len(lines),
        "match_count": len(entries),
        "entries": entries[:100],
        "error": "",
    }


def get_zambia_phishing_feed():
    cached_data = cache.get(CACHE_KEY)
    if cached_data is not None:
        return cached_data

    try:
        data = _fetch_feed()
    except (OSError, UnicodeError, URLError, ValueError):
        logger.exception("Unable to refresh the OpenPhish community feed.")
        stale_data = cache.get(STALE_CACHE_KEY)
        if stale_data is not None:
            stale_data = {**stale_data, "status": "stale"}
            stale_data["error"] = (
                "The live feed could not be refreshed. Showing the last "
                "successful snapshot instead."
            )
            cache.set(CACHE_KEY, stale_data, 60)
            return stale_data

        data = {
            "status": "unavailable",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "source": "OpenPhish community feed",
            "source_url": FEED_URL,
            "feed_entries_scanned": 0,
            "match_count": 0,
            "entries": [],
            "error": (
                "The phishing feed is temporarily unavailable. Please try again later."
            ),
        }
        cache.set(CACHE_KEY, data, 60)
        return data

    cache.set(CACHE_KEY, data, CACHE_SECONDS)
    cache.set(STALE_CACHE_KEY, data, 24 * 60 * 60)
    return data
