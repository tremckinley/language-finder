from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any
from urllib import request, error

DEFAULT_STORE_PATH = Path(__file__).resolve().parents[1] / "output" / "vercel_jobs.json"


def _normalize_domains(domains: Any) -> list[str]:
    if domains is None:
        return []
    if isinstance(domains, str):
        values = [domains]
    else:
        values = list(domains)

    out: list[str] = []
    for value in values:
        for token in str(value).replace(",", " ").split():
            if token.strip() and token.lower() != "domain":
                out.append(token.strip())
    return list(dict.fromkeys(out))


def _load_store(store_path: Path) -> dict[str, Any]:
    if store_path.exists():
        try:
            data = json.loads(store_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"jobs": {}}
        if isinstance(data, dict):
            jobs = data.get("jobs", {})
            if isinstance(jobs, dict):
                return {"jobs": jobs}
    return {"jobs": {}}


def _write_store(store_path: Path, store: dict[str, Any]) -> None:
    store_path.parent.mkdir(parents=True, exist_ok=True)
    store_path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def trigger_github_workflow(domains: list[str], job_id: str) -> None:
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    repository = os.getenv("GITHUB_REPOSITORY")
    if not token or not repository:
        return

    payload = json.dumps(
        {
            "ref": "main",
            "inputs": {"domains": "\n".join(domains), "job_id": job_id},
        }
    ).encode("utf-8")

    req = request.Request(
        f"https://api.github.com/repos/{repository}/actions/workflows/discover-languages-self-service.yml/dispatches",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=10):
            return
    except (error.HTTPError, error.URLError, TimeoutError):
        return


def create_job(domains: Any, *, store_path: str | Path | None = None) -> dict[str, Any]:
    path = Path(store_path or DEFAULT_STORE_PATH)
    store = _load_store(path)
    normalized = _normalize_domains(domains)
    job_id = str(uuid.uuid4())[:8]

    job = {
        "jobId": job_id,
        "status": "queued",
        "progress": 0,
        "domains": normalized,
        "results": None,
    }
    store["jobs"][job_id] = job
    _write_store(path, store)
    if normalized:
        trigger_github_workflow(normalized, job_id)
    return job


def get_job_status(job_id: str, *, store_path: str | Path | None = None) -> dict[str, Any]:
    path = Path(store_path or DEFAULT_STORE_PATH)
    store = _load_store(path)
    job = store["jobs"].get(job_id)
    if job is None:
        raise KeyError(job_id)
    return {
        "jobId": job["jobId"],
        "status": job["status"],
        "progress": job.get("progress", 0),
        "domains": job.get("domains", []),
    }


def get_job_result(job_id: str, *, payload: Any = None, store_path: str | Path | None = None) -> dict[str, Any]:
    path = Path(store_path or DEFAULT_STORE_PATH)
    store = _load_store(path)
    job = store["jobs"].get(job_id)
    if job is None:
        raise KeyError(job_id)

    if payload is not None:
        job["results"] = payload
        job["status"] = "completed"
        job["progress"] = 100
        store["jobs"][job_id] = job
        _write_store(path, store)

    return {
        "jobId": job["jobId"],
        "status": job["status"],
        "progress": job.get("progress", 0),
        "results": job.get("results"),
    }
