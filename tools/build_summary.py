from __future__ import annotations

import argparse
import csv
from pathlib import Path


def split_languages(value: str) -> list[str]:
    """Return cleaned languages from the language_reports.csv languages column.

    Expected format from the app is semicolon-delimited, for example:
    "English (High, 90%);French (High, 80%)".
    """
    if value is None:
        return []
    cleaned = str(value).strip()
    if cleaned in {"", "[]", "null", "None"}:
        return []
    return [item.strip() for item in cleaned.split(";") if item.strip()]


def parse_reported_count(value: str) -> int:
    try:
        return int(str(value).strip())
    except Exception:
        return 0


def get_domain(row: dict[str, str]) -> str:
    return (
        row.get("domain")
        or row.get("Domain")
        or row.get("Domain Name")
        or row.get("domain_name")
        or ""
    ).strip()


def normalized_language_count(row: dict[str, str], languages: list[str]) -> int:
    """Use the strongest available count.

    This intentionally guards against a known issue where the detailed output
    found multiple languages but the summary counted the row as single-language.
    If the languages column clearly contains multiple semicolon-delimited values,
    that value should win over a lower language_count value.
    """
    reported_count = parse_reported_count(row.get("language_count", "0"))
    return max(reported_count, len(languages))


def build_domain_summary(language_report: Path) -> list[dict[str, str]]:
    with language_report.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    output: list[dict[str, str]] = []
    for row in rows:
        languages = split_languages(row.get("languages", ""))
        output.append(
            {
                "Domain Name": get_domain(row),
                "Language Count": str(normalized_language_count(row, languages)),
                "Languages": "; ".join(languages),
            }
        )
    return output


def write_summary_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Domain Name", "Language Count", "Languages"])
        writer.writeheader()
        writer.writerows(rows)


def write_summary_md(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "## Portfolio summary",
        "",
        "| Domain Name | Language Count | Languages |",
        "|---|---:|---|",
    ]
    for row in rows:
        domain = row["Domain Name"] or "_Unknown domain_"
        count = row["Language Count"] or "0"
        languages = row["Languages"] or "_None over threshold_"
        # Escape pipe characters so the markdown table does not break.
        domain = domain.replace("|", "\\|")
        languages = languages.replace("|", "\\|")
        lines.append(f"| {domain} | {count} | {languages} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build domain-level portfolio summary for Language Discovery output.")
    parser.add_argument("--language-report", required=True)
    parser.add_argument("--summary-output", required=True)
    parser.add_argument("--markdown-output", required=True)
    args = parser.parse_args()

    language_report = Path(args.language_report)
    if not language_report.exists():
        raise SystemExit(f"Language report not found: {language_report}")

    rows = build_domain_summary(language_report)
    write_summary_csv(Path(args.summary_output), rows)
    write_summary_md(Path(args.markdown_output), rows)


if __name__ == "__main__":
    main()
