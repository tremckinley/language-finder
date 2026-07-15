# Language Discovery Patched App

Deterministic multilingual domain discovery with patched confidence behavior.

## Patch behavior

- Text heuristics can no longer create new language findings.
- Trusted evidence creates languages: `hreflang`, `<html lang>`, `/fr/` style URL paths, and language subdomains.
- Text detection is supplemental only.
- Conflicting text signals are warnings.
- Confidence is displayed as a percentage plus High/Medium/Low label.

## Codespaces run

```bash
uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload
```

## CLI run

```bash
python main.py --domain example.org --output-dir output
```
