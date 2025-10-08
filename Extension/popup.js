document.addEventListener('DOMContentLoaded', async () => {
  const data = await chrome.storage.local.get(['lastIdentifier', 'triggerPopup']);
  if (data.triggerPopup && data.lastIdentifier) {
    document.getElementById('identifier').value = data.lastIdentifier;
    await chrome.storage.local.remove('triggerPopup');
  }
  init();
});

async function init() {
  const idInput = document.getElementById('identifier');
  const fetchBtn = document.getElementById('fetchBtn');
  const statusDiv = document.getElementById('status');
  const errorDiv = document.getElementById('error');

  fetchBtn.addEventListener('click', async () => {
    statusDiv.textContent = '';
    errorDiv.textContent = '';
    let raw = idInput.value.trim();
    if (!raw) {
      errorDiv.textContent = 'Enter an identifier.';
      return;
    }

    const { lookup, flags, error } = parseInput(raw);
    if (error) {
      errorDiv.textContent = error;
      return;
    }

    const baseName = sanitizeFilename(lookup);
    statusDiv.textContent = 'Fetching…';

    try {
      const oaUrl = `https://api.openalex.org/works/${encodeURIComponent(lookup)}`;
      const oaResp = await fetch(oaUrl, {
        headers: {
          Accept: 'application/json',
          'User-Agent': 'RIS Fetcher (mailto:robertmlayne@icloud.com)',
        },
      });

      if (!oaResp.ok) throw new Error(`OpenAlex ${oaResp.status}`);
      const meta = await oaResp.json();

      const pdfLink = meta.best_oa_location?.pdf_url ? [meta.best_oa_location.pdf_url] : [];

      // Download PDFs if available
      for (let i = 0; i < pdfLink.length; i++) {
        await chrome.downloads.download({
          url: pdfLink[i],
          filename: `${baseName}${pdfLink.length > 1 ? `-${i + 1}` : ''}.pdf`,
        });
      }

      // Fetch RIS metadata
      const risResp = await fetch(oaUrl, {
        headers: { Accept: 'application/x-research-info-systems' },
      });

      const risText = await risResp.text();
      console.log('RIS response:', risText);

      if (risResp.ok) {
        const blob = new Blob([risText], { type: 'application/x-research-info-systems' });
        const url = URL.createObjectURL(blob);
        await chrome.downloads.download({ url, filename: `${baseName}.ris` });
        URL.revokeObjectURL(url);
      } else {
        console.error(`Failed to fetch RIS for ${lookup}:`, risText);
      }

      // Handle flags
      if (flags.has('--WC')) await fetchCitations(meta.id, baseName, 'referenced_works');
      if (flags.has('--SW')) await fetchCitations(meta.id, baseName, 'cited_by');

      statusDiv.textContent = 'Done ✔️';
    } catch (e) {
      console.error(e);
      errorDiv.textContent = 'Error: ' + e.message;
    }
  });
}

function parseInput(raw) {
  const parts = raw.split(/\s+/);
  let idPart = parts.shift();
  const flags = new Set(parts.filter((p) => /^--(WC|SW|ONN)$/.test(p)));

  const prefixMatch = idPart.match(/^([A-Za-z]+):(.+)$/);
  let prefix, id;
  if (prefixMatch) {
    prefix = prefixMatch[1].toLowerCase();
    id = prefixMatch[2];
  } else {
    if (/^10\.\d+\/\S+$/.test(idPart)) prefix = 'doi', id = idPart;
    else if (/^\d{4}\.\d{4,5}(v\d+)?$/.test(idPart)) prefix = 'arxiv', id = idPart;
    else if (/^W\d+$/.test(idPart)) prefix = 'openalex', id = idPart;
    else if (/^PMC\d+$/.test(idPart)) prefix = 'pmcid', id = idPart;
    else if (/^\d+$/.test(idPart)) return { error: 'All-digit IDs require prefix (pmid:/mag:)' };
    else return { error: 'Unrecognized identifier format' };
  }

  let lookup;
  switch (prefix) {
    case 'doi': lookup = `https://doi.org/${id}`; break;
    case 'pmid': lookup = `https://pubmed.ncbi.nlm.nih.gov/${id}`; break;
    case 'pmcid': lookup = `https://www.ncbi.nlm.nih.gov/pmc/articles/${id}`; break;
    case 'arxiv': lookup = `https://arxiv.org/abs/${id}`; break;
    case 'openalex': lookup = id; break;
    case 'mag': lookup = `https://doi.org/${id}`; break;
    case 's2': lookup = `https://doi.org/${id}`; break;
    default: return { error: 'Unsupported prefix' };
  }
  return { lookup, flags };
}

function sanitizeFilename(name) {
  return name.replace(/[^a-z0-9_\-\. ]+/gi, ' ').trim().replace(/\s+/g, '_');
}

async function fetchCitations(workId, baseName, type) {
  const url = `https://api.openalex.org/works/${encodeURIComponent(workId)}/${type}`;
  const resp = await fetch(url, {
    headers: {
      Accept: 'application/json',
      'User-Agent': 'RIS Fetcher (mailto:robertmlayne@icloud.com)',
    },
  });

  const data = await resp.json();
  console.log(type, data);
  // Extend logic here if you want to download or process citations
}
