import json
from collections import defaultdict
from typing import List, Dict
from datetime import timedelta
import argparse

def time_to_seconds(time_str: str) -> int:
    """Convert HH:MM:SS to seconds."""
    try:
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s
    except ValueError:
        raise ValueError("Time must be in HH:MM:SS format")

def group_messages_by_window(chat_data: List[Dict], window_size: int, 
                             start_time: int = None, end_time: int = None) -> Dict[int, List[Dict]]:
    messages_by_window = defaultdict(list)
    start_time = start_time or min(msg['time_in_seconds'] for msg in chat_data)
    end_time = end_time or max(msg['time_in_seconds'] for msg in chat_data)
    
    for message in chat_data:
        time = message['time_in_seconds']
        if start_time <= time <= end_time:
            window = (time - start_time) // window_size
            messages_by_window[window].append(message)
    
    return messages_by_window

def calculate_activity(messages_by_window: Dict[int, List[Dict]]) -> Dict[int, int]:
    return {window: len(messages) for window, messages in messages_by_window.items()}

def select_top_moments(activity_by_window: Dict[int, int], num_moments: int) -> List[int]:
    sorted_moments = sorted(
        activity_by_window.keys(),
        key=lambda w: (-activity_by_window[w], w)
    )
    return sorted_moments[:num_moments] if len(sorted_moments) > num_moments else sorted_moments

def create_moment_data(top_moments: List[int], messages_by_window: Dict[int, List[Dict]], 
                       activity_by_window: Dict[int, int], window_size: int, start_time: int = 0) -> List[Dict]:
    moment_data = []
    for window in top_moments:
        timestamp = (window * window_size) + start_time
        moment_data.append({
            'timestamp': timestamp,
            'formatted_time': format_timestamp(timestamp),
            'message_count': activity_by_window[window],
            'messages': messages_by_window[window]
        })
    return sorted(moment_data, key=lambda x: x['timestamp'])

def analyze_chat_moments(chat_data: List[Dict], window_size: int = 10, 
                         start_time: int = None, end_time: int = None,
                         num_moments: int = 50) -> List[Dict]:
    messages_by_window = group_messages_by_window(chat_data, window_size, start_time, end_time)
    
    # Ensure all windows in the time range are included
    if start_time is not None and end_time is not None:
        total_windows = (end_time - start_time) // window_size + 1
        for window in range(total_windows):
            if window not in messages_by_window:
                messages_by_window[window] = []
    
    activity_by_window = calculate_activity(messages_by_window)
    top_moments = select_top_moments(activity_by_window, num_moments)
    return create_moment_data(top_moments, messages_by_window, activity_by_window, window_size, start_time or 0)

def format_timestamp(seconds: int) -> str:
    """Convert seconds to a formatted string."""
    return str(timedelta(seconds=seconds))

def format_output(top_moments, num_messages):
    output = []
    for moment in top_moments:
        formatted_time = moment['formatted_time']
        message_count = moment['message_count']
        
        moment_output = f"Time: {formatted_time}, Message Count: {message_count}"
        
        # Add ASCII visualization
        bar_length = min(message_count, 100)  # Cap at 100 for readability
        visualization = f"\n{formatted_time} | {'-' * bar_length} ({message_count} messages)"
        moment_output += visualization
        
        if num_messages is not None:
            messages = [f"  - {msg['message']}" for msg in moment['messages'][:num_messages]]
            moment_output += "\n" + "\n".join(messages)
        output.append(moment_output)
    
    # Add scale for the visualization
    scale = "\n0       10      20      30      40      50      60      70      80      90      100"
    scale += "\n|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|"
    output.append(scale)
    
    message_counts = [moment['message_count'] for moment in top_moments]
    summary = f"\nAnalysis Summary:\n"
    summary += f"Total moments analyzed: {len(top_moments)}\n"
    summary += f"Average messages per moment: {sum(message_counts) / len(message_counts):.2f}\n"
    summary += f"Max messages in a moment: {max(message_counts)}\n"
    summary += f"Min messages in a moment: {min(message_counts)}"
    
    return "\n\n".join(output) + summary

def main():
    parser = argparse.ArgumentParser(description="Analyze Twitch chat moments")
    parser.add_argument("-f", "--file", type=str, required=True, 
                        help="Path to the JSON file containing Twitch chat data")
    parser.add_argument("-n", "--num_messages", type=int, default=None, 
                        help="Number of messages to display for each moment")
    parser.add_argument("-w", "--window_size", type=int, default=10,
                        help="Size of the time window in seconds (default: 10)")
    parser.add_argument("-s", "--start_time", type=str, default=None,
                        help="Start time for analysis in HH:MM:SS format (default: beginning of chat)")
    parser.add_argument("-e", "--end_time", type=str, default=None,
                        help="End time for analysis in HH:MM:SS format (default: end of chat)")
    parser.add_argument("-m", "--num_moments", type=int, default=50,
                        help="Number of top moments to analyze (default: 50)")
    args = parser.parse_args()

    try:
        with open(args.file, 'r') as f:
            chat_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: '{args.file}' is not a valid JSON file.")
        return

    start_time = time_to_seconds(args.start_time) if args.start_time else None
    end_time = time_to_seconds(args.end_time) if args.end_time else None

    moments = analyze_chat_moments(chat_data, window_size=args.window_size,
                                   start_time=start_time, end_time=end_time,
                                   num_moments=args.num_moments)

    print(f"Number of moments analyzed: {len(moments)}")

    output = format_output(moments, args.num_messages)
    print(output)
if __name__ == "__main__":
    main()