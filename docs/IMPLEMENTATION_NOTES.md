# Implementation Notes

This package adds a self-service GitHub Actions workflow layer on top of the existing Language Discovery app.

## Files to copy into the existing repository

```text
.github/workflows/discover-languages-self-service.yml
tools/build_summary.py
input_examples/domains.csv
docs/GITHUB_SELF_SERVICE_USER_GUIDE.md
```

## What changed

- Adds a manual GitHub Actions workflow intended for non-technical users.
- Supports two input modes: pasted domains or a CSV stored in the repository.
- Produces one downloadable artifact containing `results.zip`.
- Adds `summary.csv` and `summary.md` to make portfolio-level review easier.

## Design choice

This avoids local Python installs, Mac/Windows executable packaging, and persistent web hosting.
