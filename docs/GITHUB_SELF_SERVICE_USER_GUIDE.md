# Language Discovery GitHub Self-Service Guide

This workflow lets a non-technical user run the language-discovery tool from the GitHub web interface without installing Python or downloading an executable.

## Option 1: Paste domains into the workflow

1. Open the repository in GitHub.
2. Select **Actions**.
3. Select **Discover Published Languages - Self Service**.
4. Select **Run workflow**.
5. Set **source** to `paste_domains`.
6. Paste domains into the **domains** field.
7. Run the workflow.
8. Open the completed workflow run.
9. Download the artifact named `language-discovery-results`.
10. Unzip `results.zip` and open `language_reports.csv`.

## Option 2: Use a CSV already in the repository

1. Add or update a CSV file in the repository, for example `input_examples/domains.csv`.
2. Open **Actions**.
3. Select **Discover Published Languages - Self Service**.
4. Select **Run workflow**.
5. Set **source** to `repository_csv`.
6. Confirm the **csv_path** value.
7. Run the workflow.
8. Download the artifact and open `language_reports.csv`.

## Expected CSV format

```csv
domain
example.org
example.com
```

## Output files

The downloaded `results.zip` contains:

- `language_reports.csv` - primary user-facing output
- `language_reports.json` - structured language report
- `discovery_results.csv` - discovery summary
- `discovery_results.json` - full discovery details
- `summary.csv` - portfolio counts
- `summary.md` - GitHub run-summary version of portfolio counts

## Important note

GitHub manual workflow inputs support string, boolean, choice, and environment-style inputs. They do not provide a native file-upload field in the manual workflow form, so this package supports either pasted domains or a CSV that already exists in the repository.
