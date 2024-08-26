"""
Twitch Chat Analyzer

This module provides functionality to analyze Twitch chat data,
identifying and visualizing moments of high activity.
"""

import json
from collections import defaultdict
from typing import List, Dict, Optional
from datetime import timedelta
import argparse

# Constants
MAX_BAR_LENGTH = 100
DEFAULT_WINDOW_SIZE = 10
DEFAULT_NUM_MOMENTS = 50
TIME_FORMAT = "%H:%M:%S"

def time_to_seconds(time_str: str) -> int:
    """Convert HH:MM:SS to seconds."""
    try:
        return int(timedelta(**dict(zip(['hours', 'minutes', 'seconds'], map(int, time_str.split(':'))))).total_seconds())
    except ValueError:
        raise ValueError("Time must be in HH:MM:SS format")

def group_messages_by_window(chat_data: List[Dict], window_size: int, 
                             start_time: Optional[int] = None, end_time: Optional[int] = None) -> Dict[int, List[Dict]]:
    """Group messages by time windows."""
    if not chat_data:
        return {}
    
    start_time = start_time or min(msg['time_in_seconds'] for msg in chat_data)
    end_time = end_time or max(msg['time_in_seconds'] for msg in chat_data)
    
    messages_by_window = defaultdict(list)
    for message in chat_data:
        time = message['time_in_seconds']
        if start_time <= time <= end_time:
            window = (time - start_time) // window_size
            messages_by_window[window].append(message)
    
    return dict(messages_by_window)

def calculate_activity(messages_by_window: Dict[int, List[Dict]]) -> Dict[int, int]:
    """Calculate the number of messages in each time window."""
    return {window: len(messages) for window, messages in messages_by_window.items()}

def select_top_moments(activity_by_window: Dict[int, int], num_moments: int) -> List[int]:
    """Select the top moments based on message activity."""
    sorted_moments = sorted(
        activity_by_window.keys(),
        key=lambda w: (-activity_by_window[w], w)
    )
    return sorted_moments[:num_moments] if len(sorted_moments) > num_moments else sorted_moments

def create_moment_data(top_moments: List[int], messages_by_window: Dict[int, List[Dict]], 
                       activity_by_window: Dict[int, int], window_size: int) -> List[Dict]:
    """Create detailed data for top chat moments."""
    moment_data = []
    for window in top_moments:
        messages = messages_by_window[window]
        if messages:
            timestamp = messages[0]['time_in_seconds']  # Use the timestamp of the first message in the window
            moment_data.append({
                'timestamp': timestamp,
                'formatted_time': format_timestamp(timestamp),
                'message_count': activity_by_window[window],
                'messages': messages
            })
    return sorted(moment_data, key=lambda x: x['timestamp'])

def validate_input(window_size: int, num_moments: int) -> None:
    """Validate input parameters for analyze_chat_moments."""
    if window_size <= 0:
        raise ValueError("window_size must be greater than 0")
    if num_moments <= 0:
        raise ValueError("num_moments must be greater than 0")

def analyze_chat_moments(chat_data: List[Dict], window_size: int = DEFAULT_WINDOW_SIZE, 
                         start_time: Optional[int] = None, end_time: Optional[int] = None,
                         num_moments: int = DEFAULT_NUM_MOMENTS) -> List[Dict]:
    """
    Analyze chat data to identify top moments of activity.
    
    Returns a list of dictionaries containing detailed data for top chat moments.
    """
    if not chat_data:
        return []
    
    validate_input(window_size, num_moments)
    
    messages_by_window = group_messages_by_window(chat_data, window_size, start_time, end_time)
    
    if not messages_by_window:
        return []
    
    if start_time is not None and end_time is not None:
        total_windows = (end_time - start_time) // window_size + 1
        for window in range(total_windows):
            if window not in messages_by_window:
                messages_by_window[window] = []
    
    activity_by_window = calculate_activity(messages_by_window)
    top_moments = select_top_moments(activity_by_window, num_moments)
    return create_moment_data(top_moments, messages_by_window, activity_by_window, window_size)

def format_timestamp(seconds: int) -> str:
    """Convert seconds to a formatted string."""
    return str(timedelta(seconds=seconds))

def format_output(top_moments: List[Dict], num_messages: Optional[int]) -> str:
    """Format the output for top chat moments."""
    if not top_moments:
        return create_summary([], [])

    max_count = max(moment['message_count'] for moment in top_moments)
    output = []
    for moment in top_moments:
        formatted_time = moment['formatted_time']
        message_count = moment['message_count']
        
        # Scale the bar length relative to the maximum count
        bar_length = int((message_count / max_count) * MAX_BAR_LENGTH)
        visualization = f"{formatted_time} | {'-' * bar_length} | {message_count} messages"
        output.append(visualization)
        
        if num_messages is not None:
            messages = [f"  - {msg['message']}" for msg in moment['messages'][:num_messages]]
            output.append("\n".join(messages))
    
    message_counts = [moment['message_count'] for moment in top_moments]
    summary = create_summary(top_moments, message_counts)
    
    return "\n\n".join(output) + summary

def create_summary(top_moments: List[Dict], message_counts: List[int]) -> str:
    """Create a summary of the analysis results."""
    summary = f"\nAnalysis Summary:\n"
    summary += f"Total moments analyzed: {len(top_moments)}\n"
    if message_counts:
        avg_messages = sum(message_counts) / len(message_counts)
        summary += f"Average messages per moment: {avg_messages:.2f}\n"
        summary += f"Max messages in a moment: {max(message_counts)}\n"
        summary += f"Min messages in a moment: {min(message_counts)}"
    else:
        summary += "Average messages per moment: 0.00\n"
        summary += "No messages found in the specified range."
    return summary

def main() -> None:
    """Main function to run the Twitch chat analyzer."""
    parser = argparse.ArgumentParser(description="Analyze Twitch chat moments")
    parser.add_argument("-f", "--file", type=str, required=True, 
                        help="Path to the JSON file containing Twitch chat data")
    parser.add_argument("-n", "--num_messages", type=int, default=None, 
                        help="Number of messages to display for each moment")
    parser.add_argument("-w", "--window_size", type=int, default=DEFAULT_WINDOW_SIZE,
                        help=f"Size of the time window in seconds (default: {DEFAULT_WINDOW_SIZE})")
    parser.add_argument("-s", "--start_time", type=str, default=None,
                        help="Start time for analysis in HH:MM:SS format (default: beginning of chat)")
    parser.add_argument("-e", "--end_time", type=str, default=None,
                        help="End time for analysis in HH:MM:SS format (default: end of chat)")
    parser.add_argument("-m", "--num_moments", type=int, default=DEFAULT_NUM_MOMENTS,
                        help=f"Number of top moments to analyze (default: {DEFAULT_NUM_MOMENTS})")
    args = parser.parse_args()

    chat_data = load_chat_data(args.file)
    if not chat_data:
        return

    start_time = time_to_seconds(args.start_time) if args.start_time else None
    end_time = time_to_seconds(args.end_time) if args.end_time else None

    moments = analyze_chat_moments(chat_data, window_size=args.window_size,
                                   start_time=start_time, end_time=end_time,
                                   num_moments=args.num_moments)

    print(f"Number of moments analyzed: {len(moments)}")

    output = format_output(moments, args.num_messages)
    print(output)

def load_chat_data(file_path: str) -> Optional[List[Dict]]:
    """Load chat data from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except json.JSONDecodeError:
        print(f"Error: '{file_path}' is not a valid JSON file.")
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
    return None

if __name__ == "__main__":
    main()