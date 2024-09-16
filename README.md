# TwitchPeakAnalyzer

A tool to analyze Twitch chat activity and identify significant peaks and dips in message frequency.

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

1. First, use the `chat-downloader` to download Twitch chat data:
   ```
   chat_downloader https://www.twitch.tv/videos/YOUR_VIDEO_ID --output chat_data.json
   ```

2. Then, run the TwitchPeakAnalyzer:
   ```
   python twitch_analyzer.py -f chat_data.json
   ```

3. The script will generate two outputs:
   - A console output listing significant slopes (peaks and dips in chat activity)
   - An image file `chat_activity_analysis.png` showing the chat activity graph

### Additional Options

- `-w` or `--window`: Set the time window size in seconds (default: 10)
- `-n` or `--num_peaks`: Set the number of top positive slopes to display (default: 50)

For example:
```
python twitch_analyzer.py -f chat_data.json -w 15 -n 30
```

For more options, run:
```
python twitch_analyzer.py --help
```

## Output

- `chat_activity_analysis.png`: A graph showing chat activity over time, with significant peaks and their following steepest dips (within 1 minute) highlighted
- Console output: A list of significant positive slopes and their following steepest negative slopes (within 1 minute) in chronological order

## Requirements

- Python 3.6+
- matplotlib
- chat-downloader

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.