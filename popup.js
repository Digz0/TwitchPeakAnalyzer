document.addEventListener('DOMContentLoaded', function() {
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    chrome.tabs.sendMessage(tabs[0].id, {action: "get_peaks_status"}, function(response) {
      if (response && response.status) {
        document.getElementById('status').textContent = response.status;
      }
    });
  });
});