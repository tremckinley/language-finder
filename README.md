# Language Discovery Batch Isolation Patch

This patch makes multi-domain processing auditable and isolated so every domain is analyzed as if it were running alone.

## Replace in your repository

```text
main.py
```

## Recommended GitHub Actions edit

Add `--debug` to the workflow step that runs `main.py`.

## New debug files

```text
output/debug/<domain>.discovery.json
output/debug/<domain>.language_debug.json
output/debug/batch_manifest.json
```

## Tests included

```text
tests/test_batch_isolation.py
```
