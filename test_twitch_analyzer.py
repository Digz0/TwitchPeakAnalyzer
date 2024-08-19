"""
Test suite for the Twitch Chat Analyzer module.

This module contains unit tests for the functions in twitch_analyzer.py.
"""
import unittest
from twitch_analyzer import (
    group_messages_by_window, 
    calculate_activity, 
    select_top_moments, 
    create_moment_data, 
    analyze_chat_moments, 
    format_timestamp, 
    time_to_seconds,
    main,
    format_output
)
import io
import sys
import json
from unittest.mock import patch, mock_open
import re

class TestTwitchAnalyzer(unittest.TestCase):
    """Test cases for the Twitch Chat Analyzer module."""

    def setUp(self):
        """Set up test data."""
        self.sample_data = [
            {'time_in_seconds': 1, 'message': 'Hello'},
            {'time_in_seconds': 2, 'message': 'Hi'},
            {'time_in_seconds': 2, 'message': 'Hey'},
            {'time_in_seconds': 3, 'message': 'Wow'},
            {'time_in_seconds': 3, 'message': 'Amazing'},
            {'time_in_seconds': 3, 'message': 'Cool'},
            {'time_in_seconds': 14, 'message': 'Test1'},
            {'time_in_seconds': 14, 'message': 'Test2'},
            {'time_in_seconds': 15, 'message': 'Test3'},
        ]

    def test_analyze_chat_moments(self):
        """Test the analyze_chat_moments function."""
        result = analyze_chat_moments(self.sample_data)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(isinstance(moment, dict) for moment in result))
        self.assertTrue(all('timestamp' in moment for moment in result))
        self.assertTrue(all('formatted_time' in moment for moment in result))
        self.assertTrue(all('message_count' in moment for moment in result))
        self.assertTrue(all('messages' in moment for moment in result))

        result_custom = analyze_chat_moments(self.sample_data, window_size=5, num_moments=2)
        self.assertEqual(len(result_custom), 2)

        timestamps = [moment['timestamp'] for moment in result]
        self.assertEqual(timestamps, [1, 14])  # Update expected timestamps

        message_counts = [moment['message_count'] for moment in result]
        self.assertEqual(set(message_counts), {6, 3})
        self.assertTrue(any(moment['message_count'] == 6 for moment in result))

        result_range = analyze_chat_moments(self.sample_data, start_time=2, end_time=14)
        self.assertEqual(len(result_range), 2)
        self.assertTrue(all(2 <= moment['timestamp'] <= 14 for moment in result_range))
        self.assertEqual(result_range[0]['timestamp'], 2)
        self.assertEqual(result_range[1]['timestamp'], 14)

    def test_analyze_chat_moments_limit(self):
        """Test the analyze_chat_moments function with a large number of moments."""
        sample_data = [{'time_in_seconds': i, 'message': f'Message {i}'} for i in range(100)]
        result = analyze_chat_moments(sample_data, window_size=1, num_moments=50)
        self.assertEqual(len(result), 50)

    def test_group_messages_by_window(self):
        """Test the group_messages_by_window function."""
        result = group_messages_by_window(self.sample_data, 10)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 6)
        self.assertEqual(len(result[1]), 3)

        result_range = group_messages_by_window(self.sample_data, 10, start_time=2, end_time=14)
        self.assertEqual(len(result_range), 2)
        self.assertEqual(sum(len(messages) for messages in result_range.values()), 7)
        self.assertTrue(0 in result_range)
        self.assertTrue(1 in result_range)

    def test_calculate_activity(self):
        """Test the calculate_activity function."""
        messages_by_window = {
            0: [{'message': 'msg1'}, {'message': 'msg2'}, {'message': 'msg3'}],
            1: [{'message': 'msg4'}, {'message': 'msg5'}],
            2: [{'message': 'msg6'}],
            3: []
        }
        result = calculate_activity(messages_by_window)
        expected = {0: 3, 1: 2, 2: 1, 3: 0}
        self.assertEqual(result, expected)

    def test_select_top_moments(self):
        """Test the select_top_moments function."""
        activity_by_window = {0: 6, 1: 3, 2: 1}
        result = select_top_moments(activity_by_window, 2)
        self.assertEqual(result, [0, 1])

    def test_create_moment_data(self):
        """Test the create_moment_data function."""
        messages_by_window = {
            0: [{'time_in_seconds': 0, 'message': 'Test1'}],
            1: [{'time_in_seconds': 10, 'message': 'Test2'}]
        }
        activity_by_window = {0: 1, 1: 1}
        top_moments = [0, 1]

        result = create_moment_data(top_moments, messages_by_window, activity_by_window, 10)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['timestamp'], 0)
        self.assertEqual(result[1]['timestamp'], 10)

    def test_time_to_seconds(self):
        """Test the time_to_seconds function."""
        self.assertEqual(time_to_seconds("00:00:00"), 0)
        self.assertEqual(time_to_seconds("00:01:00"), 60)
        self.assertEqual(time_to_seconds("01:00:00"), 3600)
        self.assertEqual(time_to_seconds("01:30:30"), 5430)
        with self.assertRaises(ValueError):
            time_to_seconds("invalid")

    def test_format_timestamp(self):
        """Test the format_timestamp function."""
        self.assertEqual(format_timestamp(0), "0:00:00")
        self.assertEqual(format_timestamp(60), "0:01:00")
        self.assertEqual(format_timestamp(3600), "1:00:00")
        self.assertEqual(format_timestamp(5430), "1:30:30")
        self.assertEqual(format_timestamp(86400), "1 day, 0:00:00")

    def test_format_output_with_visualization(self):
        """Test the format_output function with visualization."""
        top_moments = [
            {
                'formatted_time': '4:07:20',
                'message_count': 82,
                'messages': [{'message': 'Test'} for _ in range(82)]
            }
        ]
        result = format_output(top_moments, num_messages=1)
        pattern = r"4:07:20 \| (-{82}) \(82 messages\)"
        self.assertTrue(re.search(pattern, result), "Visualization bar does not match expected length")
        self.assertIn("0       10      20      30      40      50      60      70      80      90      100", result)
        self.assertIn("|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|", result)
        self.assertIn("  - Test", result)
        self.assertIn("Analysis Summary:", result)

    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps([
        {'time_in_seconds': 120, 'message': 'Hello'},
        {'time_in_seconds': 125, 'message': 'Hi'},
        {'time_in_seconds': 130, 'message': 'Hey'}
    ]))
    @patch('sys.argv', ['twitch_analyzer.py', '-f', 'dummy.json', '-s', '00:02:00', '-e', '00:02:30'])
    def test_main_script_output_with_time_range(self, mock_file):
        """Test the main function output with a specific time range."""
        captured_output = io.StringIO()
        sys.stdout = captured_output

        with patch('argparse.ArgumentParser.parse_args') as mock_args:
            mock_args.return_value.file = 'dummy.json'
            mock_args.return_value.num_messages = None
            mock_args.return_value.window_size = 10
            mock_args.return_value.num_moments = 50
            mock_args.return_value.start_time = '00:02:00'
            mock_args.return_value.end_time = '00:02:30'
            main()

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("Time: 0:02:00", output)
        self.assertIn("Message Count: 2", output)
        self.assertIn("Time: 0:02:10", output)
        self.assertIn("Message Count: 1", output)
        self.assertIn("Total moments analyzed: 2", output)  # Update expected number of moments
        self.assertIn("Average messages per moment: 1.50", output)
        self.assertIn("Max messages in a moment: 2", output)
        self.assertIn("Min messages in a moment: 1", output)

    def test_analyze_chat_moments_message_count(self):
        """Test the analyze_chat_moments function for correct message counts."""
        sample_data = [
            {'time_in_seconds': 1, 'message': 'msg1'},
            {'time_in_seconds': 2, 'message': 'msg2'},
            {'time_in_seconds': 3, 'message': 'msg3'},
            {'time_in_seconds': 11, 'message': 'msg4'},
            {'time_in_seconds': 12, 'message': 'msg5'},
            {'time_in_seconds': 21, 'message': 'msg6'},
        ]
        result = analyze_chat_moments(sample_data, window_size=10, num_moments=3)
        expected_counts = [3, 2, 1]
        actual_counts = [moment['message_count'] for moment in result]
        self.assertEqual(actual_counts, expected_counts)

    def test_analyze_chat_moments_empty_data(self):
        """Test the analyze_chat_moments function with empty data."""
        result = analyze_chat_moments([])
        self.assertEqual(result, [])

    def test_analyze_chat_moments_single_window(self):
        """Test the analyze_chat_moments function with a single window."""
        data = [{'time_in_seconds': 1, 'message': 'msg'} for _ in range(10)]
        result = analyze_chat_moments(data, window_size=20)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['message_count'], 10)

    def test_analyze_chat_moments_no_messages_in_range(self):
        """Test the analyze_chat_moments function with no messages in the specified range."""
        data = [{'time_in_seconds': 1, 'message': 'msg'} for _ in range(10)]
        result = analyze_chat_moments(data, start_time=100, end_time=200)
        self.assertEqual(result, [])

    def test_analyze_chat_moments_consistency(self):
        """Test the analyze_chat_moments function for consistency in results."""
        data = [{'time_in_seconds': i, 'message': f'msg{i}'} for i in range(100)]
        result = analyze_chat_moments(data, window_size=10, num_moments=5)
        self.assertEqual(len(result), 5)
        self.assertEqual(result, sorted(result, key=lambda x: x['timestamp']))

    def test_main_file_not_found(self):
        """Test the main function when the input file is not found."""
        with patch('sys.argv', ['twitch_analyzer.py', '-f', 'nonexistent.json']):
            with patch('builtins.print') as mock_print:
                main()
                mock_print.assert_called_with("Error: File 'nonexistent.json' not found.")

    def test_main_invalid_json(self):
        """Test the main function with an invalid JSON file."""
        with patch('builtins.open', mock_open(read_data='invalid json')):
            with patch('sys.argv', ['twitch_analyzer.py', '-f', 'invalid.json']):
                with patch('builtins.print') as mock_print:
                    main()
                    mock_print.assert_called_with("Error: 'invalid.json' is not a valid JSON file.")

    def test_format_output_empty_moments(self):
        """Test the format_output function with empty moments."""
        result = format_output([], None)
        self.assertIn("Total moments analyzed: 0", result)
        self.assertIn("Average messages per moment: 0.00", result)
        self.assertIn("No messages found in the specified range.", result)

    def test_format_output_large_message_count(self):
        """Test the format_output function with a large message count."""
        moments = [{'formatted_time': '00:00:00', 'message_count': 1000, 'messages': []}]
        result = format_output(moments, None)
        self.assertIn("00:00:00 | " + "-" * 100 + " (1000 messages)", result)
        
if __name__ == '__main__':
    unittest.main()