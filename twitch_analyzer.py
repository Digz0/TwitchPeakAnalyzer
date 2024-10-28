import json
from collections import defaultdict
from datetime import timedelta
import argparse
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def load_chat_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def calculate_message_frequency(chat_data, window_size=10):
    frequency = defaultdict(int)
    for msg in chat_data:
        frequency[msg['time_in_seconds'] // window_size] += 1
    return sorted(frequency.items(), key=lambda x: x[0])

def find_least_active_window(frequency, target_window, lookback_seconds, window_size):
    start_window = max(0, target_window - lookback_seconds // window_size)
    relevant_windows = [
        (time, count) for time, count in frequency 
        if start_window <= time < target_window
    ]
    if not relevant_windows:
        return None
    min_count = min(count for _, count in relevant_windows)
    return min((time, count) for time, count in relevant_windows if count == min_count)

def find_top_windows(frequency, num_top_windows):
    peaks = []
    for i in range(1, len(frequency) - 1):
        prev_time, prev_count = frequency[i-1]
        curr_time, curr_count = frequency[i]
        next_time, next_count = frequency[i+1]
        
        if curr_count >= prev_count and curr_count > next_count:
            peaks.append((curr_time, curr_count))
    
    return sorted(peaks, key=lambda x: (-x[1], x[0]))[:num_top_windows]

def find_least_active_window_after(frequency, target_window, lookahead_seconds, window_size):
    end_window = min(target_window + lookahead_seconds // window_size, len(frequency) - 1)
    relevant_windows = [
        (time, count) for time, count in frequency 
        if target_window < time <= end_window
    ]
    if not relevant_windows:
        return None
    min_count = min(count for _, count in relevant_windows)
    return min((time, count) for time, count in relevant_windows if count == min_count)

def find_least_active_windows_for_tops(frequency, top_windows, lookback_seconds, window_size):
    least_active_before = []
    for top_window, _ in top_windows:
        before = find_least_active_window(frequency, top_window, lookback_seconds, window_size)
        least_active_before.append(before if before else (top_window, _))
    return least_active_before

def plot_chat_activity(frequency, top_windows, least_active_before, window_size):
    plt.figure(figsize=(30, 10))
    times, counts = zip(*frequency)
    plt.plot([t * window_size for t in times], counts, label='Message Frequency')
    
    top_times, top_counts = zip(*top_windows)
    plt.scatter([t * window_size for t in top_times], top_counts, 
                color='red', label='Top Windows', zorder=5)
    
    before_times, before_counts = zip(*least_active_before)
    plt.scatter([t * window_size for t in before_times], before_counts, 
                color='blue', label='Least Active Before', zorder=5)
    
    plt.xlabel('Time')
    plt.ylabel('Number of Messages')
    plt.title('Chat Activity Analysis')
    plt.legend()
    plt.grid(True)
    plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: str(timedelta(seconds=int(x)))))
    plt.gcf().autofmt_xdate()
    plt.xlim(0, max(times) * window_size)
    plt.tight_layout()
    plt.savefig('chat_activity_analysis.png', dpi=300)
    plt.close()

def main(file_path, window_size=4, num_top_windows=50, generate_image=False, lookback_seconds=60):
    chat_data = load_chat_data(file_path)
    frequency = calculate_message_frequency(chat_data, window_size)
    top_windows = find_top_windows(frequency, num_top_windows)
    least_active_before = find_least_active_windows_for_tops(frequency, top_windows, lookback_seconds, window_size)

    # Pair top windows with their corresponding least active windows and sort by least active before time
    paired_windows = sorted(zip(least_active_before, top_windows), key=lambda x: x[0][0])

    print(f"Top {num_top_windows} windows with most frequent messages and their preceding least active windows:")
    for (before_time, before_count), (top_time, top_count) in paired_windows:
        print(f"Least Active Before - Time: {timedelta(seconds=before_time * window_size)}, Message count: {before_count}")
        print(f"Top - Time: {timedelta(seconds=top_time * window_size)}, Message count: {top_count}")
        print()

    if generate_image:
        plot_chat_activity(frequency, top_windows, least_active_before, window_size)
        print("Chat activity analysis image saved as 'chat_activity_analysis.png'")

    # Prepare data for JSON output
    json_data = []
    for (before_time, before_count), (top_time, top_count) in paired_windows:
        json_data.append({
            "time": before_time * window_size,
            "before": {
                "time": before_time * window_size,
                "count": before_count
            },
            "top": {
                "time": top_time * window_size,
                "count": top_count
            }
        })

    with open('slopes_data.json', 'w') as f:
        json.dump(json_data, f, indent=2)
    print("Activity data for browser extension saved as 'slopes_data.json'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Twitch VOD chat activity")
    parser.add_argument("-f", "--file", required=True, help="Path to the JSON file containing chat data")
    parser.add_argument("-w", "--window", type=int, default=4, help="Window size in seconds (default: 4)")
    parser.add_argument("-n", "--num_top_windows", type=int, default=50, help="Number of top windows to display (default: 50)")
    parser.add_argument("--generate-image", action="store_true", help="Generate chat activity analysis image")
    parser.add_argument("-l", "--lookback", type=int, default=60, help="Lookback time in seconds for least active windows (default: 60)")
    args = parser.parse_args()

    main(args.file, args.window, args.num_top_windows, args.generate_image, args.lookback)
