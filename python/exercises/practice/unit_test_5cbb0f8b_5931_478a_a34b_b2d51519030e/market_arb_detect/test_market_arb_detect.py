import unittest
from market_arb_detect.market_arb_detect import MarketArbDetector

class TestMarketArbDetector(unittest.TestCase):
    def setUp(self):
        self.detector = MarketArbDetector(data_retention_ms=1000)
    
    def test_single_stock_no_arbitrage(self):
        self.detector.process_quote(1000, "AAPL", "bid", 150.0, 100)
        self.detector.process_quote(1001, "AAPL", "ask", 151.0, 50)
        self.assertEqual(self.detector.get_arbitrage_opportunities(), [])
    
    def test_single_stock_with_arbitrage(self):
        self.detector.process_quote(1000, "AAPL", "bid", 150.0, 100)
        self.detector.process_quote(1001, "AAPL", "ask", 149.0, 50)
        self.assertEqual(self.detector.get_arbitrage_opportunities(), [(1001, "AAPL")])
    
    def test_multiple_stocks_with_arbitrage(self):
        self.detector.process_quote(1000, "AAPL", "bid", 150.0, 100)
        self.detector.process_quote(1001, "GOOG", "bid", 2500.0, 20)
        self.detector.process_quote(1002, "AAPL", "ask", 149.5, 50)
        self.detector.process_quote(1003, "GOOG", "ask", 2499.0, 10)
        self.assertEqual(
            sorted(self.detector.get_arbitrage_opportunities()),
            sorted([(1002, "AAPL"), (1003, "GOOG")])
        )
    
    def test_arbitrage_disappears_and_reappears(self):
        self.detector.process_quote(1000, "AAPL", "bid", 150.0, 100)
        self.detector.process_quote(1001, "AAPL", "ask", 149.0, 50)
        self.detector.process_execution(1002, "AAPL", 149.0, 50)
        self.detector.process_quote(1003, "AAPL", "bid", 150.0, 100)
        self.detector.process_quote(1004, "AAPL", "ask", 149.5, 50)
        self.assertEqual(
            self.detector.get_arbitrage_opportunities(),
            [(1001, "AAPL"), (1004, "AAPL")]
        )
    
    def test_data_retention_policy(self):
        self.detector.process_quote(1000, "AAPL", "bid", 150.0, 100)
        self.detector.process_quote(1001, "AAPL", "ask", 149.0, 50)
        self.detector.process_quote(2002, "AAPL", "bid", 150.0, 100)  # Old bid expired
        self.detector.process_quote(2003, "AAPL", "ask", 151.0, 50)
        self.assertEqual(self.detector.get_arbitrage_opportunities(), [(1001, "AAPL")])
    
    def test_concurrent_access(self):
        import threading
        
        def worker():
            for i in range(100):
                self.detector.process_quote(1000 + i, "AAPL", "bid", 150.0 + i, 100)
                self.detector.process_quote(1000 + i, "AAPL", "ask", 149.0 + i, 50)
        
        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Just verify no crashes occurred
        self.assertTrue(len(self.detector.get_arbitrage_opportunities()) > 0)
    
    def test_memory_constraint(self):
        # Test with large number of symbols
        for i in range(10000):
            symbol = f"STOCK_{i}"
            self.detector.process_quote(1000, symbol, "bid", 100.0, 10)
            self.detector.process_quote(1001, symbol, "ask", 99.0, 10)
        
        # Verify we can still process new data
        self.detector.process_quote(1002, "AAPL", "bid", 150.0, 100)
        self.detector.process_quote(1003, "AAPL", "ask", 149.0, 50)
        self.assertEqual(self.detector.get_arbitrage_opportunities()[-1], (1003, "AAPL"))

if __name__ == '__main__':
    unittest.main()