# Codespaces Web App Guide

This guide explains how to run the Language Discovery web app in GitHub Codespaces.

## Start the app

1. Open the repository in GitHub.
2. Select **Code**.
3. Select the **Codespaces** tab.
4. Create or open a codespace.
5. In the terminal, run:

```bash
uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload
```

## Open the web page

The dev container forwards port `8000`. Use the Codespaces port preview/browser prompt to open the web app.

## Use the tool

1. Paste one or more domains in the text box.
2. Select **Analyze domains**.
3. Review the language count and detected languages.
4. Select **Download CSV** to save `language_reports.csv`.

## Notes

- The web app uses the same deterministic Python engine as the CLI and GitHub Actions workflow.
- The front-end is plain HTML, CSS, and JavaScript.
- The backend is FastAPI.
- No LLM is used for language detection.
