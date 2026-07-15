# Language Discovery Engine - Phase 2 Complete Build

A deterministic Python engine for discovering whether a domain ecosystem publishes pages in multiple languages.

## Current Capabilities

- Normalizes root domains and URLs
- Treats subdomains as part of the registered-domain ecosystem
- Reads `robots.txt` sitemap declarations
- Parses standard sitemaps and sitemap indexes recursively
- Crawls a bounded number of HTML pages
- Extracts `hreflang`, `<html lang>`, internal links, and visible text
- Aggregates likely published languages using deterministic confidence scoring
- Exports JSON and CSV reports

## Run

```bash
pip install -r requirements.txt
python main.py --domain example.org --output-dir output
```

Batch input:

```bash
python main.py --input domains.csv --output-dir output
```

## Primary Output

`output/language_reports.csv`

Columns:

- domain
- language_count
- languages
- details

## Notes

This build is deterministic and does not use an LLM for language detection. Text detection is intentionally conservative and supplemental; high-confidence signals are `hreflang`, `<html lang>`, and URL/subdomain patterns.
