# GitHub Actions Operator Guide

This repository can run the Language Discovery Engine from the GitHub web interface without requiring an end user to install Python or use a local IDE.

## Manual Run

1. Open the repository in GitHub.
2. Select **Actions**.
3. Select **Discover Published Languages**.
4. Select **Run workflow**.
5. Enter one or more domains, separated by commas, spaces, or line breaks.
6. Run the workflow.
7. Download the workflow artifact named `language-discovery-results` or the custom name provided at launch.

## Scheduled Run

The workflow also includes a weekly scheduled run using `input_examples/domains.csv`. Edit that CSV to maintain a standing list of domains.

## Output Files

- `language_reports.csv` - primary analyst-friendly result
- `language_reports.json` - structured language report
- `discovery_results.csv` - discovery inventory summary
- `discovery_results.json` - full discovery inventory

## Recommended First Review File

Start with `language_reports.csv`.

## Notes

The workflow uses Python and the deterministic crawler package in this repository. It does not use an LLM for language detection.
