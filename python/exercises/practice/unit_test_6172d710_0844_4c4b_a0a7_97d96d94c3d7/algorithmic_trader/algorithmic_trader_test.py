import unittest
import bisect
from algorithmic_trader import compute_trades

class AlgorithmicTraderTest(unittest.TestCase):
    def get_price_before(self, timestamp, stock_history):
        # Given a sorted list of stock_history tuples (timestamp, price),
        # return the price associated with the latest timestamp less than the given timestamp.
        times = [t for t, price in stock_history]
        index = bisect.bisect_left(times, timestamp) - 1
        return stock_history[index][1]

    def simulate_trading(self, trades, predictions, stock_history, initial_capital, transaction_cost, max_holdings, min_trade_size):
        capital = initial_capital
        holdings = 0
        for i, trade in enumerate(trades):
            pred_timestamp, _, _ = predictions[i]
            price = self.get_price_before(pred_timestamp, stock_history)

            # Check that the trade is a multiple of min_trade_size (if not zero)
            if trade != 0:
                self.assertEqual(abs(trade) % min_trade_size, 0, "Trade amount must be a multiple of min_trade_size")

            if trade > 0:
                # Buy trade: ensure that we have enough capital and do not exceed max_holdings
                cost = trade * price * (1 + transaction_cost)
                self.assertTrue(cost <= capital, "Not enough capital to perform the buy trade")
                capital -= cost
                holdings += trade
                self.assertLessEqual(holdings, max_holdings, "Holdings exceed max_holdings after buying")
            elif trade < 0:
                # Sell trade: ensure that we do not sell more shares than we hold
                self.assertTrue(holds := holdings, "Holdings should be non-negative")
                self.assertGreaterEqual(holds, abs(trade), "Attempted to sell more shares than held")
                revenue = abs(trade) * price * (1 - transaction_cost)
                capital += revenue
                holdings += trade  # trade is negative here
            # If trade == 0, nothing changes

            # Ensure capital is never negative
            self.assertGreaterEqual(capital, 0, "Capital went negative during trading simulation")

        # Final valuation using the latest available stock price
        final_price = stock_history[-1][1]
        final_value = capital + holdings * final_price
        return capital, holdings, final_value

    def test_single_window_buy(self):
        # One prediction with strong buy signal.
        predictions = [(2000, 0.95, 0.05)]
        stock_history = [(1000, 100.0), (1500, 102.0)]
        initial_capital = 10000.0
        transaction_cost = 0.01
        risk_aversion = 0.2
        max_holdings = 50
        min_trade_size = 1

        trades = compute_trades(predictions, initial_capital, transaction_cost,
                                risk_aversion, max_holdings, min_trade_size, stock_history)
        self.assertEqual(len(trades), len(predictions))
        for trade in trades:
            self.assertIsInstance(trade, int)

        capital, holdings, final_value = self.simulate_trading(trades, predictions, stock_history,
                                                               initial_capital, transaction_cost,
                                                               max_holdings, min_trade_size)
        self.assertGreaterEqual(holdings, 0)
        self.assertLessEqual(holdings, max_holdings)
        self.assertGreaterEqual(capital, 0)
        self.assertIsInstance(final_value, float)

    def test_single_window_no_trade(self):
        # One prediction with poor signal, hence no trade should be executed.
        predictions = [(2000, 0.2, -0.03)]
        stock_history = [(1000, 50.0), (1500, 51.0)]
        initial_capital = 5000.0
        transaction_cost = 0.01
        risk_aversion = 0.8
        max_holdings = 30
        min_trade_size = 1

        trades = compute_trades(predictions, initial_capital, transaction_cost,
                                risk_aversion, max_holdings, min_trade_size, stock_history)
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0], 0)

        capital, holdings, final_value = self.simulate_trading(trades, predictions, stock_history,
                                                               initial_capital, transaction_cost,
                                                               max_holdings, min_trade_size)
        self.assertEqual(holdings, 0)
        self.assertGreaterEqual(capital, 0)

    def test_multiple_windows(self):
        # Multiple predictions that should result in a mix of buys and sells.
        predictions = [
            (2000, 0.85, 0.03),   # Expect a buy trade
            (3000, 0.4, -0.02),   # Possibly no trade or partial sell
            (4000, 0.9, 0.04),    # Buy more shares
            (5000, 0.2, -0.03)    # Sell some shares if holdings exist
        ]
        stock_history = [
            (1000, 100.0),
            (1500, 102.0),
            (2500, 105.0),
            (3500, 107.0),
            (4500, 106.0),
            (5500, 108.0)
        ]
        initial_capital = 15000.0
        transaction_cost = 0.02
        risk_aversion = 0.5
        max_holdings = 200
        min_trade_size = 5

        trades = compute_trades(predictions, initial_capital, transaction_cost,
                                risk_aversion, max_holdings, min_trade_size, stock_history)
        self.assertEqual(len(trades), len(predictions))
        for trade in trades:
            self.assertIsInstance(trade, int)
            if trade != 0:
                self.assertEqual(abs(trade) % min_trade_size, 0, "Trade must be a multiple of min_trade_size")

        capital, holdings, final_value = self.simulate_trading(trades, predictions, stock_history,
                                                               initial_capital, transaction_cost,
                                                               max_holdings, min_trade_size)
        self.assertGreaterEqual(holdings, 0)
        self.assertLessEqual(holdings, max_holdings)
        self.assertGreaterEqual(capital, 0)
        self.assertIsInstance(final_value, float)

    def test_nonaligned_timestamps(self):
        # Predictions timestamps do not align exactly with the stock_history timestamps.
        predictions = [
            (2050, 0.7, 0.02),
            (3100, 0.3, -0.01),
            (4150, 0.8, 0.035)
        ]
        stock_history = [
            (1000, 80.0),
            (2000, 81.0),
            (3000, 82.0),
            (4000, 83.0),
            (5000, 84.0)
        ]
        initial_capital = 8000.0
        transaction_cost = 0.015
        risk_aversion = 0.3
        max_holdings = 150
        min_trade_size = 2

        trades = compute_trades(predictions, initial_capital, transaction_cost,
                                risk_aversion, max_holdings, min_trade_size, stock_history)
        self.assertEqual(len(trades), len(predictions))
        for trade in trades:
            self.assertIsInstance(trade, int)
            if trade != 0:
                self.assertEqual(abs(trade) % min_trade_size, 0, "Trade must be a multiple of min_trade_size")
                
        capital, holdings, final_value = self.simulate_trading(trades, predictions, stock_history,
                                                               initial_capital, transaction_cost,
                                                               max_holdings, min_trade_size)
        self.assertGreaterEqual(holdings, 0)
        self.assertLessEqual(holdings, max_holdings)
        self.assertGreaterEqual(capital, 0)
        self.assertIsInstance(final_value, float)

if __name__ == '__main__':
    unittest.main()