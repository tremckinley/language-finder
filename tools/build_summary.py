from __future__ import annotations

import argparse
import csv
from pathlib import Path


def parse_int(value: str) -> int:
    try:
        return int(str(value).strip())
    except Exception:
        return 0


def looks_like_warning(value: str) -> bool:
    cleaned = str(value or "").strip()
    return cleaned not in {"", "[]", "null", "None"}


def build_summary(language_report: Path) -> list[tuple[str, str]]:
    with language_report.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    total = len(rows)
    single = 0
    multilingual = 0
    review_required = 0
    zero = 0

    for row in rows:
        count = parse_int(row.get("language_count", "0"))
        if count == 0:
            zero += 1
        elif count == 1:
            single += 1
        elif count > 1:
            multilingual += 1
        if looks_like_warning(row.get("warnings", "")):
            review_required += 1

    return [
        ("Domains analyzed", str(total)),
        ("Single-language sites", str(single)),
        ("Multilingual sites", str(multilingual)),
        ("No language over threshold", str(zero)),
        ("Review recommended", str(review_required)),
    ]


def write_summary_csv(path: Path, summary: list[tuple[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        writer.writerows(summary)


def write_summary_md(path: Path, summary: list[tuple[str, str]]) -> None:
    lines = ["## Portfolio summary", "", "| Metric | Value |", "|---|---:|"]
    for metric, value in summary:
        lines.append(f"| {metric} | {value} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build summary files for Language Discovery output.")
    parser.add_argument("--language-report", required=True)
    parser.add_argument("--summary-output", required=True)
    parser.add_argument("--markdown-output", required=True)
    args = parser.parse_args()

    language_report = Path(args.language_report)
    if not language_report.exists():
        raise SystemExit(f"Language report not found: {language_report}")

    summary = build_summary(language_report)
    write_summary_csv(Path(args.summary_output), summary)
    write_summary_md(Path(args.markdown_output), summary)


if __name__ == "__main__":
    main()
