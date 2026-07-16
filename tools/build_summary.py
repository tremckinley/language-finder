from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

SUMMARY_COLUMNS = ["Domain Name", "Language Count", "Languages", "Review Recommended"]


def clean(value: Any) -> str:
    return str(value or "").strip()


def has_warnings(report: dict[str, Any]) -> bool:
    warnings = report.get("warnings") or []
    return bool(warnings)


def language_labels_from_json(report: dict[str, Any]) -> list[str]:
    """Build display labels from structured findings first.

    The JSON output is preferred over flattened CSV because findings preserve
    one object per language and avoid CSV quoting edge cases.
    """
    findings = report.get("findings") or []
    labels: list[str] = []
    if findings:
        for finding in findings:
            name = clean(finding.get("name"))
            label = clean(finding.get("confidence_label"))
            pct = finding.get("confidence_percent")
            if name and label and pct is not None:
                labels.append(f"{name} ({label}, {pct}%)")
            elif name:
                labels.append(name)
        return labels
    return [clean(item) for item in report.get("languages", []) if clean(item)]


def build_summary_from_json(language_report_json: Path) -> list[dict[str, str]]:
    reports = json.loads(language_report_json.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    for report in reports:
        languages = language_labels_from_json(report)
        rows.append(
            {
                "Domain Name": clean(report.get("domain")),
                "Language Count": str(len(languages)),
                "Languages": "; ".join(languages),
                "Review Recommended": "Yes" if has_warnings(report) or len(languages) == 0 else "No",
            }
        )
    return rows


def parse_int(value: Any) -> int:
    try:
        return int(str(value).strip())
    except Exception:
        return 0


def split_languages(value: Any) -> list[str]:
    raw = clean(value)
    if raw in {"", "[]", "null", "None"}:
        return []
    return [item.strip() for item in raw.split(";") if item.strip()]


def warning_from_csv(value: Any) -> bool:
    raw = clean(value)
    return raw not in {"", "[]", "null", "None"}


def build_summary_from_csv(language_report_csv: Path) -> list[dict[str, str]]:
    with language_report_csv.open("r", encoding="utf-8", newline="") as f:
        source_rows = list(csv.DictReader(f))
    rows: list[dict[str, str]] = []
    for row in source_rows:
        languages = split_languages(row.get("languages", ""))
        count = max(parse_int(row.get("language_count", "0")), len(languages))
        rows.append(
            {
                "Domain Name": clean(row.get("domain") or row.get("Domain Name")),
                "Language Count": str(count),
                "Languages": "; ".join(languages),
                "Review Recommended": "Yes" if warning_from_csv(row.get("warnings", "")) or count == 0 else "No",
            }
        )
    return rows


def write_summary_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_summary_md(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "## Portfolio summary",
        "",
        "| Domain Name | Language Count | Languages | Review Recommended |",
        "|---|---:|---|---|",
    ]
    for row in rows:
        domain = (row.get("Domain Name") or "_Unknown domain_").replace("|", "\\|")
        count = row.get("Language Count") or "0"
        languages = (row.get("Languages") or "_None over threshold_").replace("|", "\\|")
        review = row.get("Review Recommended") or "No"
        lines.append(f"| {domain} | {count} | {languages} | {review} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build V1 primary summary.csv for Language Discovery output.")
    parser.add_argument("--language-report-json")
    parser.add_argument("--language-report-csv")
    parser.add_argument("--summary-output", required=True)
    parser.add_argument("--markdown-output", required=True)
    args = parser.parse_args()

    if args.language_report_json and Path(args.language_report_json).exists():
        rows = build_summary_from_json(Path(args.language_report_json))
    elif args.language_report_csv and Path(args.language_report_csv).exists():
        rows = build_summary_from_csv(Path(args.language_report_csv))
    else:
        raise SystemExit("Provide an existing --language-report-json or --language-report-csv file.")

    write_summary_csv(Path(args.summary_output), rows)
    write_summary_md(Path(args.markdown_output), rows)


if __name__ == "__main__":
    main()
