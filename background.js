async function processFrames(frames, tabId) {
    if (!frames || frames.length === 0) return;

    try {
        const response = await fetch('http://127.0.0.1:5000/analyze_images', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ frames })
        });
        
        const data = await response.json();
        
        if (data.error) {
            console.error('Backend error:', data.error);
            return;
        }

        const updates = data.results.map(result => ({
            id: result.student_id,
            result: result.result || {
                name: `Student ${result.student_id?.split('-').pop() || 'Unknown'}`,
                status: "Error",
                score: 0
            }
        }));

        chrome.tabs.sendMessage(tabId, {
            command: 'update_overlays',
            updates: updates
        });

    } catch (error) {
        console.error('Failed to process frames:', error);
    }
}