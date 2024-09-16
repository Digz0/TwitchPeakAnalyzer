import unittest
from twitch_analyzer import (
    calculate_message_frequency,
    calculate_slopes,
    find_significant_slopes,
    format_time
)

class TestTwitchAnalyzer(unittest.TestCase):

    def test_calculate_message_frequency(self):
        chat_data = [
            {'time_in_seconds': 5},
            {'time_in_seconds': 15},
            {'time_in_seconds': 25},
            {'time_in_seconds': 25},
        ]
        frequency = calculate_message_frequency(chat_data, window_size=10)
        self.assertEqual(frequency, {0: 1, 1: 1, 2: 2})

    def test_calculate_slopes(self):
        frequency = {0: 1, 1: 3, 2: 2, 3: 4}
        slopes = calculate_slopes(frequency)
        self.assertEqual(slopes, {1: 2, 2: -1, 3: 2})

    def test_find_significant_slopes(self):
        slopes = {1: 5, 2: -2, 3: 3, 4: -1, 5: 4, 6: -3}
        significant_slopes = find_significant_slopes(slopes, num_peaks=3, window_size=10)
        expected = [(1, 5), (2, -2), (3, 3), (4, -1), (5, 4), (6, -3)]
        self.assertEqual(significant_slopes, expected)

    def test_format_time(self):
        self.assertEqual(format_time(65), "0:01:05")
        self.assertEqual(format_time(3665), "1:01:05")

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

if __name__ == '__main__':
    unittest.main()
