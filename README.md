# Language Finder Vercel Migration

The repository now supports a Vercel-style job flow for self-service analysis while keeping the existing GitHub Actions workflow and summary generation intact.

## What changed

- Added a lightweight job store bridge in [app/vercel_bridge.py](app/vercel_bridge.py) for queued runs and result persistence.
- Added Vercel-ready API entry points in [api/run.py](api/run.py), [api/status.py](api/status.py), and [api/results.py](api/results.py).
- Updated the browser UI in [web/app.js](web/app.js) to submit domains, poll job status, and display results without needing GitHub Pages.
- Added [vercel.json](vercel.json) so the app can be served by Vercel with the new routes.

## Local development

Run the local FastAPI app with:

```bash
uvicorn app.vercel_api:app --reload
```

Then open the browser at http://127.0.0.1:8000/.

## Vercel deployment notes

1. Connect the repository to Vercel.
2. Ensure the project root is the repository root.
3. Set the following environment variables in Vercel:
   - `GITHUB_TOKEN` or `GH_TOKEN`
   - `GITHUB_REPOSITORY`
4. Deploy.

## API shape

- POST /api/run with a JSON body like `{ "domains": ["example.org"] }`
- GET /api/status/{jobId}
- GET /api/results/{jobId}

The job flow preserves the existing summary payload shape so the front end can consume the results immediately.
