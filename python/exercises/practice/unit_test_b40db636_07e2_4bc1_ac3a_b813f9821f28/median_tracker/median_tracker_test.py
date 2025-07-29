import unittest
from median_tracker import MedianTracker

class TestMedianTracker(unittest.TestCase):

    def setUp(self):
        # Create a new tracker instance before each test
        self.tracker = MedianTracker()

    def test_empty_tracker(self):
        # When no data centers or prices exist, median should be -1.
        self.assertEqual(self.tracker.get_global_median(), -1)

    def test_single_data_center_single_price(self):
        # Add a single data center and report one price.
        self.tracker.add_data_center("dc1")
        self.tracker.report_price("dc1", 100)
        self.assertEqual(self.tracker.get_global_median(), 100)

    def test_single_data_center_multiple_prices_odd(self):
        # With an odd number of prices in one data center.
        self.tracker.add_data_center("dc1")
        prices = [200, 50, 150]
        for price in prices:
            self.tracker.report_price("dc1", price)
        # Sorted prices: [50, 150, 200] -> median is 150.
        self.assertEqual(self.tracker.get_global_median(), 150)

    def test_single_data_center_multiple_prices_even(self):
        # With an even number of prices, pick the lower middle.
        self.tracker.add_data_center("dc1")
        prices = [300, 10, 200, 100]
        for price in prices:
            self.tracker.report_price("dc1", price)
        # Sorted prices: [10, 100, 200, 300] -> middle two are 100 and 200, so median is 100.
        self.assertEqual(self.tracker.get_global_median(), 100)

    def test_multiple_data_centers(self):
        # Add multiple data centers and report various prices.
        self.tracker.add_data_center("dc1")
        self.tracker.add_data_center("dc2")
        self.tracker.add_data_center("dc3")
        
        # Data center 1 reports prices: [40, 60]
        self.tracker.report_price("dc1", 40)
        self.tracker.report_price("dc1", 60)
        
        # Data center 2 reports prices: [20, 80, 100]
        self.tracker.report_price("dc2", 20)
        self.tracker.report_price("dc2", 80)
        self.tracker.report_price("dc2", 100)
        
        # Data center 3 reports prices: [50]
        self.tracker.report_price("dc3", 50)
        
        # Combined sorted prices: [20, 40, 50, 60, 80, 100]
        # Even number of prices, middle two: 50 and 60, lower is 50
        self.assertEqual(self.tracker.get_global_median(), 50)

    def test_remove_data_center(self):
        # Test removal of a data center and update in median calculation.
        self.tracker.add_data_center("dc1")
        self.tracker.add_data_center("dc2")
        
        # dc1: [10, 30]
        self.tracker.report_price("dc1", 10)
        self.tracker.report_price("dc1", 30)
        
        # dc2: [20, 40]
        self.tracker.report_price("dc2", 20)
        self.tracker.report_price("dc2", 40)
        
        # Combined sorted: [10, 20, 30, 40] -> median is 20 (lower middle of 20 and 30).
        self.assertEqual(self.tracker.get_global_median(), 20)
        
        # Remove dc1
        self.tracker.remove_data_center("dc1")
        
        # Now remaining prices: [20, 40] -> median is 20.
        self.assertEqual(self.tracker.get_global_median(), 20)
        
        # Remove dc2
        self.tracker.remove_data_center("dc2")
        # No prices remain, median should be -1.
        self.assertEqual(self.tracker.get_global_median(), -1)

    def test_data_center_out_of_order_reporting(self):
        # Add data centers and report multiple prices in arbitrary order.
        self.tracker.add_data_center("dcA")
        self.tracker.add_data_center("dcB")
        
        self.tracker.report_price("dcA", 500)
        self.tracker.report_price("dcA", 300)
        self.tracker.report_price("dcB", 400)
        self.tracker.report_price("dcB", 200)
        self.tracker.report_price("dcA", 100)
        
        # Combined prices: [500, 300, 100, 400, 200] sorted: [100, 200, 300, 400, 500]
        # Median is 300.
        self.assertEqual(self.tracker.get_global_median(), 300)

    def test_multiple_removals_and_additions(self):
        # Test sequence of operations with data centers added and removed repeatedly.
        self.tracker.add_data_center("dc1")
        self.tracker.add_data_center("dc2")
        self.tracker.report_price("dc1", 250)
        self.tracker.report_price("dc2", 750)
        
        # Median is lower of [250,750] -> 250.
        self.assertEqual(self.tracker.get_global_median(), 250)
        
        # Add another data center and report more prices.
        self.tracker.add_data_center("dc3")
        self.tracker.report_price("dc3", 500)
        # Combined prices: [250,500,750] -> median is 500.
        self.assertEqual(self.tracker.get_global_median(), 500)
        
        # Remove dc2, remaining prices: [250,500] -> median is 250.
        self.tracker.remove_data_center("dc2")
        self.assertEqual(self.tracker.get_global_median(), 250)
        
        # Report additional price to dc1, making dc1 prices: [250, 300]
        self.tracker.report_price("dc1", 300)
        # Combined prices: [250,300,500] -> median is 300.
        self.assertEqual(self.tracker.get_global_median(), 300)
        
        # Remove dc1; remaining prices: [500] -> median is 500.
        self.tracker.remove_data_center("dc1")
        self.assertEqual(self.tracker.get_global_median(), 500)

    def test_invalid_data_center_removal(self):
        # Removing a non-existent data center should not alter the global median.
        self.tracker.add_data_center("dc1")
        self.tracker.report_price("dc1", 100)
        # Try to remove a data center that wasn't added. Expect no changes.
        try:
            self.tracker.remove_data_center("non_existent_dc")
        except Exception as e:
            self.fail("remove_data_center raised an exception for non-existent data center: " + str(e))
        self.assertEqual(self.tracker.get_global_median(), 100)

if __name__ == '__main__':
    unittest.main()