let peaks = [];
let currentPeakIndex = -1;
let notificationElement = null;

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
    const nextPeak = peaks.find((peak, index) => peak.time > currentTime && peak.slope > 0 && index % 2 === 0);
    
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

function createNotification(message) {
  if (notificationElement) {
    notificationElement.textContent = message;
  } else {
    notificationElement = document.createElement('div');
    notificationElement.textContent = message;
    notificationElement.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background-color: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 10px;
      border-radius: 5px;
      z-index: 9999;
    `;
    document.body.appendChild(notificationElement);
  }
}

function removeNotification() {
  if (notificationElement && notificationElement.parentNode) {
    document.body.removeChild(notificationElement);
    notificationElement = null;
  }
}

function checkForPeakWindow() {
  const video = document.querySelector('video');
  if (video && peaks.length > 0) {
    const currentTime = video.currentTime;
    
    for (let i = 0; i < peaks.length - 1; i += 2) {
      const positivePeak = peaks[i];
      const negativePeak = peaks[i + 1];
      
      if (currentTime >= positivePeak.time && currentTime < negativePeak.time) {
        if (i !== currentPeakIndex) {
          const message = `You're in a peak window! Peak started at ${formatTime(positivePeak.time)} with slope ${positivePeak.slope}.`;
          createNotification(message);
          currentPeakIndex = i;
        }
        return;
      }
    }
    
    // If we're not in any peak window, remove the notification and reset the currentPeakIndex
    removeNotification();
    currentPeakIndex = -1;
  }
}

document.addEventListener('keydown', function(event) {
  if (event.key === 'N' || event.key === 'n') {
    jumpToNextPeak();
  }
});

// Automatically load chat peaks when the script is injected
loadChatPeaks();

// Check for peak window every second
setInterval(checkForPeakWindow, 1000);

// We'll keep this listener for potential future use or manual reloading
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === "load_chat_peaks") {
    loadChatPeaks();
    sendResponse({status: "Chat peaks loaded. Press 'N' to jump to peaks."});
  }
  if (request.action === "get_peaks_status") {
    sendResponse({status: "Chat peaks loaded. Press 'N' to jump to peaks."});
  }
});