let peaks = [];
let currentPeakIndex = -1;
let notificationElement = null;

async function loadChatPeaks() {
  try {
    const response = await fetch(chrome.runtime.getURL('slopes_data.json'));
    peaks = await response.json();
    console.log(`Loaded ${peaks.length} chat peaks. Press 'Enter' to jump to the next peak.`);
  } catch (error) {
    console.error('Error loading slopes_data.json:', error);
  }
}

function jumpToNextPeak() {
  const video = document.querySelector('video');
  if (!video || peaks.length === 0) return;

  const currentTime = video.currentTime;
  const nextPeak = peaks.find(peak => peak.time > currentTime && peak.slope > 0);
  
  if (nextPeak) {
    video.currentTime = Math.max(0, nextPeak.time - 10);
    console.log(`Jumped to 10 seconds before peak at ${formatTime(nextPeak.time)}. Slope: ${nextPeak.slope}`);
  } else {
    console.log("No more peaks ahead!");
  }
}

function formatTime(seconds) {
  return new Date(seconds * 1000).toISOString().substr(11, 8);
}

function toggleNotification(message) {
  if (message) {
    if (!notificationElement) {
      notificationElement = document.createElement('div');
      notificationElement.style.cssText = `
        position: fixed; top: 20px; left: 20px; background-color: rgba(0, 0, 0, 0.8);
        color: white; padding: 10px; border-radius: 5px; z-index: 9999;
      `;
      document.body.appendChild(notificationElement);
    }
    notificationElement.textContent = message;
  } else if (notificationElement) {
    notificationElement.remove();
    notificationElement = null;
  }
}

function checkForPeakWindow() {
  const video = document.querySelector('video');
  if (!video || peaks.length === 0) return;

  const currentTime = video.currentTime;
  for (let i = 0; i < peaks.length - 1; i += 2) {
    const [start, end] = [peaks[i], peaks[i + 1]];
    if (currentTime >= start.time && currentTime < end.time) {
      toggleNotification(`Peak window: ${formatTime(start.time)} - ${formatTime(end.time)}`);
      return;
    }
  }
  toggleNotification(null);
}

document.addEventListener('keydown', event => {
  if (event.key === 'Enter') {
    jumpToNextPeak();
  }
});

loadChatPeaks();
setInterval(checkForPeakWindow, 1000);

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "get_peaks_status") {
    sendResponse({status: "Chat peaks loaded. Press 'Enter' to jump to peaks."});
  }
});