# TwitchPeakAnalyzer

A tool to analyze Twitch VOD chat activity and identify significant peaks and dips in message frequency.

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/Digz0/TwitchPeakAnalyzer.git
   cd TwitchPeakAnalyzer
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Use the `chat-downloader` to download Twitch chat data:
   ```
   chat_downloader https://www.twitch.tv/videos/YOUR_VIDEO_ID --output chat_data.json
   ```

2. Run the TwitchPeakAnalyzer:
   ```
   python twitch_analyzer.py -f chat_data.json -v YOUR_VIDEO_ID
   ```

3. Load the browser extension:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the extension directory

4. Navigate to the Twitch VOD page. The extension will automatically load chat peaks.

5. Press 'N' to jump to the next peak while watching the VOD.

### Additional Options

- `-w` or `--window`: Set the time window size in seconds (default: 10)
- `-n` or `--num_peaks`: Set the number of top positive slopes to display (default: 50)

Example: