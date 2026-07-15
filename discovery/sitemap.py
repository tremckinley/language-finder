from __future__ import annotations
import gzip
from xml.etree import ElementTree as ET
from discovery.urls import normalize_url, same_registered_domain

DEFAULT_SITEMAPS = ["/sitemap.xml", "/sitemap_index.xml"]

def extract_sitemaps_from_robots(text: str) -> list[str]:
    results: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.lower().startswith("sitemap:"):
            value = line.split(":", 1)[1].strip()
            if value:
                results.append(value)
    return list(dict.fromkeys(results))

def decode_sitemap_payload(payload: str | bytes) -> str:
    if isinstance(payload, bytes):
        if payload[:2] == b"\x1f\x8b":
            return gzip.decompress(payload).decode("utf-8", errors="replace")
        return payload.decode("utf-8", errors="replace")
    return payload

def parse_sitemap_xml(xml_text: str | bytes) -> dict[str, list[str]]:
    xml = decode_sitemap_payload(xml_text).strip()
    if not xml:
        return {"urls": [], "sitemaps": []}
    root = ET.fromstring(xml)
    tag = root.tag.lower()
    is_index = tag.endswith("sitemapindex")
    urls: list[str] = []
    sitemaps: list[str] = []
    for loc in root.findall(".//{*}loc"):
        value = (loc.text or "").strip()
        if not value:
            continue
        if is_index:
            sitemaps.append(value)
        else:
            urls.append(value)
    return {"urls": list(dict.fromkeys(urls)), "sitemaps": list(dict.fromkeys(sitemaps))}

def default_sitemap_candidates(base_url: str) -> list[str]:
    return [normalize_url(path, base_url=base_url) for path in DEFAULT_SITEMAPS]

def filter_domain_urls(urls: list[str], registered_domain: str) -> list[str]:
    filtered = []
    for url in urls:
        normalized = normalize_url(url)
        if normalized and same_registered_domain(normalized, registered_domain):
            filtered.append(normalized)
    return list(dict.fromkeys(filtered))
