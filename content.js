// =================================================================================
//  Content Script - Version 15.0 ("The Unbreakable Build")
// =================================================================================
//  - CRASH FIXED: This version uses a new "request-response" loop. It sends one
//    batch of frames for analysis and WAITS for the results before sending the next batch.
//    This prevents overwhelming the backend and solves the timestamp crash.
//  - This is the final, stable, and working content script.
// =================================================================================

let analysisTimeoutId;
let isAnalyzing = false;
let canvasElement = document.createElement('canvas');
const MAX_WIDTH = 480;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.command === 'start') {
        const result = startAnalysis();
        sendResponse(result);
    } else if (request.command === 'stop') {
        stopAnalysis();
        sendResponse({ status: 'stopped' });
    }
    return true;
});

function startAnalysis() {
    if (isAnalyzing) return { status: 'error', message: 'Analysis is already running.' };
    
    const visibleVideos = Array.from(document.querySelectorAll('video')).filter(v => v.readyState >= 4 && v.offsetHeight > 100);
    if (visibleVideos.length === 0) {
        return { status: 'error', message: 'No participant videos found.' };
    }

    isAnalyzing = true;
    console.log("Monitor: Analysis started successfully.");
    runAnalysisCycle(); 
    return { status: 'success' };
}

function stopAnalysis() {
    if (!isAnalyzing) return;
    isAnalyzing = false;
    clearTimeout(analysisTimeoutId);
    document.querySelectorAll('.monitor-overlay').forEach(el => el.remove());
    console.log("Monitor: Analysis stopped.");
}

async function runAnalysisCycle() {
    if (!isAnalyzing) return;

    const videoElements = document.querySelectorAll('video');
    const analysisPromises = [];
    
    videoElements.forEach((videoEl, index) => {
        if (videoEl.readyState >= 4 && videoEl.offsetHeight > 100 && videoEl.offsetWidth > 100) {
            let videoId = videoEl.dataset.monitorId;
            if (!videoId) {
                videoId = `participant-${Date.now()}-${index}`;
                videoEl.dataset.monitorId = videoId;
            }
            analysisPromises.push(captureAndSendFrame(videoId, videoEl));
        }
    });

    await Promise.all(analysisPromises);
    
    if (isAnalyzing) {
        analysisTimeoutId = setTimeout(runAnalysisCycle, 1000); // 1-second delay between cycles
    }
}

async function captureAndSendFrame(videoId, videoEl) {
    if (!videoEl || videoEl.videoWidth === 0) return;
    const aspectRatio = videoEl.videoHeight / videoEl.videoWidth;
    canvasElement.width = MAX_WIDTH;
    canvasElement.height = MAX_WIDTH * aspectRatio;
    const ctx = canvasElement.getContext('2d');
    ctx.drawImage(videoEl, 0, 0, canvasElement.width, canvasElement.height);
    const imageData = canvasElement.toDataURL('image/jpeg', 0.7);

    try {
        const response = await fetch('http://127.0.0.1:5000/process_frame', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: videoId, image: imageData }),
        });
        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        const data = await response.json();
        if (data.result) {
            updateOverlay(data.student_id, data.result);
        }
    } catch (e) {
        console.error(`Monitor: Backend fetch failed for ${videoId}.`, e);
    }
}

function updateOverlay(videoId, result) {
    const videoEl = document.querySelector(`[data-monitor-id="${videoId}"]`);
    if (!videoEl) return;

    let overlay = document.getElementById(`overlay-${videoId}`);
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'monitor-overlay';
        overlay.id = `overlay-${videoId}`;
        document.body.appendChild(overlay);
    }

    const videoRect = videoEl.getBoundingClientRect();
    const statusColor = {"Attentive": "#28a745", "Distracted": "#ffc107", "Inattentive": "#dc3545"}[result.status] || "#6c757d";
    
    requestAnimationFrame(() => {
        overlay.style.cssText = `
            position: absolute; left: ${window.scrollX + videoRect.left}px; top: ${window.scrollY + videoRect.top}px;
            width: ${videoRect.width}px; height: ${videoRect.height}px;
            border: 5px solid ${statusColor}; border-radius: 12px; box-sizing: border-box;
            pointer-events: none; z-index: 9999; transition: all 0.3s ease-out;
        `;
        
        let label = overlay.querySelector('.monitor-label');
        if (!label) {
            label = document.createElement('div');
            label.className = 'monitor-label';
            overlay.appendChild(label);
        }
        
        label.innerHTML = `<strong>${result.name}</strong> | ${result.score} | <span style="color:${statusColor};">${result.status}</span>`;
        label.style.cssText = `
            position:absolute; top:8px; left:8px; background:rgba(0,0,0,0.8);
            color:white; padding:5px 10px; font-size:16px; border-radius:8px;
            font-weight:bold; box-shadow: 0 2px 5px rgba(0,0,0,0.5);
        `;
    });
}