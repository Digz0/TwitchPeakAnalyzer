let peaks = [];
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
  const nextPeak = peaks.find(peak => peak.top.time > currentTime);
  
  if (nextPeak) {
    video.currentTime = Math.max(0, nextPeak.before.time);
    console.log(`Jumped to quiet period at ${formatTime(nextPeak.before.time)} before peak at ${formatTime(nextPeak.top.time)}`);
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
  const currentPeak = peaks.find(peak => 
    currentTime >= peak.before.time && currentTime <= peak.top.time
  );

  if (currentPeak) {
    const messageCount = currentPeak.top.count - currentPeak.before.count;
    toggleNotification(
      `Approaching peak: ${formatTime(currentPeak.before.time)} → ${formatTime(currentPeak.top.time)}\n` +
      `Message increase: ${currentPeak.before.count} → ${currentPeak.top.count} (+${messageCount})`
    );
  } else {
    toggleNotification(null);
  }
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
