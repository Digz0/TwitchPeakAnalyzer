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
        t = msg['time_in_seconds']
        frequency[t // window_size] += 1
    return dict(frequency)

def calculate_slopes(frequency):
    slopes = {}
    times = sorted(frequency.keys())
    for i in range(1, len(times)):
        current_time = times[i]
        prev_time = times[i-1]
        slope = frequency[current_time] - frequency[prev_time]
        slopes[current_time] = slope
    return slopes

def find_significant_slopes(slopes, num_peaks=50, window_size=10):
    positive_slopes = sorted([(t, s) for t, s in slopes.items() if s > 0], key=lambda x: -x[1])[:num_peaks]
    positive_slopes.sort(key=lambda x: x[0])  # Sort positive slopes chronologically
    
    all_slopes = []
    for current_time, current_slope in positive_slopes:
        all_slopes.append((current_time, current_slope))
        
        # Look ahead max 1 minute (6 * 10-second windows)
        next_minute = current_time + (60 // window_size)
        
        # Find the steepest negative slope within the next minute
        steepest_negative = min(
            ((t, s) for t, s in slopes.items() if current_time < t <= next_minute and s < 0),
            key=lambda x: x[1],  # Sort by slope value (steepest negative)
            default=None
        )
        
        if steepest_negative:
            all_slopes.append(steepest_negative)
    
    return all_slopes

def format_time(seconds):
    return str(timedelta(seconds=seconds))

def plot_chat_activity(frequency, significant_slopes, window_size):
    times = sorted(frequency.keys())
    messages = [frequency[t] for t in times]
    
    # Calculate the full duration of the chat
    max_time = max(times) * window_size
    
    plt.figure(figsize=(30, 10))
    plt.plot([t * window_size for t in times], messages, label='Message Frequency')
    
    positive_slopes = [(t, s) for t, s in significant_slopes if s > 0]
    negative_slopes = [(t, s) for t, s in significant_slopes if s < 0]
    
    plt.scatter([t * window_size for t, _ in positive_slopes], [frequency[t] for t, _ in positive_slopes], 
                color='green', label='Positive Slopes', zorder=5)
    plt.scatter([t * window_size for t, _ in negative_slopes], [frequency[t] for t, _ in negative_slopes], 
                color='red', label='Negative Slopes', zorder=5)
    
    plt.xlabel('Time')
    plt.ylabel('Number of Messages')
    plt.title('Chat Activity Analysis')
    plt.legend()
    plt.grid(True)
    
    # Format x-axis to show time in H:M:S
    def format_time(x, pos):
        return str(timedelta(seconds=int(x)))
    
    plt.gca().xaxis.set_major_formatter(FuncFormatter(format_time))
    plt.gcf().autofmt_xdate()  # Rotate and align the tick labels
    
    # Set the x-axis limit to the full duration of the chat
    plt.xlim(0, max_time)
    
    plt.tight_layout()  # Adjust the layout to prevent cutting off labels
    plt.savefig('chat_activity_analysis.png', dpi=300)  # Increased DPI for better quality
    plt.close()

def main(file_path, window_size=10, num_peaks=50):
    chat_data = load_chat_data(file_path)
    frequency = calculate_message_frequency(chat_data, window_size)
    slopes = calculate_slopes(frequency)
    significant_slopes = find_significant_slopes(slopes, num_peaks, window_size)

    print(f"Top {num_peaks} positive slopes and intervening negative slopes (chronological order):")
    for time, slope in significant_slopes:
        sign = '+' if slope > 0 else ''
        print(f"Time: {format_time(time * window_size)}, Slope: {sign}{slope}")

    plot_chat_activity(frequency, significant_slopes, window_size)
    print("Chat activity analysis image saved as 'chat_activity_analysis.png'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Twitch chat activity")
    parser.add_argument("-f", "--file", required=True, help="Path to the JSON file containing chat data")
    parser.add_argument("-w", "--window", type=int, default=10, help="Window size in seconds (default: 10)")
    parser.add_argument("-n", "--num_peaks", type=int, default=50, help="Number of top positive slopes to display (default: 50)")
    args = parser.parse_args()

    main(args.file, args.window, args.num_peaks)
