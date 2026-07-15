from discovery.urls import (
    build_discovery_seed,
    extract_candidate_language_path,
    normalize_url,
    same_registered_domain,
)


def test_build_discovery_seed_adds_https():
    seed = build_discovery_seed("www.example.org")
    assert seed.normalized_url == "https://www.example.org/"
    assert seed.registered_domain == "example.org"
    assert seed.host == "www.example.org"


def test_normalize_url_resolves_relative_links():
    assert normalize_url("/es/about", "https://example.org") == "https://example.org/es/about"


def test_same_registered_domain_includes_subdomains():
    assert same_registered_domain("https://fr.example.org/page", "example.org")


def test_candidate_language_path():
    assert extract_candidate_language_path("https://example.org/es-mx/about") == "/es-mx/"
    assert extract_candidate_language_path("https://example.org/about") is None
