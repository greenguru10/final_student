document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const endBtn = document.getElementById('endBtn');
    const statusDiv = document.getElementById('status');
    const downloadLinksDiv = document.getElementById('download-links');

    function setStatus(className, text) { statusDiv.className = className; statusDiv.textContent = text; }

    function sendMessageToContentScript(command, callback) {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0] && tabs[0].url.includes("meet.google.com")) {
                chrome.tabs.sendMessage(tabs[0].id, { command }, (response) => {
                    if (chrome.runtime.lastError) { setStatus('status-error', 'Error: Refresh Meet page.'); }
                    else if (callback) { callback(response); }
                });
            } else { setStatus('status-error', 'Error: Not on a Google Meet page.'); }
        });
    }

    startBtn.addEventListener('click', () => {
        downloadLinksDiv.innerHTML = '';
        sendMessageToContentScript('start', (response) => {
            if (response?.status === 'success') { setStatus('status-running', 'Status: Analysis Running...'); }
            else { setStatus('status-error', `Error: ${response?.message || 'Could not start.'}`); }
        });
    });

    stopBtn.addEventListener('click', () => {
        sendMessageToContentScript('stop', () => {
            setStatus('status-stopped', 'Status: Analysis Stopped.');
        });
    });

    endBtn.addEventListener('click', async () => {
        downloadLinksDiv.innerHTML = '';
        setStatus('status-generating', 'Status: Generating reports...');
        sendMessageToContentScript('stop');
        try {
            const response = await fetch('http://127.0.0.1:5000/end_session', { method: 'POST' });
            const data = await response.json();
            if (data.status === 'success') {
                setStatus('status-generating', 'Reports Ready for Download');
                displayDownloadLinks(data.reports);
            } else { setStatus('status-error', `Error: ${data.message}`); }
        } catch (e) { setStatus('status-error', 'Error: Backend is unreachable.'); }
    });

    function displayDownloadLinks(reports) {
        if (!reports || reports.length === 0) {
            downloadLinksDiv.innerHTML = "<h4>No reports generated.</h4><p>Ensure participants were visible for at least 30 seconds.</p>";
            return;
        }
        downloadLinksDiv.innerHTML = '<h4>Download Reports:</h4>';
        reports.forEach(report => {
            const link = document.createElement('a');
            link.href = `http://127.0.0.1:5000/download_report/${report.filename}`;
            link.download = report.filename;
            link.textContent = `Report for ${report.student_name}`;
            downloadLinksDiv.appendChild(link);
        });
    }
});