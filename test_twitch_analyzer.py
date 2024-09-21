import unittest
import json
import os
import tempfile
from unittest.mock import patch, call
from twitch_analyzer import (
    calculate_message_frequency,
    calculate_slopes,
    find_significant_slopes,
    format_time,
    load_chat_data,
    plot_chat_activity,
    main,
    export_slopes_for_extension
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
        self.assertEqual(frequency, {0: 1, 1: 1, 2: 2})

    def test_calculate_slopes(self):
        frequency = {0: 1, 1: 3, 2: 2, 3: 4}
        slopes = calculate_slopes(frequency)
        self.assertEqual(slopes, {1: 2, 2: -1, 3: 2})

    def test_find_significant_slopes(self):
        slopes = {1: 5, 2: -2, 3: 3, 4: -3, 5: 4, 6: -1}
        significant_slopes = find_significant_slopes(slopes, num_peaks=3, window_size=10)
        expected = [(1, 5), (4, -3), (3, 3), (4, -3), (5, 4), (6, -1)]
        self.assertEqual(significant_slopes, expected)

    def test_find_significant_slopes_with_no_negatives(self):
        slopes = {1: 5, 2: 3, 3: 4}
        significant_slopes = find_significant_slopes(slopes, num_peaks=2, window_size=10)
        expected = [(1, 5), (3, 4)]
        self.assertEqual(significant_slopes, expected)

    def test_find_significant_slopes_with_distant_negatives(self):
        slopes = {1: 5, 2: 3, 10: -2, 20: 4, 21: -1}
        significant_slopes = find_significant_slopes(slopes, num_peaks=2, window_size=10)
        expected = [(1, 5), (20, 4), (21, -1)]
        self.assertEqual(significant_slopes, expected)

    def test_load_chat_data(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            json.dump(self.sample_chat_data, temp_file)
        
        loaded_data = load_chat_data(temp_file.name)
        self.assertEqual(loaded_data, self.sample_chat_data)
        
        os.unlink(temp_file.name)

    @patch('matplotlib.pyplot.savefig')
    def test_plot_chat_activity(self, mock_savefig):
        frequency = {0: 1, 1: 2, 2: 3}
        significant_slopes = [(1, 2), (2, -1)]
        window_size = 10

        plot_chat_activity(frequency, significant_slopes, window_size)
        
        mock_savefig.assert_called_once_with('chat_activity_analysis.png', dpi=300)

    @patch('twitch_analyzer.plot_chat_activity')
    @patch('twitch_analyzer.load_chat_data')
    def test_main_function(self, mock_load_data, mock_plot):
        mock_load_data.return_value = self.sample_chat_data
        
        with patch('builtins.print') as mock_print:
            main('test.json', generate_image=True)
            
            mock_load_data.assert_called_once_with('test.json')
            mock_plot.assert_called_once()
            mock_print.assert_any_call("Chat activity analysis image saved as 'chat_activity_analysis.png'")

    @patch('twitch_analyzer.plot_chat_activity')
    @patch('twitch_analyzer.load_chat_data')
    @patch('twitch_analyzer.calculate_message_frequency')
    @patch('twitch_analyzer.find_significant_slopes')
    def test_main_function_with_custom_args(self, mock_find_slopes, mock_calc_freq, mock_load_data, mock_plot):
        mock_load_data.return_value = self.sample_chat_data
        
        main('test.json', window_size=20, num_peaks=30, generate_image=True)
        
        mock_load_data.assert_called_once_with('test.json')
        mock_calc_freq.assert_called_once_with(self.sample_chat_data, 20)
        mock_find_slopes.assert_called_once()
        self.assertEqual(mock_find_slopes.call_args[0][1], 30)  # Check num_peaks argument
        self.assertEqual(mock_find_slopes.call_args[0][2], 20)  # Check window_size argument
        mock_plot.assert_called_once()

    def test_find_significant_slopes_with_steepest_negative(self):
        slopes = {1: 5, 2: -1, 3: -3, 4: -2, 5: 4, 6: -1, 7: -4}
        significant_slopes = find_significant_slopes(slopes, num_peaks=2, window_size=10)
        expected = [(1, 5), (7, -4), (5, 4), (7, -4)]
        self.assertEqual(significant_slopes, expected)

    def test_find_significant_slopes_steepest_negative(self):
        slopes = {1: 5, 2: -1, 3: -2, 4: -3, 5: 4, 6: -1, 7: -2}
        significant_slopes = find_significant_slopes(slopes, num_peaks=2, window_size=10)
        expected = [(1, 5), (4, -3), (5, 4), (7, -2)]
        self.assertEqual(significant_slopes, expected)

    def test_export_slopes_for_extension(self):
        significant_slopes = [(1, 5), (2, -3), (3, 4)]
        window_size = 10
        expected_output = [
            {"time": 10, "slope": 5},
            {"time": 20, "slope": -3},
            {"time": 30, "slope": 4}
        ]
        result = export_slopes_for_extension(significant_slopes, window_size)
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()
