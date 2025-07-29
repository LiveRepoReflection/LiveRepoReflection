import unittest
from rtb_profit import optimize_bidding


class RtbProfitTest(unittest.TestCase):
    
    def test_single_round_simple(self):
        # Test a single round with 100% chance of value 10
        n = 1
        budget = 100.0
        transaction_cost = 0.01
        
        # Auction data: user value distribution, winning bid, second-highest bid
        rounds_data = [
            ([(10.0, 1.0)], -1, -1)  # First round, no previous data
        ]
        
        profit = optimize_bidding(n, budget, transaction_cost, rounds_data)
        # In this simple case, optimal bid would be just above 0 (since there's no competition info yet)
        # We don't assert the exact profit since the bidding strategy might vary
        self.assertIsInstance(profit, float)
    
    def test_multiple_rounds_simple(self):
        # Test multiple rounds with fixed value and consistent competition
        n = 3
        budget = 100.0
        transaction_cost = 0.01
        
        # Auction data: user value distribution, winning bid, second-highest bid
        rounds_data = [
            ([(10.0, 1.0)], -1, -1),  # First round, no previous data
            ([(10.0, 1.0)], 8.0, 7.0),  # Second round, competition bids high
            ([(10.0, 1.0)], 8.0, 7.0)   # Third round, competition still bids high
        ]
        
        profit = optimize_bidding(n, budget, transaction_cost, rounds_data)
        self.assertIsInstance(profit, float)
    
    def test_probabilistic_value(self):
        # Test with probabilistic user values
        n = 2
        budget = 100.0
        transaction_cost = 0.01
        
        # Auction data: user value distribution, winning bid, second-highest bid
        rounds_data = [
            ([(5.0, 0.3), (10.0, 0.5), (20.0, 0.2)], -1, -1),  # First round, mixed value distribution
            ([(5.0, 0.3), (10.0, 0.5), (20.0, 0.2)], 7.0, 5.0)  # Second round
        ]
        
        profit = optimize_bidding(n, budget, transaction_cost, rounds_data)
        self.assertIsInstance(profit, float)
    
    def test_changing_competition(self):
        # Test with changing competition behavior
        n = 3
        budget = 100.0
        transaction_cost = 0.01
        
        # Auction data: user value distribution, winning bid, second-highest bid
        rounds_data = [
            ([(10.0, 1.0)], -1, -1),    # First round, no previous data
            ([(10.0, 1.0)], 5.0, 3.0),  # Second round, moderate competition
            ([(10.0, 1.0)], 9.0, 8.0)   # Third round, higher competition
        ]
        
        profit = optimize_bidding(n, budget, transaction_cost, rounds_data)
        self.assertIsInstance(profit, float)
    
    def test_limited_budget(self):
        # Test with very limited budget
        n = 5
        budget = 10.0  # Limited budget
        transaction_cost = 0.01
        
        # Auction data: user value distribution, winning bid, second-highest bid
        rounds_data = [
            ([(20.0, 1.0)], -1, -1),    # First round, high value
            ([(20.0, 1.0)], 8.0, 7.0),  # Subsequent rounds
            ([(20.0, 1.0)], 9.0, 8.0),
            ([(20.0, 1.0)], 10.0, 9.0),
            ([(20.0, 1.0)], 11.0, 10.0)
        ]
        
        profit = optimize_bidding(n, budget, transaction_cost, rounds_data)
        self.assertIsInstance(profit, float)
        # With limited budget, algorithm should be more selective
    
    def test_high_transaction_cost(self):
        # Test with high transaction cost
        n = 3
        budget = 100.0
        transaction_cost = 0.05  # 5% transaction cost
        
        # Auction data: user value distribution, winning bid, second-highest bid
        rounds_data = [
            ([(10.0, 1.0)], -1, -1),   # First round
            ([(10.0, 1.0)], 6.0, 5.0), # Next rounds
            ([(10.0, 1.0)], 6.0, 5.0)
        ]
        
        profit = optimize_bidding(n, budget, transaction_cost, rounds_data)
        self.assertIsInstance(profit, float)
        # High transaction cost should lead to more conservative bidding
    
    def test_complex_scenario(self):
        # Test with complex and changing conditions
        n = 5
        budget = 200.0
        transaction_cost = 0.02
        
        # Auction data: user value distribution, winning bid, second-highest bid
        rounds_data = [
            ([(5.0, 0.2), (15.0, 0.6), (25.0, 0.2)], -1, -1),  # Round 1
            ([(8.0, 0.3), (12.0, 0.4), (20.0, 0.3)], 10.0, 8.0),  # Round 2
            ([(10.0, 0.5), (20.0, 0.5)], 15.0, 12.0),  # Round 3
            ([(5.0, 0.1), (10.0, 0.2), (15.0, 0.4), (25.0, 0.3)], 18.0, 15.0),  # Round 4
            ([(30.0, 1.0)], 25.0, 20.0)  # Round 5, high value user
        ]
        
        profit = optimize_bidding(n, budget, transaction_cost, rounds_data)
        self.assertIsInstance(profit, float)
    
    def test_large_scale(self):
        # Test with a large number of rounds
        n = 100
        budget = 1000.0
        transaction_cost = 0.01
        
        # Generate auction data with consistent patterns
        rounds_data = []
        
        # First round with no previous data
        rounds_data.append(([(10.0, 0.5), (20.0, 0.5)], -1, -1))
        
        # Subsequent rounds with slowly increasing competition
        for i in range(1, n):
            win_bid = 5.0 + (i * 0.1)
            second_bid = win_bid - 1.0
            if i % 10 == 0:  # Every 10 rounds, higher value users
                rounds_data.append(([(15.0, 0.3), (25.0, 0.7)], win_bid, second_bid))
            else:
                rounds_data.append(([(10.0, 0.5), (20.0, 0.5)], win_bid, second_bid))
        
        profit = optimize_bidding(n, budget, transaction_cost, rounds_data)
        self.assertIsInstance(profit, float)
    
    def test_edge_cases(self):
        # Test edge cases
        
        # Case 1: Minimum rounds
        n = 1
        budget = 10.0
        transaction_cost = 0.0  # No transaction cost
        rounds_data = [([(10.0, 1.0)], -1, -1)]
        profit = optimize_bidding(n, budget, transaction_cost, rounds_data)
        self.assertIsInstance(profit, float)
        
        # Case 2: Zero budget
        n = 3
        budget = 0.0
        transaction_cost = 0.01
        rounds_data = [
            ([(10.0, 1.0)], -1, -1),
            ([(10.0, 1.0)], 5.0, 4.0),
            ([(10.0, 1.0)], 6.0, 5.0)
        ]
        profit = optimize_bidding(n, budget, transaction_cost, rounds_data)
        self.assertEqual(profit, 0.0)  # With zero budget, profit should be zero
        
        # Case 3: Very high value with certainty
        n = 1
        budget = 1000.0
        transaction_cost = 0.01
        rounds_data = [([(100.0, 1.0)], -1, -1)]
        profit = optimize_bidding(n, budget, transaction_cost, rounds_data)
        self.assertIsInstance(profit, float)


if __name__ == '__main__':
    unittest.main()