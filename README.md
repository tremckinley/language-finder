# GitHub Pages Integration Patch

This patch completes the immediate next task:

1. Generate `summary.json` from `language_reports.json`.
2. Publish `summary.json` to `docs/data/summary.json`.
3. Update the front-end so it loads latest results from `docs/data/summary.json`.

## Files to copy into your repository

```text
docs/index.html
docs/styles.css
docs/app.js
docs/data/summary.json
tools/build_summary.py
.github/workflows/discover-languages-self-service.yml
```

## GitHub Pages setup

In your repository:

1. Go to **Settings**.
2. Go to **Pages**.
3. Choose **Deploy from a branch**.
4. Select branch `main`.
5. Select folder `/docs`.
6. Save.

## How the page works

- The page loads `data/summary.json` when it opens.
- The results table is populated from that JSON file.
- The Run Analysis button opens the GitHub Actions workflow page.
- After the workflow completes, the workflow commits a new `docs/data/summary.json`.
- The user returns to the page and clicks **Refresh Results**.

## Important security note

This version does not store GitHub tokens in browser code. That is intentional.
