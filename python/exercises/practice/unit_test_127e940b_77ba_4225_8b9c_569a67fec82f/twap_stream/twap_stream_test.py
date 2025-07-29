import unittest
import time
import threading
from twap_stream import TWAPStream

class TestTWAPStream(unittest.TestCase):
    def setUp(self):
        # Initialize the TWAP stream with a window size of 5000 milliseconds.
        self.stream = TWAPStream(window_ms=5000)

    def test_empty_twap(self):
        # When no trades have been recorded for an asset, TWAP should return 0.0.
        self.assertEqual(self.stream.get_twap("AAPL"), 0.0)

    def test_single_asset_multiple_trades(self):
        # Insert two trades for asset AAPL.
        # The TWAP is calculated using the last trade's timestamp as the current time.
        self.stream.update_trade(1000, "AAPL", 150.0, 10)
        self.stream.update_trade(3000, "AAPL", 155.0, 20)
        # For AAPL, current time is 3000; window start = 3000 - 5000 = -2000.
        # Trade 1: weight = (1000 - (-2000)) / 5000 = 3000/5000 = 0.6
        # Trade 2: weight = (3000 - (-2000)) / 5000 = 5000/5000 = 1.0
        # Numerator = 150*10*0.6 + 155*20*1.0 = 900 + 3100 = 4000
        # Denominator = 10*0.6 + 20*1.0 = 6 + 20 = 26
        # Expected TWAP = 4000 / 26 = 153.8461538 ~ 153.8462
        self.assertAlmostEqual(self.stream.get_twap("AAPL"), 153.8462, places=4)

    def test_trade_out_of_window(self):
        # Insert two trades that will fall out of the window after a later trade.
        self.stream.update_trade(1000, "GOOG", 1000.0, 5)
        self.stream.update_trade(2000, "GOOG", 1010.0, 10)
        # Insert a trade that pushes the current time forward.
        self.stream.update_trade(8000, "GOOG", 1020.0, 15)
        # For GOOG, current time is 8000; window start = 8000 - 5000 = 3000.
        # Only the trade at 8000 is within the window.
        # Weight = (8000 - 3000) / 5000 = 1.0, so TWAP = 1020*15/15 = 1020.0
        self.assertEqual(self.stream.get_twap("GOOG"), 1020.0)

    def test_multiple_assets(self):
        # Insert trades for multiple assets and verify individual TWAP calculations.
        self.stream.update_trade(1000, "AAPL", 150.0, 10)
        self.stream.update_trade(1100, "GOOG", 1000.0, 5)
        self.stream.update_trade(1200, "MSFT", 200.0, 20)
        self.stream.update_trade(2000, "AAPL", 155.0, 10)
        self.stream.update_trade(2100, "GOOG", 1005.0, 5)
        self.stream.update_trade(2200, "MSFT", 205.0, 20)

        # For each asset, use the time of its latest trade to compute the TWAP.
        # AAPL: current time = 2000, window start = 2000 - 5000 = -3000.
        #   Trade 1: (1000 - (-3000)) / 5000 = 4000/5000 = 0.8
        #   Trade 2: (2000 - (-3000)) / 5000 = 5000/5000 = 1.0
        #   Numerator: 150*10*0.8 + 155*10*1.0 = 1200 + 1550 = 2750
        #   Denom: 10*0.8 + 10*1.0 = 8 + 10 = 18 => TWAP = 2750/18 = 152.7778
        # GOOG: current time = 2100, window start = 2100 - 5000 = -2900.
        #   Trade 1: (1100 - (-2900)) / 5000 = 4000/5000 = 0.8
        #   Trade 2: (2100 - (-2900)) / 5000 = 5000/5000 = 1.0
        #   Numerator: 1000*5*0.8 + 1005*5*1.0 = 4000 + 5025 = 9025
        #   Denom: 5*0.8 + 5*1.0 = 4 + 5 = 9 => TWAP = 9025/9 = 1002.7778
        # MSFT: current time = 2200, window start = 2200 - 5000 = -2800.
        #   Trade 1: (1200 - (-2800)) / 5000 = 4000/5000 = 0.8
        #   Trade 2: (2200 - (-2800)) / 5000 = 5000/5000 = 1.0
        #   Numerator: 200*20*0.8 + 205*20*1.0 = 3200 + 4100 = 7300
        #   Denom: 20*0.8 + 20*1.0 = 16 + 20 = 36 => TWAP = 7300/36 = 202.7778
        aapl_twap = self.stream.get_twap("AAPL")
        goog_twap = self.stream.get_twap("GOOG")
        msft_twap = self.stream.get_twap("MSFT")
        self.assertAlmostEqual(aapl_twap, 152.7778, places=4)
        self.assertAlmostEqual(goog_twap, 1002.7778, places=4)
        self.assertAlmostEqual(msft_twap, 202.7778, places=4)

    def test_concurrent_updates(self):
        # Test that the system correctly processes concurrent trade updates.
        def update_data(asset, base_time):
            for i in range(10):
                ts = base_time + i * 500
                price = 100.0 + i
                volume = 10 + i
                self.stream.update_trade(ts, asset, price, volume)
                time.sleep(0.01)
        
        threads = [
            threading.Thread(target=update_data, args=("AAPL", 1000)),
            threading.Thread(target=update_data, args=("GOOG", 1500)),
            threading.Thread(target=update_data, args=("MSFT", 2000))
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Ensure that each asset now has a non-zero TWAP.
        self.assertNotEqual(self.stream.get_twap("AAPL"), 0.0)
        self.assertNotEqual(self.stream.get_twap("GOOG"), 0.0)
        self.assertNotEqual(self.stream.get_twap("MSFT"), 0.0)

if __name__ == '__main__':
    unittest.main()