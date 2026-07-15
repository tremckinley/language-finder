"""URL normalization and domain-boundary helpers."""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse, urlunparse

try:
    import tldextract
except Exception:  # pragma: no cover - fallback for minimal environments
    tldextract = None

from models import DiscoverySeed

LANG_PATH_RE = re.compile(r"^/([a-z]{2})(?:[-_]([a-z]{2}))?(?:/|$)", re.IGNORECASE)
TRACKING_PARAMS_PREFIXES = ("utm_",)
TRACKING_PARAMS_EXACT = {"fbclid", "gclid", "msclkid"}


def ensure_scheme(value: str, default_scheme: str = "https") -> str:
    """Return a URL-like value with an HTTP scheme."""
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("Domain or URL cannot be empty.")
    if not cleaned.startswith(("http://", "https://")):
        cleaned = f"{default_scheme}://{cleaned}"
    return cleaned


def strip_default_port(netloc: str) -> str:
    if netloc.endswith(":443"):
        return netloc[:-4]
    if netloc.endswith(":80"):
        return netloc[:-3]
    return netloc


def normalize_url(url: str, base_url: str | None = None, keep_query: bool = False) -> str | None:
    """Normalize a URL for de-duplication.

    Returns None for non-http(s), mailto, tel, javascript, and malformed values.
    """
    if not url:
        return None
    candidate = url.strip()
    if candidate.startswith(("mailto:", "tel:", "javascript:", "#")):
        return None
    if base_url:
        candidate = urljoin(base_url, candidate)
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None

    scheme = parsed.scheme.lower()
    netloc = strip_default_port(parsed.netloc.lower())
    path = parsed.path or "/"
    # remove duplicate slashes within path while preserving root
    path = re.sub(r"/{2,}", "/", path)
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/") + "/"

    query = parsed.query if keep_query else ""
    return urlunparse((scheme, netloc, path, "", query, ""))


def get_host(url: str) -> str:
    parsed = urlparse(ensure_scheme(url))
    return strip_default_port(parsed.netloc.lower())


def get_registered_domain(host_or_url: str) -> str:
    """Return the registrable domain where possible.

    Uses tldextract when available, with a conservative fallback for simple hosts.
    """
    host = get_host(host_or_url) if "://" in host_or_url else host_or_url.lower().strip()
    host = strip_default_port(host)
    if tldextract is not None:
        ext = tldextract.extract(host)
        if ext.domain and ext.suffix:
            return f"{ext.domain}.{ext.suffix}"
    pieces = [p for p in host.split(".") if p]
    if len(pieces) >= 2:
        return ".".join(pieces[-2:])
    return host


def same_registered_domain(url: str, registered_domain: str) -> bool:
    try:
        return get_registered_domain(url) == registered_domain.lower().strip()
    except Exception:
        return False


def build_discovery_seed(domain_or_url: str) -> DiscoverySeed:
    normalized = normalize_url(ensure_scheme(domain_or_url))
    if normalized is None:
        raise ValueError(f"Could not normalize input: {domain_or_url}")
    host = get_host(normalized)
    registered_domain = get_registered_domain(host)
    return DiscoverySeed(
        input_domain=domain_or_url,
        normalized_url=normalized,
        registered_domain=registered_domain,
        host=host,
    )


def extract_candidate_language_path(url: str) -> str | None:
    """Return a leading language-like path namespace, if present.

    Examples:
        https://example.org/en/about -> /en/
        https://example.org/es-mx/foo -> /es-mx/
    """
    parsed = urlparse(url)
    match = LANG_PATH_RE.match(parsed.path or "")
    if not match:
        return None
    language = match.group(1).lower()
    region = match.group(2).lower() if match.group(2) else None
    return f"/{language}-{region}/" if region else f"/{language}/"
