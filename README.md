# TwitchPeakAnalyzer

TwitchPeakAnalyzer is a tool for analyzing Twitch chat data, identifying and visualizing moments of high activity.

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

For more options, run:
```
python twitch_analyzer.py --help
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.