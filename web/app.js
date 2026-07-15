const analyzeButton = document.getElementById('analyzeButton');
const downloadButton = document.getElementById('downloadButton');
const statusEl = document.getElementById('status');
const resultsEl = document.getElementById('results');
const resultCountEl = document.getElementById('resultCount');
const domainsEl = document.getElementById('domains');
let latestCsv = '';

function parseDomains(value) {
  return value.split(/[\s,]+/).map(x => x.trim()).filter(Boolean);
}

function setStatus(message) {
  statusEl.textContent = message;
}

function renderResults(reports) {
  resultCountEl.textContent = `${reports.length} domain${reports.length === 1 ? '' : 's'}`;
  if (!reports.length) {
    resultsEl.className = 'results empty';
    resultsEl.textContent = 'No results yet.';
    return;
  }
  resultsEl.className = 'results';
  resultsEl.innerHTML = reports.map(report => {
    const languages = report.languages && report.languages.length ? report.languages : ['No languages over threshold'];
    const chips = languages.map(lang => `<span class="language-chip">${escapeHtml(lang)}</span>`).join('');
    const details = JSON.stringify(report.findings || [], null, 2);
    return `
      <article class="result-item">
        <div class="result-top">
          <div class="domain">${escapeHtml(report.domain)}</div>
          <span class="pill">${report.language_count} language${report.language_count === 1 ? '' : 's'}</span>
        </div>
        <div class="languages">${chips}</div>
        <details>
          <summary>Evidence details</summary>
          <pre>${escapeHtml(details)}</pre>
        </details>
      </article>
    `;
  }).join('');
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function downloadCsv() {
  if (!latestCsv) return;
  const blob = new Blob([latestCsv], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'language_reports.csv';
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

analyzeButton.addEventListener('click', async () => {
  const domains = parseDomains(domainsEl.value);
  if (!domains.length) {
    setStatus('Enter at least one domain.');
    return;
  }
  analyzeButton.disabled = true;
  downloadButton.disabled = true;
  latestCsv = '';
  setStatus(`Analyzing ${domains.length} domain${domains.length === 1 ? '' : 's'}...`);
  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domains })
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Request failed: ${response.status}`);
    }
    const payload = await response.json();
    latestCsv = payload.csv || '';
    renderResults(payload.reports || []);
    downloadButton.disabled = !latestCsv;
    setStatus('Analysis complete.');
  } catch (error) {
    setStatus(error.message || 'Analysis failed.');
  } finally {
    analyzeButton.disabled = false;
  }
});

downloadButton.addEventListener('click', downloadCsv);
