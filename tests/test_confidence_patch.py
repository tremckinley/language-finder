from language.aggregator import LanguageAggregator
from models import DiscoveryResult, PageEvidence

def test_text_only_spanish_is_suppressed_when_french_url_exists():
    d=DiscoveryResult(domain='example.org', normalized_start_url='https://example.org/', registered_domain='example.org')
    d.discovered_urls.add('https://example.org/fr/page')
    d.candidate_language_paths.add('/fr/')
    text=' '.join(['el la de que y en para con nuestro una']*50)
    d.pages.append(PageEvidence(url='https://example.org/fr/page', final_url='https://example.org/fr/page', html_lang='fr', visible_text=text))
    report=LanguageAggregator().aggregate(d)
    assert report.language_count == 1
    assert report.findings[0].code == 'fr'
    assert 'Spanish' not in ';'.join(report.languages)
    assert any(w['type']=='text_signal_conflict' for w in report.warnings)

def test_confidence_labels_and_percentages_display():
    d=DiscoveryResult(domain='example.org', normalized_start_url='https://example.org/', registered_domain='example.org')
    d.hreflang_targets.update({'en','fr'})
    d.candidate_language_paths.add('/fr/')
    d.pages.append(PageEvidence(url='https://example.org/', html_lang='en'))
    report=LanguageAggregator().aggregate(d)
    assert all(f.confidence_label in {'High','Medium','Low'} for f in report.findings)
    assert any('%' in lang for lang in report.languages)
