from __future__ import annotations
from collections import deque
from urllib.parse import urlparse

from config import DEFAULT_CONFIG, DiscoveryConfig
from discovery.fetcher import AsyncFetcher
from discovery.html import parse_html_evidence
from discovery.robots import robots_url
from discovery.sitemap import default_sitemap_candidates, extract_sitemaps_from_robots, filter_domain_urls, parse_sitemap_xml
from discovery.urls import build_discovery_seed, extract_candidate_language_path, get_host, normalize_url, same_registered_domain
from models import DiscoveryResult, PageEvidence

HTML_TYPES = ("text/html", "application/xhtml+xml")
XML_TYPES = ("xml", "text/plain")

class DomainDiscoverer:
    def __init__(self, config: DiscoveryConfig = DEFAULT_CONFIG):
        self.config = config

    async def discover(self, domain: str) -> DiscoveryResult:
        seed = build_discovery_seed(domain)
        result = DiscoveryResult(
            domain=seed.input_domain,
            normalized_start_url=seed.normalized_url,
            registered_domain=seed.registered_domain,
        )
        result.subdomains.add(seed.host)
        result.discovered_urls.add(seed.normalized_url)

        async with AsyncFetcher(self.config) as fetcher:
            await self._discover_sitemaps(fetcher, seed.normalized_url, result)
            await self._crawl_pages(fetcher, result)
        return result

    async def _discover_sitemaps(self, fetcher: AsyncFetcher, base_url: str, result: DiscoveryResult) -> None:
        candidates = []
        robots = robots_url(base_url)
        robots_result = await fetcher.fetch_text(robots)
        if robots_result.ok and robots_result.text:
            candidates.extend(extract_sitemaps_from_robots(robots_result.text))
        elif robots_result.error:
            result.fetch_errors.append(f"robots: {robots_result.requested_url}: {robots_result.error}")
        candidates.extend(default_sitemap_candidates(base_url))
        candidates = filter_domain_urls([c for c in candidates if c], result.registered_domain)

        queue = deque(candidates)
        seen: set[str] = set()
        while queue and len(seen) < self.config.max_sitemaps and len(result.discovered_urls) < self.config.max_sitemap_urls:
            sitemap_url = queue.popleft()
            if sitemap_url in seen:
                continue
            seen.add(sitemap_url)
            result.sitemap_urls.add(sitemap_url)
            fetched = await fetcher.fetch_text(sitemap_url)
            if not fetched.ok or not fetched.text:
                if fetched.error:
                    result.fetch_errors.append(f"sitemap: {sitemap_url}: {fetched.error}")
                continue
            try:
                parsed = parse_sitemap_xml(fetched.text)
            except Exception as exc:
                result.fetch_errors.append(f"sitemap_parse: {sitemap_url}: {exc.__class__.__name__}")
                continue
            child_sitemaps = filter_domain_urls(parsed.get("sitemaps", []), result.registered_domain)
            urls = filter_domain_urls(parsed.get("urls", []), result.registered_domain)
            for child in child_sitemaps:
                if child not in seen:
                    queue.append(child)
            for url in urls:
                self._record_url(result, url)

    async def _crawl_pages(self, fetcher: AsyncFetcher, result: DiscoveryResult) -> None:
        queue: deque[tuple[str, int]] = deque()
        seed_urls = [result.normalized_start_url] + sorted(result.discovered_urls)[: self.config.max_pages]
        for url in seed_urls:
            normalized = normalize_url(url)
            if normalized:
                queue.append((normalized, 0))
        visited: set[str] = set()
        while queue and len(result.pages) < self.config.max_pages:
            url, depth = queue.popleft()
            if url in visited or not same_registered_domain(url, result.registered_domain):
                continue
            visited.add(url)
            fetched = await fetcher.fetch_text(url)
            page = PageEvidence(url=url, final_url=fetched.final_url, status_code=fetched.status_code, error=fetched.error)
            if not fetched.ok or not fetched.text:
                result.pages.append(page)
                if fetched.error:
                    result.fetch_errors.append(f"page: {url}: {fetched.error}")
                continue
            content_type = (fetched.content_type or "").lower()
            if not any(t in content_type for t in HTML_TYPES) and "<html" not in fetched.text[:1000].lower():
                continue
            evidence = parse_html_evidence(fetched.text, fetched.final_url or url, result.registered_domain)
            page.html_lang = evidence["html_lang"]
            page.hreflang_targets = evidence["hreflangs"]
            page.internal_links = evidence["internal_links"]
            page.visible_text = evidence["visible_text"]
            result.pages.append(page)
            result.hreflang_targets.update(page.hreflang_targets)
            for hreflang_url in evidence["hreflang_urls"]:
                self._record_url(result, hreflang_url)
                if depth < self.config.max_depth:
                    queue.append((hreflang_url, depth + 1))
            for link in list(page.internal_links)[: self.config.max_links_per_page]:
                self._record_url(result, link)
                if depth < self.config.max_depth:
                    queue.append((link, depth + 1))

    def _record_url(self, result: DiscoveryResult, url: str) -> None:
        normalized = normalize_url(url)
        if not normalized or not same_registered_domain(normalized, result.registered_domain):
            return
        result.discovered_urls.add(normalized)
        try:
            result.subdomains.add(get_host(normalized))
        except Exception:
            pass
        candidate = extract_candidate_language_path(normalized)
        if candidate:
            result.candidate_language_paths.add(candidate)
