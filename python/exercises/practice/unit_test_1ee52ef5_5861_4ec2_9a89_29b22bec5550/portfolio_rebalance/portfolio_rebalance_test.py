import unittest
from portfolio_rebalance import rebalance_portfolio

class PortfolioRebalanceTest(unittest.TestCase):
    def test_empty_holdings_and_target(self):
        # Test with empty current holdings and target allocation
        result = rebalance_portfolio({}, {}, {"AAPL": 150.0}, 0.01, 10, 10000.0, 5, 5)
        self.assertEqual(result, ([], {}, 0))  # No orders should be generated

    def test_no_rebalancing_needed(self):
        # Test when counter hasn't reached the rebalancing interval
        target_allocation = {"AAPL": 0.5, "GOOG": 0.3, "MSFT": 0.2}
        current_holdings = {"AAPL": 100, "GOOG": 20, "MSFT": 50}
        price_update = {"AAPL": 150.0, "GOOG": 2000.0, "MSFT": 300.0}
        
        # Counter (4) is still less than rebalancing_interval (5)
        result = rebalance_portfolio(
            target_allocation, current_holdings, price_update, 0.01, 10, 10000.0, 5, 4
        )
        
        # Should increment counter but not rebalance
        self.assertEqual(result[0], [])  # No orders
        self.assertEqual(result[1], current_holdings)  # Holdings unchanged
        self.assertEqual(result[2], 5)  # Counter incremented

    def test_basic_rebalancing(self):
        # Test when rebalancing is needed and triggered
        target_allocation = {"AAPL": 0.5, "GOOG": 0.5}
        current_holdings = {"AAPL": 100, "GOOG": 10}
        price_update = {"AAPL": 100.0, "GOOG": 500.0}
        
        # Counter equals rebalancing_interval - should trigger rebalance
        result = rebalance_portfolio(
            target_allocation, current_holdings, price_update, 0.01, 1, 10000.0, 5, 5
        )
        
        # Total portfolio value = 100*100 + 10*500 = 15000
        # Target for AAPL = 0.5 * 15000 = 7500, which is 75 shares at $100 each
        # Target for GOOG = 0.5 * 15000 = 7500, which is 15 shares at $500 each
        # Should sell 25 AAPL and buy 5 GOOG
        
        orders = result[0]
        updated_holdings = result[1]
        
        # Check that counter was reset
        self.assertEqual(result[2], 0)
        
        # Verify we have some orders and holdings have changed
        self.assertTrue(len(orders) > 0)
        self.assertNotEqual(current_holdings, updated_holdings)
        
        # Convert orders to a dictionary for easier verification
        order_dict = {}
        for symbol, shares in orders:
            order_dict[symbol] = shares
        
        # Verify the directions of trades are correct
        if "AAPL" in order_dict:
            self.assertTrue(order_dict["AAPL"] < 0)  # Should sell AAPL
        if "GOOG" in order_dict:
            self.assertTrue(order_dict["GOOG"] > 0)  # Should buy GOOG

    def test_min_trade_size_constraint(self):
        # Test that trades below min_trade_size are not executed
        target_allocation = {"AAPL": 0.51, "GOOG": 0.49}
        current_holdings = {"AAPL": 100, "GOOG": 20}
        price_update = {"AAPL": 100.0, "GOOG": 250.0}
        
        # Setting a high minimum trade size to force no trades
        result = rebalance_portfolio(
            target_allocation, current_holdings, price_update, 0.01, 50, 10000.0, 5, 5
        )
        
        # The difference is slight, so with a high min_trade_size, no trades should occur
        self.assertEqual(result[0], [])
        self.assertEqual(result[1], current_holdings)
        self.assertEqual(result[2], 0)  # Counter still resets when rebalance is triggered

    def test_max_trade_value_constraint(self):
        target_allocation = {"AAPL": 0.2, "GOOG": 0.8}
        current_holdings = {"AAPL": 200, "GOOG": 10}
        price_update = {"AAPL": 100.0, "GOOG": 1000.0}
        
        # Set a low max_trade_value to limit order sizes
        max_trade_value = 5000.0
        result = rebalance_portfolio(
            target_allocation, current_holdings, price_update, 0.01, 1, max_trade_value, 5, 5
        )
        
        orders = result[0]
        # Check that no single order exceeds max_trade_value
        for symbol, shares in orders:
            trade_value = abs(shares) * price_update[symbol]
            self.assertLessEqual(trade_value, max_trade_value)

    def test_sell_stocks_not_in_target(self):
        # Test that stocks in holdings but not in target are sold
        target_allocation = {"AAPL": 0.5, "GOOG": 0.5}
        current_holdings = {"AAPL": 100, "GOOG": 20, "MSFT": 50}
        price_update = {"AAPL": 100.0, "GOOG": 500.0, "MSFT": 200.0}
        
        result = rebalance_portfolio(
            target_allocation, current_holdings, price_update, 0.01, 1, 10000.0, 5, 5
        )
        
        orders = result[0]
        updated_holdings = result[1]
        
        # Check that MSFT is being sold
        order_dict = {}
        for symbol, shares in orders:
            order_dict[symbol] = shares
        
        if "MSFT" in order_dict:
            self.assertTrue(order_dict["MSFT"] < 0)  # Should sell MSFT
        
        # MSFT should be either removed from holdings or have 0 shares
        self.assertTrue("MSFT" not in updated_holdings or updated_holdings["MSFT"] == 0)

    def test_transaction_costs(self):
        # Test that transaction costs are considered in rebalancing
        target_allocation = {"AAPL": 0.5, "GOOG": 0.5}
        current_holdings = {"AAPL": 100, "GOOG": 20}
        price_update = {"AAPL": 100.0, "GOOG": 250.0}
        
        # Execute with zero transaction cost
        result_no_cost = rebalance_portfolio(
            target_allocation, current_holdings, price_update, 0.0, 1, 10000.0, 5, 5
        )
        
        # Execute with high transaction cost
        result_high_cost = rebalance_portfolio(
            target_allocation, current_holdings, price_update, 0.05, 1, 10000.0, 5, 5
        )
        
        # There should be more aggressive rebalancing with no transaction cost
        if len(result_no_cost[0]) > 0 and len(result_high_cost[0]) > 0:
            total_shares_traded_no_cost = sum(abs(shares) for _, shares in result_no_cost[0])
            total_shares_traded_high_cost = sum(abs(shares) for _, shares in result_high_cost[0])
            self.assertGreaterEqual(total_shares_traded_no_cost, total_shares_traded_high_cost)

    def test_new_stock_in_target(self):
        # Test handling of stocks in target but not currently held
        target_allocation = {"AAPL": 0.4, "GOOG": 0.4, "TSLA": 0.2}
        current_holdings = {"AAPL": 100, "GOOG": 20}
        price_update = {"AAPL": 100.0, "GOOG": 500.0, "TSLA": 800.0}
        
        result = rebalance_portfolio(
            target_allocation, current_holdings, price_update, 0.01, 1, 10000.0, 5, 5
        )
        
        orders = result[0]
        updated_holdings = result[1]
        
        order_dict = {}
        for symbol, shares in orders:
            order_dict[symbol] = shares
        
        # Should buy TSLA since it's in target but not in holdings
        if "TSLA" in order_dict:
            self.assertTrue(order_dict["TSLA"] > 0)
        
        # TSLA should appear in updated holdings
        self.assertTrue("TSLA" in updated_holdings)

    def test_zero_values_in_target(self):
        # Test with zero values in target allocation
        target_allocation = {"AAPL": 0.0, "GOOG": 1.0}
        current_holdings = {"AAPL": 100, "GOOG": 20}
        price_update = {"AAPL": 100.0, "GOOG": 500.0}
        
        result = rebalance_portfolio(
            target_allocation, current_holdings, price_update, 0.01, 1, 10000.0, 5, 5
        )
        
        orders = result[0]
        updated_holdings = result[1]
        
        order_dict = {}
        for symbol, shares in orders:
            order_dict[symbol] = shares
        
        # Should sell all AAPL since target is 0
        if "AAPL" in order_dict:
            self.assertEqual(order_dict["AAPL"], -100)
        
        # AAPL should be either removed from holdings or have 0 shares
        self.assertTrue("AAPL" not in updated_holdings or updated_holdings["AAPL"] == 0)

    def test_missing_price_updates(self):
        # Test when price_update is missing some stocks
        target_allocation = {"AAPL": 0.5, "GOOG": 0.5}
        current_holdings = {"AAPL": 100, "GOOG": 20}
        # Missing GOOG price update
        price_update = {"AAPL": 100.0}
        
        # Should not rebalance because of missing price data
        result = rebalance_portfolio(
            target_allocation, current_holdings, price_update, 0.01, 1, 10000.0, 5, 5
        )
        
        # Should not trade without complete price information
        self.assertEqual(result[0], [])
        self.assertEqual(result[1], current_holdings)
        # Even though we don't rebalance, the counter should reset as the interval was reached
        self.assertEqual(result[2], 0)

if __name__ == "__main__":
    unittest.main()