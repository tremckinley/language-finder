# Language Discovery v1

Language Discovery is a deterministic portfolio-scanning tool that identifies published languages across one or more domains and produces analyst-friendly CSV output.

## Primary deliverable

The primary output file is:

```text
summary.csv
```

It contains four columns:

```text
Domain Name | Language Count | Languages | Review Recommended
```

Use `summary.csv` first. The other files are supporting evidence and debugging artifacts.

## What the tool does

- Reads a list of domains from pasted GitHub Actions input or a repository CSV.
- Crawls each domain as an isolated job so multi-domain runs behave like repeated single-domain runs.
- Checks trusted language evidence such as `hreflang`, `<html lang>`, language URL paths, and language subdomains.
- Produces a concise portfolio summary for SEO or content review.
- Writes debug files for auditability.

## What the tool does not do

- It does not evaluate translation quality.
- It does not guarantee every page on a site was crawled.
- It does not use AI or an LLM to infer languages.
- It does not replace manual review when warning signals are present.

## GitHub Actions usage

1. Open the repository in GitHub.
2. Select **Actions**.
3. Select **Discover Published Languages - Self Service**.
4. Select **Run workflow**.
5. Choose an input mode:
   - `paste_domains` — paste domains into the workflow form.
   - `repository_csv` — run against a CSV already committed to the repository.
6. Run the workflow.
7. Open the completed run.
8. Download the artifact named `language-discovery-results`.
9. Unzip `results.zip`.
10. Open `summary.csv` first.

## Expected input CSV format

```csv
domain
example.org
gymshark.com
```

## Review Recommended

`Review Recommended` is set to `Yes` when the run produced warnings for that domain or when no language was found over the reporting threshold.

Use this column to quickly identify domains that should receive manual review.

## Supporting files

The result package may also include:

```text
language_reports.csv
language_reports.json
discovery_results.csv
discovery_results.json
summary.md
debug/
```

These files are useful for troubleshooting, but `summary.csv` is the intended v1 reviewer-facing output.

## Local CLI usage

```bash
python main.py --input input/domains.csv --output-dir output --debug
```

Then open:

```text
output/summary.csv
```
