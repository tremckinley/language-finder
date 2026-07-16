from pathlib import Path
from tools.build_summary import build_domain_summary


def test_multilingual_count_uses_languages_column_when_reported_count_is_wrong(tmp_path: Path):
    report = tmp_path / "language_reports.csv"
    report.write_text(
        'domain,language_count,languages,warnings\n'
        'example.org,1,"English (High, 90%);French (High, 85%)",[]\n',
        encoding="utf-8",
    )
    rows = build_domain_summary(report)
    assert rows == [
        {
            "Domain Name": "example.org",
            "Language Count": "2",
            "Languages": "English (High, 90%); French (High, 85%)",
        }
    ]


def test_summary_table_columns_are_domain_count_languages(tmp_path: Path):
    report = tmp_path / "language_reports.csv"
    report.write_text('domain,language_count,languages\nexample.com,1,"English (High, 90%)"\n', encoding="utf-8")
    rows = build_domain_summary(report)
    assert list(rows[0].keys()) == ["Domain Name", "Language Count", "Languages"]
