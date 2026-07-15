from __future__ import annotations
import re
from bs4 import BeautifulSoup
from discovery.urls import normalize_url, same_registered_domain

SPACE_RE = re.compile(r"\s+")

def parse_html_evidence(html: str, page_url: str, registered_domain: str) -> dict:
    soup = BeautifulSoup(html or "", "lxml")
    html_lang = None
    if soup.html and soup.html.has_attr("lang"):
        html_lang = str(soup.html.get("lang") or "").strip() or None

    hreflangs: set[str] = set()
    hreflang_urls: set[str] = set()
    for tag in soup.find_all("link"):
        rel = " ".join(tag.get("rel", [])) if isinstance(tag.get("rel"), list) else str(tag.get("rel", ""))
        if "alternate" not in rel.lower():
            continue
        hreflang = str(tag.get("hreflang") or "").strip()
        href = tag.get("href")
        if hreflang:
            hreflangs.add(hreflang)
        if href:
            normalized = normalize_url(str(href), base_url=page_url)
            if normalized and same_registered_domain(normalized, registered_domain):
                hreflang_urls.add(normalized)

    links: set[str] = set()
    for a in soup.find_all("a", href=True):
        normalized = normalize_url(str(a.get("href")), base_url=page_url)
        if normalized and same_registered_domain(normalized, registered_domain):
            links.add(normalized)

    for bad in soup(["script", "style", "noscript", "svg"]):
        bad.decompose()
    visible_text = SPACE_RE.sub(" ", soup.get_text(" ")).strip()
    return {
        "html_lang": html_lang,
        "hreflangs": hreflangs,
        "hreflang_urls": hreflang_urls,
        "internal_links": links,
        "visible_text": visible_text,
    }
