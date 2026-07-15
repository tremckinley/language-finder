from __future__ import annotations
from config import DEFAULT_CONFIG, DiscoveryConfig
from language.detector import detect_language_from_url, heuristic_detect_text_language, language_name, normalize_language_code
from models import DiscoveryResult, LanguageFinding, LanguageReport

SOURCE_POINTS = {
    "hreflang": 100,
    "html_lang": 60,
    "url_pattern": 35,
    "text_heuristic": 25,
}

class LanguageAggregator:
    def __init__(self, config: DiscoveryConfig = DEFAULT_CONFIG):
        self.config = config

    def aggregate(self, discovery: DiscoveryResult) -> LanguageReport:
        findings: dict[str, LanguageFinding] = {}
        def add(code: str | None, source: str, url: str | None = None) -> None:
            if not code:
                return
            finding = findings.setdefault(code, LanguageFinding(code=code, name=language_name(code)))
            finding.confidence += SOURCE_POINTS.get(source, 0)
            finding.sources.add(source)
            if url:
                finding.sample_urls.add(url)

        for target in discovery.hreflang_targets:
            add(normalize_language_code(target), "hreflang")
        for path in discovery.candidate_language_paths:
            add(normalize_language_code(path.strip("/").split("-", 1)[0]), "url_pattern")
        for url in discovery.discovered_urls:
            add(detect_language_from_url(url), "url_pattern", url)
        for page in discovery.pages:
            page_url = page.final_url or page.url
            add(normalize_language_code(page.html_lang), "html_lang", page_url)
            for hreflang in page.hreflang_targets:
                add(normalize_language_code(hreflang), "hreflang", page_url)
            add(detect_language_from_url(page_url), "url_pattern", page_url)
            add(heuristic_detect_text_language(page.visible_text or "", self.config.min_text_chars_for_detection), "text_heuristic", page_url)

        final = [f for f in findings.values() if f.confidence >= self.config.language_confidence_threshold]
        final.sort(key=lambda f: (-f.confidence, f.name))
        return LanguageReport(
            domain=discovery.domain,
            language_count=len(final),
            languages=[f.name for f in final],
            findings=final,
            discovery_counts=discovery.to_dict().get("counts", {}),
        )
