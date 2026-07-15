from discovery.html import parse_html_evidence
from language.detector import detect_language_from_url, normalize_language_code, heuristic_detect_text_language
from language.aggregator import LanguageAggregator
from models import DiscoveryResult, PageEvidence


def test_parse_html_evidence():
    html = '''<html lang="es-MX"><head><link rel="alternate" hreflang="fr" href="https://fr.example.org/"></head><body><a href="/en/about">About</a><script>x</script>Hola mundo</body></html>'''
    e = parse_html_evidence(html, 'https://example.org/es/', 'example.org')
    assert e['html_lang'] == 'es-MX'
    assert 'fr' in e['hreflangs']
    assert 'https://example.org/en/about' in e['internal_links']
    assert 'x' not in e['visible_text']


def test_language_code_normalization():
    assert normalize_language_code('es-MX') == 'es'
    assert normalize_language_code('x-default') is None


def test_url_language_detection():
    assert detect_language_from_url('https://fr.example.org/about') == 'fr'
    assert detect_language_from_url('https://example.org/es-mx/about') == 'es'


def test_text_heuristic_detection():
    text = ' '.join(['el la de que y en para con nuestro una'] * 40)
    assert heuristic_detect_text_language(text, min_chars=20) == 'es'


def test_language_aggregation():
    d = DiscoveryResult(domain='example.org', normalized_start_url='https://example.org/', registered_domain='example.org')
    d.discovered_urls.update({'https://example.org/es/about', 'https://fr.example.org/'})
    d.candidate_language_paths.add('/es/')
    d.hreflang_targets.add('fr')
    d.pages.append(PageEvidence(url='https://example.org/', html_lang='en-US'))
    report = LanguageAggregator().aggregate(d)
    assert report.language_count == 3
    assert set(report.languages) == {'English', 'Spanish', 'French'}
