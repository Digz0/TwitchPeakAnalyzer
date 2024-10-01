# TwitchPeakAnalyzer

A tool to analyze Twitch VOD chat activity and identify significant peaks and dips in message frequency.

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/Digz0/TwitchPeakAnalyzer.git
   cd TwitchPeakAnalyzer
   ```

2. Create and activate a virtual environment (recommended):
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. Install the required dependencies:
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
   python twitch_analyzer.py -f chat_data.json
   ```
   This will generate a `slopes_data.json` file for the browser extension.

3. Copy the generated `slopes_data.json` file to the browser extension directory.

4. Load the browser extension:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the extension directory (containing manifest.json)
   - Note: This extension uses Manifest V3

5. Navigate to the Twitch VOD page. The extension will automatically load chat peaks.

6. While watching the VOD:
   - Press 'Enter' to jump to the next peak.
   - An on-screen notification will appear when you're in a peak window.

### Additional Options

- `-w` or `--window`: Set the time window size in seconds (default: 10)
- `-n` or `--num_peaks`: Set the number of top positive slopes to display (default: 50)
- `--generate-image`: Generate chat activity analysis image (optional)
- `--slope-method`: Choose the method to calculate slopes: 'difference' or 'ratio' (default: difference)

Example using the ratio method and generating an image:
```
python twitch_analyzer.py -f chat_data.json -w 15 -n 75 --generate-image --slope-method ratio
```

If you use the `--generate-image` option, it will create `chat_activity_analysis.png`.

### Slope Calculation Methods

- Difference: Calculates the absolute change in message frequency between time windows.
- Ratio: Calculates the relative change in message frequency between time windows. This can be useful for detecting significant relative changes, especially in less active chats.

## Requirements

- Python 3.7+
- Chrome browser (for the extension)

## Testing

To run the tests:
```
python -m unittest test_twitch_analyzer.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.