let peaks = [];

function extractVODId() {
  const match = window.location.pathname.match(/\/videos\/(\d+)/);
  return match ? match[1] : null;
}

function loadChatPeaks() {
  fetch(chrome.runtime.getURL('slopes_data.json'))
    .then(response => response.json())
    .then(data => {
      peaks = data;
      console.log(`Loaded ${peaks.length} chat peaks. Press 'N' to jump to the next peak.`);
    })
    .catch(error => {
      console.error('Error loading slopes_data.json:', error);
      console.log('Error loading chat peaks. Make sure you have run the Python script for this VOD.');
    });
}

function jumpToNextPeak() {
  const video = document.querySelector('video');
  if (video && peaks.length > 0) {
    const currentTime = video.currentTime;
    const nextPeak = peaks.find(peak => peak.time > currentTime);
    
    if (nextPeak) {
      const jumpTime = Math.max(0, nextPeak.time - 10); // Jump 10 seconds before the peak, but not before 0
      video.currentTime = jumpTime;
      console.log(`Jumped to 10 seconds before peak at ${formatTime(nextPeak.time)}. Slope: ${nextPeak.slope}`);
    } else {
      console.log("No more peaks ahead!");
    }
  } else {
    console.log("Video not found or no peaks loaded!");
  }
}

function formatTime(seconds) {
  return new Date(seconds * 1000).toISOString().substr(11, 8);
}

document.addEventListener('keydown', function(event) {
  if (event.key === 'N' || event.key === 'n') {
    jumpToNextPeak();
  }
});

// Automatically load chat peaks when the script is injected
loadChatPeaks();

// We'll keep this listener for potential future use or manual reloading
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === "load_chat_peaks") {
    loadChatPeaks();
    sendResponse({status: "Chat peaks loaded. Press 'N' to jump to peaks."});
  }
});