// static/script.js
let currentJob = null;
const btnStart = document.getElementById('btnStart');
const btnCancel = document.getElementById('btnCancel');
const inputUrl = document.getElementById('inputUrl');
const statusDiv = document.getElementById('status');
const jobInfo = document.getElementById('jobInfo');
const resultsDiv = document.getElementById('results');
let pollInterval = null;

btnStart.addEventListener('click', async () => {
  const url = inputUrl.value.trim();
  if (!url) return alert('Enter a valid OLX search URL.');

  btnStart.disabled = true;
  statusDiv.textContent = 'Starting scrape...';
  resultsDiv.innerHTML = '';
  jobInfo.innerHTML = '';

  try {
    const res = await fetch('/start_scrape', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({url})
    });
    const data = await res.json();
    if (data.jobid) {
      currentJob = data.jobid;
      statusDiv.textContent = 'Job queued: ' + currentJob;
      startPolling(currentJob);
      btnCancel.disabled = false;
    } else {
      statusDiv.textContent = 'Failed to start job.';
      btnStart.disabled = false;
    }
  } catch (err) {
    console.error(err);
    statusDiv.textContent = 'Error starting job: ' + err.message;
    btnStart.disabled = false;
  }
});

btnCancel.addEventListener('click', () => {
  // simple UI cancel: stop polling (server thread will still run)
  if (pollInterval) {
    clearInterval(pollInterval);
    pollInterval = null;
  }
  statusDiv.textContent = 'Polling stopped by user.';
  btnStart.disabled = false;
  btnCancel.disabled = true;
});

function startPolling(jobid) {
  if (pollInterval) clearInterval(pollInterval);

  async function poll() {
    try {
      const res = await fetch('/status/' + jobid);
      const j = await res.json();
      if (j.error) {
        statusDiv.textContent = 'Job error: ' + j.error;
        clearInterval(pollInterval);
        pollInterval = null;
        btnStart.disabled = false;
        btnCancel.disabled = true;
        return;
      }
      statusDiv.textContent = 'Job ' + jobid + ' — status: ' + j.status + ' — items: ' + (j.count || 0);
      jobInfo.innerHTML = `<div class="small">Job: ${jobid} — status: ${j.status} — items: ${j.count || 0}</div>`;

      if (j.status === 'finished') {
        clearInterval(pollInterval);
        pollInterval = null;
        btnStart.disabled = false;
        btnCancel.disabled = true;
        fetchResults(jobid);
      } else if (j.status === 'error') {
        clearInterval(pollInterval);
        pollInterval = null;
        statusDiv.textContent = 'Job error: ' + (j.error || 'unknown');
        btnStart.disabled = false;
        btnCancel.disabled = true;
      }
    } catch (err) {
      console.error('poll error', err);
      statusDiv.textContent = 'Polling error: ' + err.message;
      clearInterval(pollInterval);
      pollInterval = null;
      btnStart.disabled = false;
      btnCancel.disabled = true;
    }
  }

  // poll every 2 seconds
  poll();
  pollInterval = setInterval(poll, 2000);
}

async function fetchResults(jobid) {
  try {
    const res = await fetch('/results/' + jobid);
    const j = await res.json();
    if (j.error) {
      resultsDiv.innerHTML = '<div class="small">Error fetching results: ' + j.error + '</div>';
      return;
    }
    const arr = j.results || [];
    if (!arr.length) {
      resultsDiv.innerHTML = '<div class="small">No results found.</div>';
      return;
    }

    // build table + download link
    let html = '<div style="margin:8px 0"><a href="/download/' + jobid + '"><button>Download CSV</button></a></div>';
    html += '<table><thead><tr><th>#</th><th>Title</th><th>Description</th><th>Price</th><th>Link</th></tr></thead><tbody>';
    arr.forEach((it, idx) => {
      html += '<tr>';
      html += '<td>' + (idx+1) + '</td>';
      html += '<td>' + escapeHtml(it.title || '') + '</td>';
      html += '<td>' + escapeHtml(it.description || '') + '</td>';
      html += '<td>' + escapeHtml(it.price || '') + '</td>';
      html += '<td>' + (it.link ? ('<a href="' + it.link + '" target="_blank">Open</a>') : '') + '</td>';
      html += '</tr>';
    });
    html += '</tbody></table>';
    resultsDiv.innerHTML = html;
  } catch (err) {
    console.error(err);
    resultsDiv.innerHTML = '<div class="small">Error getting results: ' + err.message + '</div>';
  }
}

function escapeHtml(s) {
  if (!s) return '';
  return s.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
}
