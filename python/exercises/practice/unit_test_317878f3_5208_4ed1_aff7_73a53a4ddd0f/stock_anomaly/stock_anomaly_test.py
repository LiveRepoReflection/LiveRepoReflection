import unittest
import os
import tempfile
import io
import sys
from datetime import timedelta

# Import the module under test
from stock_anomaly import AnomalyDetector

# Helper function to convert seconds to nanoseconds
def sec_to_ns(seconds):
    return int(seconds * 1e9)

class TestAnomalyDetector(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for logging anomalies
        self.temp_log = tempfile.NamedTemporaryFile(delete=False)
        self.log_file = self.temp_log.name
        self.temp_log.close()
        # Initialize the detector with a 60-second window and z score threshold of 3.0
        self.detector = AnomalyDetector(window_size=60, z_threshold=3.0, log_file=self.log_file)
        # Capture stdout
        self.held_stdout = sys.stdout
        sys.stdout = io.StringIO()
    
    def tearDown(self):
        # Restore stdout
        sys.stdout = self.held_stdout
        # Remove temporary log file
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
    
    def test_no_anomaly(self):
        # Feed ticks with similar prices for a single stock and ensure no anomaly is reported.
        base_timestamp = sec_to_ns(1000)
        stock_id = "AAPL"
        prices = [100, 101, 99, 100, 100, 101, 99, 100, 100, 101]
        anomalies = []
        for i, price in enumerate(prices):
            tick = {
                'timestamp': base_timestamp + sec_to_ns(i),
                'stock_id': stock_id,
                'price': price,
                'volume': 10
            }
            result = self.detector.process_tick(tick)
            if result is not None:
                anomalies.append(result)
        self.assertEqual(len(anomalies), 0)
    
    def test_single_anomaly(self):
        # Feed ticks for a stock with small variation then an anomaly tick.
        base_timestamp = sec_to_ns(2000)
        stock_id = "GOOG"
        # Slight variation to build up a valid window
        normal_prices = [200, 202, 198, 201, 199, 202, 200, 203, 197, 200]
        anomaly_tick = None
        anomaly_found = False
        
        # Feed normal ticks
        for i, price in enumerate(normal_prices):
            tick = {
                'timestamp': base_timestamp + sec_to_ns(i),
                'stock_id': stock_id,
                'price': price,
                'volume': 15
            }
            result = self.detector.process_tick(tick)
            if result is not None:
                anomaly_found = True
        
        # At this point, no anomaly should have been detected.
        self.assertFalse(anomaly_found)
        
        # Create an anomaly tick that deviates by more than 3 standard deviations.
        anomaly_price = 210  # Significantly higher than normal prices.
        anomaly_tick = {
            'timestamp': base_timestamp + sec_to_ns(len(normal_prices)),
            'stock_id': stock_id,
            'price': anomaly_price,
            'volume': 15
        }
        result = self.detector.process_tick(anomaly_tick)
        self.assertIsNotNone(result)
        # Check that the result contains the required keys in its string representation.
        for key in ['timestamp', 'stock_id', 'price', 'volume', 'mu', 'sigma', 'z_score']:
            self.assertIn(key, result)
        
        # Verify that the anomaly was printed to stdout.
        output = sys.stdout.getvalue()
        self.assertIn("Anomaly:", output)
        self.assertIn(stock_id, output)
    
    def test_multiple_stocks(self):
        # Feed ticks for multiple stocks concurrently and check that anomalies are detected independently.
        base_timestamp = sec_to_ns(3000)
        stock_prices = {
            "AAPL": [150, 151, 149, 150, 150, 151, 149, 150],
            "MSFT": [250, 249, 251, 250, 250, 251, 249, 250]
        }
        # Feed normal ticks for both stocks.
        for i in range(len(stock_prices["AAPL"])):
            for stock, prices in stock_prices.items():
                tick = {
                    'timestamp': base_timestamp + sec_to_ns(i),
                    'stock_id': stock,
                    'price': prices[i],
                    'volume': 20
                }
                self.detector.process_tick(tick)
        
        # Feed an anomaly tick for AAPL only
        anomaly_tick = {
            'timestamp': base_timestamp + sec_to_ns(len(stock_prices["AAPL"])),
            'stock_id': "AAPL",
            'price': 170,  # Significantly higher than previous values.
            'volume': 20
        }
        result = self.detector.process_tick(anomaly_tick)
        self.assertIsNotNone(result)
        self.assertIn("AAPL", result)
        
        # For MSFT, feed a normal tick.
        normal_tick = {
            'timestamp': base_timestamp + sec_to_ns(len(stock_prices["AAPL"])),
            'stock_id': "MSFT",
            'price': 250,
            'volume': 20
        }
        result_msft = self.detector.process_tick(normal_tick)
        self.assertIsNone(result_msft)
    
    def test_sliding_window_expiration(self):
        # Test that ticks outside the 60-second sliding window are correctly expired.
        stock_id = "TEST"
        base_timestamp = sec_to_ns(4000)
        # Feed ticks for 70 seconds; the early ticks should expire.
        for i in range(0, 70, 5):  # every 5 seconds
            tick = {
                'timestamp': base_timestamp + sec_to_ns(i),
                'stock_id': stock_id,
                'price': 100 + (i % 3),  # some variation
                'volume': 5
            }
            self.detector.process_tick(tick)
        
        # After 70 seconds, the sliding window should contain only ticks from t >= base_timestamp+10 sec.
        # Now, feed an anomaly tick with a dramatically different price.
        anomaly_tick = {
            'timestamp': base_timestamp + sec_to_ns(70),
            'stock_id': stock_id,
            'price': 150,  # large jump
            'volume': 5
        }
        result = self.detector.process_tick(anomaly_tick)
        # Given that old ticks are expired, the mean in the current window should be lower,
        # and the anomaly should be detected.
        self.assertIsNotNone(result)
    
    def test_log_file_writing(self):
        # Feed an anomaly and then check that the log file has been written.
        base_timestamp = sec_to_ns(5000)
        stock_id = "LOGTST"
        normal_prices = [120, 121, 119, 120, 120, 121, 119, 120]
        for i, price in enumerate(normal_prices):
            tick = {
                'timestamp': base_timestamp + sec_to_ns(i),
                'stock_id': stock_id,
                'price': price,
                'volume': 8
            }
            self.detector.process_tick(tick)
        # Feed anomaly tick.
        anomaly_tick = {
            'timestamp': base_timestamp + sec_to_ns(len(normal_prices)),
            'stock_id': stock_id,
            'price': 140,  # significantly different
            'volume': 8
        }
        anomaly_result = self.detector.process_tick(anomaly_tick)
        self.assertIsNotNone(anomaly_result)
        
        # Ensure the log file has the anomaly report.
        with open(self.log_file, "r") as f:
            log_content = f.read()
        self.assertIn("Anomaly:", log_content)
        self.assertIn(stock_id, log_content)

if __name__ == '__main__':
    unittest.main()