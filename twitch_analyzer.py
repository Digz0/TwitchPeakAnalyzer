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
    return dict(frequency)

def calculate_slopes(frequency, method='difference'):
    slopes = {}
    times = sorted(frequency.keys())
    for i in range(1, len(times)):
        current_time = times[i]
        prev_time = times[i-1]
        if method == 'difference':
            slopes[current_time] = frequency[current_time] - frequency[prev_time]
        elif method == 'ratio':
            if frequency[prev_time] != 0:
                ratio = frequency[current_time] / frequency[prev_time]
                slopes[current_time] = ratio - 1
            else:
                slopes[current_time] = float('inf') if frequency[current_time] > 0 else 0
    return slopes

def find_significant_slopes(slopes, num_peaks=50, window_size=10):
    positive_slopes = sorted([(t, s) for t, s in slopes.items() if s > 0], key=lambda x: -x[1])[:num_peaks]
    positive_slopes.sort(key=lambda x: x[0])
    
    all_slopes = []
    for current_time, current_slope in positive_slopes:
        all_slopes.append((current_time, current_slope))
        next_minute = current_time + (60 // window_size)
        negative_slopes = [(t, s) for t, s in slopes.items() if current_time < t <= next_minute and s < 0]
        if negative_slopes:
            all_slopes.append(min(negative_slopes, key=lambda x: x[1]))
    
    return all_slopes

def plot_chat_activity(frequency, significant_slopes, window_size):
    times = sorted(frequency.keys())
    plt.figure(figsize=(30, 10))
    plt.plot([t * window_size for t in times], [frequency[t] for t in times], label='Message Frequency')
    
    for color, label, slopes in [('green', 'Positive Slopes', [s for s in significant_slopes if s[1] > 0]),
                                 ('red', 'Negative Slopes', [s for s in significant_slopes if s[1] < 0])]:
        plt.scatter([t * window_size for t, _ in slopes], [frequency[t] for t, _ in slopes], 
                    color=color, label=label, zorder=5)
    
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

def main(file_path, window_size=10, num_peaks=50, generate_image=False, slope_method='difference'):
    chat_data = load_chat_data(file_path)
    frequency = calculate_message_frequency(chat_data, window_size)
    slopes = calculate_slopes(frequency, method=slope_method)
    significant_slopes = find_significant_slopes(slopes, num_peaks, window_size)

    print(f"Top {num_peaks} positive slopes and intervening negative slopes (chronological order):")
    for time, slope in significant_slopes:
        if slope_method == 'difference':
            print(f"Time: {timedelta(seconds=time * window_size)}, Slope: {slope:+d}")
        else:
            print(f"Time: {timedelta(seconds=time * window_size)}, Ratio change: {slope:+.2f}")

    if generate_image:
        plot_chat_activity(frequency, significant_slopes, window_size)
        print("Chat activity analysis image saved as 'chat_activity_analysis.png'")

    with open('slopes_data.json', 'w') as f:
        json.dump([{"time": time * window_size, "slope": slope} for time, slope in significant_slopes], f)
    print("Slopes data for browser extension saved as 'slopes_data.json'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Twitch VOD chat activity")
    parser.add_argument("-f", "--file", required=True, help="Path to the JSON file containing chat data")
    parser.add_argument("-w", "--window", type=int, default=10, help="Window size in seconds (default: 10)")
    parser.add_argument("-n", "--num_peaks", type=int, default=50, help="Number of top positive slopes to display (default: 50)")
    parser.add_argument("--generate-image", action="store_true", help="Generate chat activity analysis image")
    parser.add_argument("--slope-method", choices=['difference', 'ratio'], default='difference', 
                        help="Method to calculate slopes: 'difference' or 'ratio' (default: difference)")
    args = parser.parse_args()

    main(args.file, args.window, args.num_peaks, args.generate_image, args.slope_method)
