import unittest
import time
import random
from unittest.mock import MagicMock, patch
from rtb_optimizer import optimize_rtb


class TestRTBOptimizer(unittest.TestCase):
    def setUp(self):
        # Define a simple model and bidding strategy for testing
        self.model = lambda user_id, ad_slot, user_context: random.uniform(0.1, 0.9)
        self.bidding_strategy = lambda predicted_value: predicted_value * 2.0
        
        # Generate a set of sample bid requests for testing
        self.generate_test_bid_requests()
        
    def generate_test_bid_requests(self):
        """Generate sample bid requests for testing."""
        self.bid_requests = []
        current_time = time.time()
        
        # Generate 100 sample bid requests
        for i in range(100):
            self.bid_requests.append({
                'user_id': f'user_{i}',
                'ad_slot': f'slot_{i % 10}',
                'user_context': {
                    'age': random.randint(18, 65),
                    'interests': random.sample(['sports', 'tech', 'fashion', 'travel', 'food'], 2)
                },
                'timestamp': current_time + i
            })
            
    def test_basic_functionality(self):
        """Test that the function runs without errors and returns the expected format."""
        budget = 100.0
        time_limit = 100.0
        
        result = optimize_rtb(self.bid_requests, budget, time_limit, self.model, self.bidding_strategy)
        
        # Check result is a list
        self.assertIsInstance(result, list)
        
        # Check each bid has the required format
        for bid in result:
            self.assertIsInstance(bid, tuple)
            self.assertEqual(len(bid), 5)
            timestamp, bid_price, predicted_value, user_id, ad_slot = bid
            self.assertIsInstance(timestamp, (int, float))
            self.assertIsInstance(bid_price, (int, float))
            self.assertIsInstance(predicted_value, (int, float))
            self.assertIsInstance(user_id, str)
            self.assertIsInstance(ad_slot, str)
            
    def test_budget_constraint(self):
        """Test that the total cost of bids does not exceed the budget."""
        budget = 50.0
        time_limit = 100.0
        
        result = optimize_rtb(self.bid_requests, budget, time_limit, self.model, self.bidding_strategy)
        
        total_cost = sum(bid[1] for bid in result)
        self.assertLessEqual(total_cost, budget * 1.001)  # Allow for small floating-point errors
        
    def test_time_constraint(self):
        """Test that the bids are distributed reasonably across time."""
        budget = 100.0
        time_limit = 50.0
        
        result = optimize_rtb(self.bid_requests, budget, time_limit, self.model, self.bidding_strategy)
        
        # Check that all bids are within the time limit
        earliest_timestamp = min(self.bid_requests, key=lambda x: x['timestamp'])['timestamp']
        for bid in result:
            self.assertLessEqual(bid[0] - earliest_timestamp, time_limit)
            
    def test_empty_input(self):
        """Test with empty bid requests."""
        budget = 100.0
        time_limit = 100.0
        
        result = optimize_rtb([], budget, time_limit, self.model, self.bidding_strategy)
        
        self.assertEqual(result, [])
        
    def test_zero_budget(self):
        """Test with zero budget."""
        budget = 0.0
        time_limit = 100.0
        
        result = optimize_rtb(self.bid_requests, budget, time_limit, self.model, self.bidding_strategy)
        
        # Expect no bids when budget is zero
        self.assertEqual(result, [])
        
    def test_efficiency_with_large_input(self):
        """Test efficiency with a large number of bid requests."""
        budget = 1000.0
        time_limit = 1000.0
        
        # Generate a large number of bid requests
        large_bid_requests = []
        current_time = time.time()
        for i in range(10000):
            large_bid_requests.append({
                'user_id': f'user_{i}',
                'ad_slot': f'slot_{i % 100}',
                'user_context': {
                    'age': random.randint(18, 65),
                    'interests': random.sample(['sports', 'tech', 'fashion', 'travel', 'food'], 2)
                },
                'timestamp': current_time + i * 0.1
            })
            
        start_time = time.time()
        result = optimize_rtb(large_bid_requests, budget, time_limit, self.model, self.bidding_strategy)
        end_time = time.time()
        
        # Check execution time is reasonable (less than 10 seconds)
        self.assertLess(end_time - start_time, 10.0)
        
        # Check budget constraint is maintained
        total_cost = sum(bid[1] for bid in result)
        self.assertLessEqual(total_cost, budget * 1.001)
        
    def test_model_integration(self):
        """Test that the model is used correctly."""
        budget = 100.0
        time_limit = 100.0
        
        mock_model = MagicMock(return_value=0.5)
        result = optimize_rtb(self.bid_requests[:10], budget, time_limit, mock_model, self.bidding_strategy)
        
        # Check that the model was called for each bid request
        self.assertEqual(mock_model.call_count, 10)
        
    def test_bidding_strategy_integration(self):
        """Test that the bidding strategy is used correctly."""
        budget = 100.0
        time_limit = 100.0
        
        mock_bidding_strategy = MagicMock(return_value=1.0)
        result = optimize_rtb(self.bid_requests[:10], budget, time_limit, self.model, mock_bidding_strategy)
        
        # Check that the bidding strategy was called for bids
        self.assertGreaterEqual(mock_bidding_strategy.call_count, 1)
        
    def test_value_maximization(self):
        """Test that the algorithm maximizes value within constraints."""
        budget = 50.0
        time_limit = 100.0
        
        # Create a deterministic model that returns higher values for certain users
        def deterministic_model(user_id, ad_slot, user_context):
            if int(user_id.split('_')[1]) % 5 == 0:
                return 0.9  # High value for these users
            return 0.1
        
        result = optimize_rtb(self.bid_requests, budget, time_limit, deterministic_model, self.bidding_strategy)
        
        # Check that high-value users are prioritized
        high_value_bids = [bid for bid in result if bid[2] > 0.5]
        low_value_bids = [bid for bid in result if bid[2] <= 0.5]
        
        # If we have both high and low value bids, there should be more high value ones
        if high_value_bids and low_value_bids:
            self.assertGreaterEqual(len(high_value_bids) / len(result), 0.5)
        
    def test_uniform_spending_over_time(self):
        """Test that spending is distributed over time (not all at beginning or end)."""
        budget = 50.0
        time_limit = 100.0
        
        result = optimize_rtb(self.bid_requests, budget, time_limit, self.model, self.bidding_strategy)
        
        if result:
            # Sort bids by timestamp
            sorted_bids = sorted(result, key=lambda x: x[0])
            
            # Calculate time range
            earliest = sorted_bids[0][0]
            latest = sorted_bids[-1][0]
            time_range = latest - earliest
            
            if time_range > 0 and len(sorted_bids) >= 10:
                # Divide time into 3 segments
                segment_size = time_range / 3
                
                # Count bids in each segment
                segments = [0, 0, 0]
                for bid in sorted_bids:
                    segment_index = min(int((bid[0] - earliest) / segment_size), 2)
                    segments[segment_index] += 1
                
                # Check each segment has at least some bids (not all concentrated in one)
                for segment_count in segments:
                    self.assertGreaterEqual(segment_count, 1)
        
    def test_adaptive_bidding(self):
        """Test that bidding adapts to remaining budget."""
        budget = 20.0  # Small budget to force adaptation
        time_limit = 100.0
        
        result = optimize_rtb(self.bid_requests, budget, time_limit, self.model, self.bidding_strategy)
        
        if len(result) >= 10:
            # Sort bids by timestamp
            sorted_bids = sorted(result, key=lambda x: x[0])
            
            # Check if average bid amounts decrease over time as budget gets spent
            early_bids = sorted_bids[:len(sorted_bids)//3]
            late_bids = sorted_bids[-len(sorted_bids)//3:]
            
            avg_early_bid = sum(bid[1] for bid in early_bids) / len(early_bids)
            avg_late_bid = sum(bid[1] for bid in late_bids) / len(late_bids)
            
            # We can't make a hard assertion since adaptive bidding could work in different ways,
            # but we can check if there's a noticeable difference
            self.assertNotEqual(round(avg_early_bid, 2), round(avg_late_bid, 2))

if __name__ == '__main__':
    unittest.main()