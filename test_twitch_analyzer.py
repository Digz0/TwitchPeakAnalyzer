import unittest
import json
import os
import tempfile
from unittest.mock import patch, call
from twitch_analyzer import (
    calculate_message_frequency,
    find_top_windows,
    find_least_active_window,
    find_least_active_windows_for_tops,
    load_chat_data,
    plot_chat_activity,
    main
)

class TestTwitchAnalyzer(unittest.TestCase):

    def setUp(self):
        self.sample_chat_data = [
            {'time_in_seconds': 5},
            {'time_in_seconds': 15},
            {'time_in_seconds': 25},
            {'time_in_seconds': 25},
        ]

    def test_calculate_message_frequency(self):
        frequency = calculate_message_frequency(self.sample_chat_data, window_size=10)
        self.assertEqual(frequency, [(0, 1), (1, 1), (2, 2)])

    def test_find_top_windows(self):
        frequency = [(0, 1), (1, 3), (2, 2), (3, 4), (4, 2)]
        top_windows = find_top_windows(frequency, num_top_windows=2)
        self.assertEqual(top_windows, [(3, 4), (1, 3)])

    def test_find_least_active_window(self):
        frequency = [(0, 2), (1, 1), (2, 3), (3, 2)]
        least_active = find_least_active_window(frequency, target_window=3, lookback_seconds=30, window_size=10)
        self.assertEqual(least_active, (1, 1))

    def test_find_least_active_windows_for_tops(self):
        frequency = [(0, 2), (1, 1), (2, 3), (3, 2)]
        top_windows = [(2, 3)]
        least_active = find_least_active_windows_for_tops(frequency, top_windows, lookback_seconds=30, window_size=10)
        self.assertEqual(least_active, [(1, 1)])

    def test_load_chat_data(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            json.dump(self.sample_chat_data, temp_file)
        
        loaded_data = load_chat_data(temp_file.name)
        self.assertEqual(loaded_data, self.sample_chat_data)
        
        os.unlink(temp_file.name)

    @patch('matplotlib.pyplot.savefig')
    def test_plot_chat_activity(self, mock_savefig):
        frequency = [(0, 1), (1, 2), (2, 3)]
        top_windows = [(2, 3)]
        least_active_before = [(1, 1)]
        window_size = 10

        plot_chat_activity(frequency, top_windows, least_active_before, window_size)
        
        mock_savefig.assert_called_once_with('chat_activity_analysis.png', dpi=300)

    @patch('twitch_analyzer.plot_chat_activity')
    @patch('twitch_analyzer.load_chat_data')
    def test_main_function(self, mock_load_data, mock_plot):
        mock_load_data.return_value = self.sample_chat_data
        
        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                main('test.json', generate_image=True)
                
                self.assertTrue(os.path.exists('slopes_data.json'))
                
                with open('slopes_data.json', 'r') as f:
                    peaks_data = json.load(f)
                
                self.assertIsInstance(peaks_data, list)
                self.assertTrue(all(
                    'time' in item and 
                    'before' in item and 
                    'top' in item 
                    for item in peaks_data))
                
                mock_load_data.assert_called_once_with('test.json')
                mock_plot.assert_called_once()
            finally:
                os.chdir(original_dir)

    @patch('twitch_analyzer.load_chat_data')
    def test_main_function_output_formatting(self, mock_load_data):
        mock_load_data.return_value = self.sample_chat_data
        
        with patch('builtins.print') as mock_print:
            main('test.json')
            
            # Check for expected output format
            mock_print.assert_any_call("Top 50 windows with most frequent messages and their preceding least active windows:")
            
            # Check that the final message about saving JSON is printed
            mock_print.assert_any_call("Activity data for browser extension saved as 'slopes_data.json'")

if __name__ == '__main__':
    unittest.main()
