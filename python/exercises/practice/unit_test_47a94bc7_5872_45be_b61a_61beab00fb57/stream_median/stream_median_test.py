import unittest
from stream_median import MedianFinder

class TestStreamMedian(unittest.TestCase):
    def test_single_element(self):
        mf = MedianFinder()
        mf.add_number(5)
        self.assertEqual(mf.get_median(), 5.0)

    def test_two_elements(self):
        mf = MedianFinder()
        mf.add_number(1)
        mf.add_number(2)
        self.assertEqual(mf.get_median(), 1.5)

    def test_odd_count(self):
        mf = MedianFinder()
        mf.add_number(1)
        mf.add_number(3)
        mf.add_number(2)
        self.assertEqual(mf.get_median(), 2.0)

    def test_even_count(self):
        mf = MedianFinder()
        mf.add_number(1)
        mf.add_number(3)
        mf.add_number(2)
        mf.add_number(4)
        self.assertEqual(mf.get_median(), 2.5)

    def test_negative_numbers(self):
        mf = MedianFinder()
        mf.add_number(-1)
        mf.add_number(-2)
        mf.add_number(-3)
        self.assertEqual(mf.get_median(), -2.0)

    def test_mixed_numbers(self):
        mf = MedianFinder()
        mf.add_number(-1)
        mf.add_number(2)
        mf.add_number(0)
        mf.add_number(5)
        self.assertEqual(mf.get_median(), 1.0)

    def test_duplicates(self):
        mf = MedianFinder()
        mf.add_number(1)
        mf.add_number(1)
        mf.add_number(1)
        self.assertEqual(mf.get_median(), 1.0)

    def test_large_numbers(self):
        mf = MedianFinder()
        mf.add_number(1000000)
        mf.add_number(2000000)
        mf.add_number(3000000)
        self.assertEqual(mf.get_median(), 2000000.0)

    def test_sequential_ascending(self):
        mf = MedianFinder()
        for i in range(1, 101):
            mf.add_number(i)
        self.assertEqual(mf.get_median(), 50.5)

    def test_sequential_descending(self):
        mf = MedianFinder()
        for i in range(100, 0, -1):
            mf.add_number(i)
        self.assertEqual(mf.get_median(), 50.5)

    def test_random_order(self):
        mf = MedianFinder()
        nums = [5, 2, 8, 1, 9, 4, 6, 3, 7]
        for num in nums:
            mf.add_number(num)
        self.assertEqual(mf.get_median(), 5.0)

    def test_empty_stream(self):
        mf = MedianFinder()
        with self.assertRaises(ValueError):
            mf.get_median()

if __name__ == '__main__':
    unittest.main()