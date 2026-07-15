from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from main import analyze_domains

ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "web"

app = FastAPI(
    title="Language Discovery Web App",
    description="Simple HTML front-end for the deterministic Language Discovery Engine.",
    version="0.3.0",
)

app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")


class AnalyzeRequest(BaseModel):
    domains: list[str] = Field(default_factory=list, description="Domains to analyze")


class AnalyzeResponse(BaseModel):
    reports: list[dict[str, Any]]
    csv: str


def clean_domains(values: list[str]) -> list[str]:
    cleaned: list[str] = []
    for value in values:
        for token in str(value).replace(",", " ").split():
            token = token.strip()
            if token and token.lower() != "domain":
                cleaned.append(token)
    return list(dict.fromkeys(cleaned))


def reports_to_csv(reports: list[dict[str, Any]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=["domain", "language_count", "languages", "details"])
    writer.writeheader()
    for report in reports:
        writer.writerow(
            {
                "domain": report.get("domain", ""),
                "language_count": report.get("language_count", 0),
                "languages": ";".join(report.get("languages", [])),
                "details": report.get("findings", []),
            }
        )
    return buffer.getvalue()


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return (WEB_DIR / "index.html").read_text(encoding="utf-8")


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    domains = clean_domains(request.domains)
    if not domains:
        raise HTTPException(status_code=400, detail="Provide at least one domain.")
    discoveries, report_objects = await analyze_domains(domains)
    reports = [report.to_dict() for report in report_objects]
    return AnalyzeResponse(reports=reports, csv=reports_to_csv(reports))


@app.post("/api/analyze.csv", response_class=PlainTextResponse)
async def analyze_csv(request: AnalyzeRequest) -> PlainTextResponse:
    domains = clean_domains(request.domains)
    if not domains:
        raise HTTPException(status_code=400, detail="Provide at least one domain.")
    discoveries, report_objects = await analyze_domains(domains)
    reports = [report.to_dict() for report in report_objects]
    return PlainTextResponse(
        reports_to_csv(reports),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=language_reports.csv"},
    )
