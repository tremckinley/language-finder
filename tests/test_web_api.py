from fastapi.testclient import TestClient
from app.api import app, clean_domains

def test_clean_domains_splits_common_formats():
    assert clean_domains(['example.org, nature.org\nexample.com']) == ['example.org','nature.org','example.com']

def test_homepage_serves_html():
    client=TestClient(app)
    response=client.get('/')
    assert response.status_code==200
    assert 'Language Discovery' in response.text
