from app.api import clean_domains, reports_to_csv


def test_clean_domains_splits_common_formats():
    assert clean_domains(["example.org, nature.org\nexample.com"]) == [
        "example.org",
        "nature.org",
        "example.com",
    ]


def test_reports_to_csv_has_expected_columns():
    csv_text = reports_to_csv([
        {"domain": "example.org", "language_count": 1, "languages": ["English"], "findings": []}
    ])
    assert "domain,language_count,languages,details" in csv_text
    assert "example.org" in csv_text

from fastapi.testclient import TestClient
from app.api import app


def test_homepage_serves_html():
    client = TestClient(app)
    response = client.get('/')
    assert response.status_code == 200
    assert 'Language Discovery' in response.text
