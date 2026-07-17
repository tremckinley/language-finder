const DATA_URL = "data/summary.json";
const WORKFLOW_URL = "../actions/workflows/discover-languages-self-service.yml";

const els = {
  domains: document.getElementById("domains"),
  runButton: document.getElementById("runButton"),
  refreshButton: document.getElementById("refreshButton"),
  status: document.getElementById("status"),
  runningPanel: document.getElementById("runningPanel"),
  resultsPanel: document.getElementById("resultsPanel"),
  progressBar: document.getElementById("progressBar"),
  progressText: document.getElementById("progressText"),
  resultsBody: document.getElementById("resultsBody"),
  downloadButton: document.getElementById("downloadButton"),
};

let latestRows = [];
let fakeProgressTimer = null;

function parseDomains(value) {
  return value
    .split(/[\s,]+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function normalizeRow(row) {
  return {
    domain: row.domain || row.DomainName || row["Domain Name"] || "",
    count: row.languageCount || row.LanguageCount || row["Language Count"] || "",
    languages: row.languages || row.Languages || "",
    review: row.reviewRecommended || row.ReviewRecommended || row["Review Recommended"] || "No",
  };
}

async function loadResults() {
  try {
    const response = await fetch(`${DATA_URL}?v=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) throw new Error("No published results found yet.");
    const data = await response.json();
    latestRows = Array.isArray(data) ? data.map(normalizeRow) : [];
    renderTable(latestRows);
    els.resultsPanel.classList.toggle("hidden", latestRows.length === 0);
    els.status.textContent = latestRows.length
      ? `Loaded latest results for ${latestRows.length} domain${latestRows.length === 1 ? "" : "s"}.`
      : "No results found in summary.json.";
  } catch (error) {
    latestRows = [];
    els.resultsPanel.classList.add("hidden");
    els.status.textContent = error.message;
  }
}

function renderTable(rows) {
  els.resultsBody.innerHTML = rows
    .map(
      (row) => `
        <tr>
          <td>${escapeHtml(row.domain)}</td>
          <td class="countCell">${escapeHtml(row.count)}</td>
          <td>${escapeHtml(row.languages || "—")}</td>
          <td class="reviewCell ${row.review === "Yes" ? "reviewYes" : "reviewNo"}">${escapeHtml(row.review)}</td>
        </tr>
      `
    )
    .join("");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function csvEscape(value) {
  const str = String(value ?? "");
  return /[",\n]/.test(str) ? `"${str.replaceAll('"', '""')}"` : str;
}

function rowsToCsv(rows) {
  const header = ["Domain Name", "Language Count", "Languages", "Review Recommended"];
  const lines = [header, ...rows.map((row) => [row.domain, row.count, row.languages, row.review])];
  return lines.map((cols) => cols.map(csvEscape).join(",")).join("\n");
}

function downloadCsv() {
  if (!latestRows.length) return;
  const blob = new Blob([rowsToCsv(latestRows)], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "summary.csv";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function showWaitingState() {
  els.runningPanel.classList.remove("hidden");
  els.progressBar.style.width = "10%";
  els.progressText.textContent = "Open the workflow, run it, then return here and refresh results.";
  let progress = 10;
  clearInterval(fakeProgressTimer);
  fakeProgressTimer = setInterval(() => {
    progress = Math.min(progress + 6, 88);
    els.progressBar.style.width = `${progress}%`;
  }, 1200);
}

function runAnalysis() {
  const domains = parseDomains(els.domains.value);
  if (!domains.length) {
    alert("Please enter at least one domain.");
    return;
  }

  showWaitingState();
  els.status.textContent = "Workflow page opened. Paste the same domains there, run the workflow, then refresh this page.";
  window.open(WORKFLOW_URL, "_blank");
}

els.runButton.addEventListener("click", runAnalysis);
els.refreshButton.addEventListener("click", loadResults);
els.downloadButton.addEventListener("click", downloadCsv);

loadResults();
