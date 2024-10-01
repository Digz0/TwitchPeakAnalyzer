import unittest
import json
import os
import tempfile
from unittest.mock import patch, call
from twitch_analyzer import (
    calculate_message_frequency,
    calculate_slopes,
    find_significant_slopes,
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
        self.assertEqual(frequency, {0: 1, 1: 1, 2: 2})

    def test_calculate_slopes(self):
        frequency = {0: 1, 1: 3, 2: 2, 3: 4}
        slopes = calculate_slopes(frequency)
        self.assertEqual(slopes, {1: 2, 2: -1, 3: 2})

    def test_calculate_slopes_ratio(self):
        frequency = {0: 1, 1: 2, 2: 1, 3: 4}
        slopes = calculate_slopes(frequency, method='ratio')
        expected = {1: 1.0, 2: -0.5, 3: 3.0}
        self.assertAlmostEqual(slopes[1], expected[1], places=6)
        self.assertAlmostEqual(slopes[2], expected[2], places=6)
        self.assertAlmostEqual(slopes[3], expected[3], places=6)

    def test_calculate_slopes_ratio_zero_division(self):
        frequency = {0: 0, 1: 2, 2: 0, 3: 3}
        slopes = calculate_slopes(frequency, method='ratio')
        self.assertEqual(slopes[1], float('inf'))
        self.assertEqual(slopes[2], -1)
        self.assertEqual(slopes[3], float('inf'))

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
            main('test.json', generate_image=True, slope_method='difference')
            
            mock_load_data.assert_called_once_with('test.json')
            mock_plot.assert_called_once()
            mock_print.assert_any_call("Chat activity analysis image saved as 'chat_activity_analysis.png'")
            
            # Reset mocks
            mock_load_data.reset_mock()
            mock_plot.reset_mock()
            mock_print.reset_mock()
            
            main('test.json', generate_image=True, slope_method='ratio')
            
            mock_load_data.assert_called_once_with('test.json')
            mock_plot.assert_called_once()
            mock_print.assert_any_call("Chat activity analysis image saved as 'chat_activity_analysis.png'")

    @patch('twitch_analyzer.plot_chat_activity')
    @patch('twitch_analyzer.load_chat_data')
    @patch('twitch_analyzer.calculate_message_frequency')
    @patch('twitch_analyzer.calculate_slopes')
    @patch('twitch_analyzer.find_significant_slopes')
    def test_main_function_with_custom_args(self, mock_find_slopes, mock_calc_slopes, mock_calc_freq, mock_load_data, mock_plot):
        mock_load_data.return_value = self.sample_chat_data
        
        main('test.json', window_size=20, num_peaks=30, generate_image=True, slope_method='ratio')
        
        mock_load_data.assert_called_once_with('test.json')
        mock_calc_freq.assert_called_once_with(self.sample_chat_data, 20)
        mock_calc_slopes.assert_called_once_with(mock_calc_freq.return_value, method='ratio')
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

    @patch('twitch_analyzer.load_chat_data')
    def test_main_function_creates_slopes_data_json(self, mock_load_data):
        mock_load_data.return_value = self.sample_chat_data
        
        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                main('test.json', window_size=10, num_peaks=2)
                
                self.assertTrue(os.path.exists('slopes_data.json'))
                
                with open('slopes_data.json', 'r') as f:
                    slopes_data = json.load(f)
                
                self.assertIsInstance(slopes_data, list)
                self.assertTrue(all('time' in item and 'slope' in item for item in slopes_data))
            finally:
                os.chdir(original_dir)

    @patch('twitch_analyzer.load_chat_data')
    @patch('twitch_analyzer.calculate_message_frequency')
    @patch('twitch_analyzer.calculate_slopes')
    @patch('twitch_analyzer.find_significant_slopes')
    def test_main_function_output_formatting(self, mock_find_slopes, mock_calc_slopes, mock_calc_freq, mock_load_data):
        mock_load_data.return_value = self.sample_chat_data
        mock_calc_freq.return_value = {0: 1, 1: 2}
        mock_calc_slopes.return_value = {1: 1}
        mock_find_slopes.return_value = [(1, 1)]
        
        with patch('builtins.print') as mock_print:
            main('test.json', slope_method='difference')
            mock_print.assert_any_call("Time: 0:00:10, Slope: +1")
            
            mock_print.reset_mock()
            
            main('test.json', slope_method='ratio')
            mock_print.assert_any_call("Time: 0:00:10, Ratio change: +1.00")

if __name__ == '__main__':
    unittest.main()