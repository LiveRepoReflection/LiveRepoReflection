import unittest
import time
from datetime import datetime
import types
from algo_arb import detect_arbitrage_opportunities

class TestAlgoArb(unittest.TestCase):
    def test_empty_quote_stream(self):
        def empty_generator():
            return
            yield  # This will never execute but makes it a generator
        
        transaction_fees = {"ExchangeA": 0.01, "ExchangeB": 0.02}
        latency_matrix = {
            "ExchangeA": {"ExchangeA": 0, "ExchangeB": 5},
            "ExchangeB": {"ExchangeA": 5, "ExchangeB": 0}
        }
        max_trade_volume = 100
        staleness_threshold = 1000

        results = detect_arbitrage_opportunities(
            empty_generator(), transaction_fees, latency_matrix, 
            max_trade_volume, staleness_threshold
        )
        
        self.assertEqual(results, [], "Empty quote stream should return empty list")

    def test_no_arbitrage_opportunities(self):
        def quote_generator():
            # No arbitrage opportunity as ask_price(A) > bid_price(B)
            yield {
                "exchange_id": "ExchangeA",
                "stock_symbol": "AAPL",
                "timestamp": int(time.time() * 1000),
                "bid_price": 150.0,
                "ask_price": 151.0,
                "volume": 100
            }
            yield {
                "exchange_id": "ExchangeB",
                "stock_symbol": "AAPL",
                "timestamp": int(time.time() * 1000),
                "bid_price": 149.0,
                "ask_price": 150.0,
                "volume": 100
            }
        
        transaction_fees = {"ExchangeA": 0.01, "ExchangeB": 0.02}
        latency_matrix = {
            "ExchangeA": {"ExchangeA": 0, "ExchangeB": 5},
            "ExchangeB": {"ExchangeA": 5, "ExchangeB": 0}
        }
        max_trade_volume = 100
        staleness_threshold = 1000

        results = detect_arbitrage_opportunities(
            quote_generator(), transaction_fees, latency_matrix, 
            max_trade_volume, staleness_threshold
        )
        
        self.assertEqual(results, [], "No arbitrage opportunities should return empty list")

    def test_basic_arbitrage_opportunity(self):
        current_time = int(time.time() * 1000)
        
        def quote_generator():
            yield {
                "exchange_id": "ExchangeA",
                "stock_symbol": "AAPL",
                "timestamp": current_time,
                "bid_price": 150.0,
                "ask_price": 150.5,
                "volume": 100
            }
            yield {
                "exchange_id": "ExchangeB",
                "stock_symbol": "AAPL",
                "timestamp": current_time,
                "bid_price": 152.0,
                "ask_price": 152.5,
                "volume": 80
            }
        
        transaction_fees = {"ExchangeA": 0.01, "ExchangeB": 0.02}
        latency_matrix = {
            "ExchangeA": {"ExchangeA": 0, "ExchangeB": 0.05},
            "ExchangeB": {"ExchangeA": 0.05, "ExchangeB": 0}
        }
        max_trade_volume = 100
        staleness_threshold = 1000

        results = detect_arbitrage_opportunities(
            quote_generator(), transaction_fees, latency_matrix, 
            max_trade_volume, staleness_threshold
        )
        
        self.assertEqual(len(results), 1, "Should detect one arbitrage opportunity")
        opportunity = results[0]
        self.assertEqual(opportunity["stock_symbol"], "AAPL")
        self.assertEqual(opportunity["exchange_A"], "ExchangeA")
        self.assertEqual(opportunity["exchange_B"], "ExchangeB")
        self.assertEqual(opportunity["buy_price"], 150.5)
        self.assertEqual(opportunity["sell_price"], 152.0)
        self.assertEqual(opportunity["volume"], 80)  # Limited by exchange B's volume
        
        # Calculate expected profit
        expected_profit = (152.0 - 150.5 - 0.01 - 0.02 - 0.05 - 0.05) * 80
        self.assertAlmostEqual(opportunity["profit"], expected_profit, places=5)

    def test_multiple_arbitrage_opportunities(self):
        current_time = int(time.time() * 1000)
        
        def quote_generator():
            # AAPL quotes
            yield {
                "exchange_id": "ExchangeA",
                "stock_symbol": "AAPL",
                "timestamp": current_time,
                "bid_price": 150.0,
                "ask_price": 150.5,
                "volume": 100
            }
            yield {
                "exchange_id": "ExchangeB",
                "stock_symbol": "AAPL",
                "timestamp": current_time,
                "bid_price": 152.0,
                "ask_price": 152.5,
                "volume": 80
            }
            
            # GOOG quotes
            yield {
                "exchange_id": "ExchangeA",
                "stock_symbol": "GOOG",
                "timestamp": current_time,
                "bid_price": 2500.0,
                "ask_price": 2501.0,
                "volume": 10
            }
            yield {
                "exchange_id": "ExchangeB",
                "stock_symbol": "GOOG",
                "timestamp": current_time,
                "bid_price": 2505.0,
                "ask_price": 2506.0,
                "volume": 15
            }
        
        transaction_fees = {"ExchangeA": 0.1, "ExchangeB": 0.2}
        latency_matrix = {
            "ExchangeA": {"ExchangeA": 0, "ExchangeB": 0.5},
            "ExchangeB": {"ExchangeA": 0.5, "ExchangeB": 0}
        }
        max_trade_volume = 50
        staleness_threshold = 1000

        results = detect_arbitrage_opportunities(
            quote_generator(), transaction_fees, latency_matrix, 
            max_trade_volume, staleness_threshold
        )
        
        self.assertEqual(len(results), 2, "Should detect two arbitrage opportunities")
        
        # Sort results by stock symbol for deterministic testing
        results.sort(key=lambda x: x["stock_symbol"])
        
        # AAPL opportunity
        aapl = results[0]
        self.assertEqual(aapl["stock_symbol"], "AAPL")
        self.assertEqual(aapl["exchange_A"], "ExchangeA")
        self.assertEqual(aapl["exchange_B"], "ExchangeB")
        self.assertEqual(aapl["buy_price"], 150.5)
        self.assertEqual(aapl["sell_price"], 152.0)
        self.assertEqual(aapl["volume"], min(80, 50))  # Limited by max_trade_volume and ExchangeB's volume
        expected_profit = (152.0 - 150.5 - 0.1 - 0.2 - 0.5 - 0.5) * min(80, 50)
        self.assertAlmostEqual(aapl["profit"], expected_profit, places=5)
        
        # GOOG opportunity
        goog = results[1]
        self.assertEqual(goog["stock_symbol"], "GOOG")
        self.assertEqual(goog["exchange_A"], "ExchangeA")
        self.assertEqual(goog["exchange_B"], "ExchangeB")
        self.assertEqual(goog["buy_price"], 2501.0)
        self.assertEqual(goog["sell_price"], 2505.0)
        self.assertEqual(goog["volume"], 10)  # Limited by ExchangeA's volume
        expected_profit = (2505.0 - 2501.0 - 0.1 - 0.2 - 0.5 - 0.5) * 10
        self.assertAlmostEqual(goog["profit"], expected_profit, places=5)

    def test_stale_quotes(self):
        current_time = int(time.time() * 1000)
        stale_time = current_time - 2000  # 2 seconds ago
        
        def quote_generator():
            # Fresh quotes for AAPL
            yield {
                "exchange_id": "ExchangeA",
                "stock_symbol": "AAPL",
                "timestamp": current_time,
                "bid_price": 150.0,
                "ask_price": 150.5,
                "volume": 100
            }
            # Stale quote for AAPL on ExchangeB
            yield {
                "exchange_id": "ExchangeB",
                "stock_symbol": "AAPL",
                "timestamp": stale_time,
                "bid_price": 152.0,
                "ask_price": 152.5,
                "volume": 80
            }
            
            # Fresh quotes for GOOG
            yield {
                "exchange_id": "ExchangeA",
                "stock_symbol": "GOOG",
                "timestamp": current_time,
                "bid_price": 2500.0,
                "ask_price": 2501.0,
                "volume": 10
            }
            yield {
                "exchange_id": "ExchangeB",
                "stock_symbol": "GOOG",
                "timestamp": current_time,
                "bid_price": 2505.0,
                "ask_price": 2506.0,
                "volume": 15
            }
        
        transaction_fees = {"ExchangeA": 0.1, "ExchangeB": 0.2}
        latency_matrix = {
            "ExchangeA": {"ExchangeA": 0, "ExchangeB": 0.5},
            "ExchangeB": {"ExchangeA": 0.5, "ExchangeB": 0}
        }
        max_trade_volume = 100
        staleness_threshold = 1000  # 1 second threshold

        results = detect_arbitrage_opportunities(
            quote_generator(), transaction_fees, latency_matrix, 
            max_trade_volume, staleness_threshold
        )
        
        # AAPL should be excluded due to stale quote on ExchangeB
        # Only GOOG should have an arbitrage opportunity
        self.assertEqual(len(results), 1, "Should detect only one arbitrage opportunity (GOOG)")
        
        opportunity = results[0]
        self.assertEqual(opportunity["stock_symbol"], "GOOG")

    def test_updated_quotes(self):
        current_time = int(time.time() * 1000)
        
        def quote_generator():
            # Initial quotes (no arbitrage)
            yield {
                "exchange_id": "ExchangeA",
                "stock_symbol": "AAPL",
                "timestamp": current_time,
                "bid_price": 150.0,
                "ask_price": 151.0,
                "volume": 100
            }
            yield {
                "exchange_id": "ExchangeB",
                "stock_symbol": "AAPL",
                "timestamp": current_time,
                "bid_price": 149.0,
                "ask_price": 150.0,
                "volume": 100
            }
            
            # Updated quotes creating an arbitrage opportunity
            yield {
                "exchange_id": "ExchangeA",
                "stock_symbol": "AAPL",
                "timestamp": current_time + 100,  # 100ms later
                "bid_price": 150.0,
                "ask_price": 150.5,
                "volume": 100
            }
            yield {
                "exchange_id": "ExchangeB",
                "stock_symbol": "AAPL",
                "timestamp": current_time + 100,  # 100ms later
                "bid_price": 152.0,
                "ask_price": 152.5,
                "volume": 80
            }
        
        transaction_fees = {"ExchangeA": 0.01, "ExchangeB": 0.02}
        latency_matrix = {
            "ExchangeA": {"ExchangeA": 0, "ExchangeB": 0.05},
            "ExchangeB": {"ExchangeA": 0.05, "ExchangeB": 0}
        }
        max_trade_volume = 100
        staleness_threshold = 1000

        results = detect_arbitrage_opportunities(
            quote_generator(), transaction_fees, latency_matrix, 
            max_trade_volume, staleness_threshold
        )
        
        self.assertEqual(len(results), 1, "Should detect one arbitrage opportunity after quote update")
        opportunity = results[0]
        self.assertEqual(opportunity["stock_symbol"], "AAPL")
        self.assertEqual(opportunity["exchange_A"], "ExchangeA")
        self.assertEqual(opportunity["exchange_B"], "ExchangeB")
        self.assertEqual(opportunity["buy_price"], 150.5)
        self.assertEqual(opportunity["sell_price"], 152.0)

    def test_volume_constraints(self):
        current_time = int(time.time() * 1000)
        
        def quote_generator():
            yield {
                "exchange_id": "ExchangeA",
                "stock_symbol": "AAPL",
                "timestamp": current_time,
                "bid_price": 150.0,
                "ask_price": 150.5,
                "volume": 10  # Small volume on ExchangeA
            }
            yield {
                "exchange_id": "ExchangeB",
                "stock_symbol": "AAPL",
                "timestamp": current_time,
                "bid_price": 152.0,
                "ask_price": 152.5,
                "volume": 80
            }
        
        transaction_fees = {"ExchangeA": 0.01, "ExchangeB": 0.02}
        latency_matrix = {
            "ExchangeA": {"ExchangeA": 0, "ExchangeB": 0.05},
            "ExchangeB": {"ExchangeA": 0.05, "ExchangeB": 0}
        }
        max_trade_volume = 100
        staleness_threshold = 1000

        results = detect_arbitrage_opportunities(
            quote_generator(), transaction_fees, latency_matrix, 
            max_trade_volume, staleness_threshold
        )
        
        self.assertEqual(len(results), 1, "Should detect one arbitrage opportunity")
        opportunity = results[0]
        self.assertEqual(opportunity["volume"], 10, "Volume should be limited by ExchangeA's volume")
        
        # Test with max_trade_volume constraint
        max_trade_volume = 5  # Set smaller than both exchange volumes
        
        results = detect_arbitrage_opportunities(
            quote_generator(), transaction_fees, latency_matrix, 
            max_trade_volume, staleness_threshold
        )
        
        self.assertEqual(len(results), 1, "Should detect one arbitrage opportunity")
        opportunity = results[0]
        self.assertEqual(opportunity["volume"], 5, "Volume should be limited by max_trade_volume")

    def test_edge_case_zero_fees_and_latency(self):
        current_time = int(time.time() * 1000)
        
        def quote_generator():
            yield {
                "exchange_id": "ExchangeA",
                "stock_symbol": "AAPL",
                "timestamp": current_time,
                "bid_price": 150.0,
                "ask_price": 150.5,
                "volume": 100
            }
            yield {
                "exchange_id": "ExchangeB",
                "stock_symbol": "AAPL",
                "timestamp": current_time,
                "bid_price": 150.6,  # Just slightly higher than ask_price on ExchangeA
                "ask_price": 150.7,
                "volume": 80
            }
        
        transaction_fees = {"ExchangeA": 0.0, "ExchangeB": 0.0}
        latency_matrix = {
            "ExchangeA": {"ExchangeA": 0, "ExchangeB": 0},
            "ExchangeB": {"ExchangeA": 0, "ExchangeB": 0}
        }
        max_trade_volume = 100
        staleness_threshold = 1000

        results = detect_arbitrage_opportunities(
            quote_generator(), transaction_fees, latency_matrix, 
            max_trade_volume, staleness_threshold
        )
        
        self.assertEqual(len(results), 1, "Should detect one arbitrage opportunity with zero fees and latency")
        opportunity = results[0]
        self.assertEqual(opportunity["profit"], (150.6 - 150.5) * 80, "Profit calculation with zero fees and latency")

    def test_multiple_exchanges(self):
        current_time = int(time.time() * 1000)
        
        def quote_generator():
            # AAPL on three exchanges
            yield {
                "exchange_id": "ExchangeA",
                "stock_symbol": "AAPL",
                "timestamp": current_time,
                "bid_price": 150.0,
                "ask_price": 150.5,
                "volume": 100
            }
            yield {
                "exchange_id": "ExchangeB",
                "stock_symbol": "AAPL",
                "timestamp": current_time,
                "bid_price": 151.0,
                "ask_price": 151.5,
                "volume": 80
            }
            yield {
                "exchange_id": "ExchangeC",
                "stock_symbol": "AAPL",
                "timestamp": current_time,
                "bid_price": 152.0,
                "ask_price": 152.5,
                "volume": 60
            }
        
        transaction_fees = {"ExchangeA": 0.01, "ExchangeB": 0.02, "ExchangeC": 0.03}
        latency_matrix = {
            "ExchangeA": {"ExchangeA": 0, "ExchangeB": 0.05, "ExchangeC": 0.1},
            "ExchangeB": {"ExchangeA": 0.05, "ExchangeB": 0, "ExchangeC": 0.07},
            "ExchangeC": {"ExchangeA": 0.1, "ExchangeB": 0.07, "ExchangeC": 0}
        }
        max_trade_volume = 100
        staleness_threshold = 1000

        results = detect_arbitrage_opportunities(
            quote_generator(), transaction_fees, latency_matrix, 
            max_trade_volume, staleness_threshold
        )
        
        # Should find multiple arbitrage opportunities:
        # A -> B, A -> C, B -> C
        expected_opportunities = [
            ("ExchangeA", "ExchangeB"),
            ("ExchangeA", "ExchangeC"),
            ("ExchangeB", "ExchangeC")
        ]
        
        self.assertEqual(len(results), len(expected_opportunities), 
                         f"Should detect {len(expected_opportunities)} arbitrage opportunities")
        
        # Check each opportunity is in the expected set
        found_opportunities = [(opp["exchange_A"], opp["exchange_B"]) for opp in results]
        for expected in expected_opportunities:
            self.assertIn(expected, found_opportunities, f"Expected opportunity {expected} not found")

    def test_quote_generator_type(self):
        """Test that the function accepts a generator as input"""
        def quote_generator():
            yield {"exchange_id": "ExchangeA", "stock_symbol": "AAPL", "timestamp": int(time.time() * 1000),
                  "bid_price": 150.0, "ask_price": 151.0, "volume": 100}
            
        transaction_fees = {"ExchangeA": 0.01}
        latency_matrix = {"ExchangeA": {"ExchangeA": 0}}
        max_trade_volume = 100
        staleness_threshold = 1000
        
        # This should not raise a TypeError if the function accepts a generator
        detect_arbitrage_opportunities(
            quote_generator(), transaction_fees, latency_matrix, 
            max_trade_volume, staleness_threshold
        )
        
        # Also test with a list comprehension generator
        quotes = [{"exchange_id": "ExchangeA", "stock_symbol": "AAPL", "timestamp": int(time.time() * 1000),
                  "bid_price": 150.0, "ask_price": 151.0, "volume": 100}]
        quote_gen = (q for q in quotes)
        
        # This should also not raise a TypeError
        detect_arbitrage_opportunities(
            quote_gen, transaction_fees, latency_matrix, 
            max_trade_volume, staleness_threshold
        )

if __name__ == '__main__':
    unittest.main()