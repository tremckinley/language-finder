import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import analyze_domains


class DummyDiscovery:
    def to_dict(self, include_text=False):
        return {"domain": "dummy"}


class DummyReport:
    def to_dict(self):
        return {"domain": "dummy"}


def test_analyze_domains_emits_progress_and_failure_messages(monkeypatch, capsys):
    async def fake_analyze_domain(domain):
        if domain == "bad.example":
            raise RuntimeError("boom")
        return DummyDiscovery(), DummyReport()

    monkeypatch.setattr("main.analyze_domain", fake_analyze_domain)

    discoveries, reports = asyncio.run(analyze_domains(["good.example", "bad.example"]))

    captured = capsys.readouterr()
    assert len(discoveries) == 1
    assert len(reports) == 1
    assert "Starting analysis for domain 1/2: good.example" in captured.err
    assert "Starting analysis for domain 2/2: bad.example" in captured.err
    assert "Failed to analyze domain bad.example" in captured.err
    assert "Completed analysis for domain good.example" in captured.err
