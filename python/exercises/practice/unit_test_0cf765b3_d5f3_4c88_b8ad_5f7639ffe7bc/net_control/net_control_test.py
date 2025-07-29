import unittest
from net_control import simulate_congestion_control

class NetControlTest(unittest.TestCase):
    def test_simple_network(self):
        """Test with a simple network of two nodes with one link."""
        n = 2
        network = {0: [(1, 10)], 1: []}
        initial_rate = 5.0
        max_rate = 10.0
        congestion_threshold = 0.9
        decrease_factor = 0.5
        increase_increment = 1.0
        num_rounds = 5
        
        result = simulate_congestion_control(
            n, network, initial_rate, max_rate, congestion_threshold, 
            decrease_factor, increase_increment, num_rounds
        )
        
        # The first node should increase its rate until it reaches max_rate or congestion occurs
        # The second node has no outgoing links, so its rate should remain at initial_rate
        self.assertEqual(len(result), n)
        self.assertLessEqual(result[0], max_rate)
        self.assertEqual(result[1], initial_rate)

    def test_congestion_triggering(self):
        """Test with a network that triggers congestion."""
        n = 3
        network = {0: [(1, 5)], 1: [(2, 5)], 2: []}
        initial_rate = 4.0
        max_rate = 10.0
        congestion_threshold = 0.9
        decrease_factor = 0.5
        increase_increment = 1.0
        num_rounds = 10
        
        result = simulate_congestion_control(
            n, network, initial_rate, max_rate, congestion_threshold, 
            decrease_factor, increase_increment, num_rounds
        )
        
        # Node 0 and 1 should experience congestion as the rate increases
        self.assertEqual(len(result), n)
        # Rates should not exceed max_rate
        for rate in result:
            self.assertLessEqual(rate, max_rate)
            self.assertGreaterEqual(rate, 0)

    def test_complex_network(self):
        """Test with a more complex network."""
        n = 5
        network = {
            0: [(1, 10), (2, 5)],
            1: [(3, 7)],
            2: [(4, 3)],
            3: [(4, 8)],
            4: []
        }
        initial_rate = 3.0
        max_rate = 15.0
        congestion_threshold = 0.8
        decrease_factor = 0.7
        increase_increment = 2.0
        num_rounds = 15
        
        result = simulate_congestion_control(
            n, network, initial_rate, max_rate, congestion_threshold, 
            decrease_factor, increase_increment, num_rounds
        )
        
        self.assertEqual(len(result), n)
        for rate in result:
            self.assertLessEqual(rate, max_rate)
            self.assertGreaterEqual(rate, 0)

    def test_no_outgoing_links(self):
        """Test behavior when a node has no outgoing links."""
        n = 3
        network = {0: [], 1: [(2, 10)], 2: []}
        initial_rate = 5.0
        max_rate = 10.0
        congestion_threshold = 0.9
        decrease_factor = 0.5
        increase_increment = 1.0
        num_rounds = 5
        
        result = simulate_congestion_control(
            n, network, initial_rate, max_rate, congestion_threshold, 
            decrease_factor, increase_increment, num_rounds
        )
        
        # Nodes with no outgoing links should maintain their initial rate
        self.assertEqual(result[0], initial_rate)
        self.assertLessEqual(result[1], max_rate)
        self.assertEqual(result[2], initial_rate)

    def test_congestion_with_multiple_senders(self):
        """Test congestion handling with multiple senders to the same link."""
        n = 4
        network = {
            0: [(2, 10)],
            1: [(2, 10)],
            2: [(3, 15)],
            3: []
        }
        initial_rate = 8.0
        max_rate = 20.0
        congestion_threshold = 0.9
        decrease_factor = 0.5
        increase_increment = 2.0
        num_rounds = 10
        
        result = simulate_congestion_control(
            n, network, initial_rate, max_rate, congestion_threshold, 
            decrease_factor, increase_increment, num_rounds
        )
        
        self.assertEqual(len(result), n)
        # Check if node 2's link to 3 is getting congested
        # The total rate from 0 and 1 to 2 should eventually exceed 2's capacity to 3
        # causing rate adjustments
        for rate in result:
            self.assertLessEqual(rate, max_rate)
            self.assertGreaterEqual(rate, 0)

    def test_rate_bounds(self):
        """Test that rates stay within bounds."""
        n = 2
        network = {0: [(1, 1000)], 1: []}
        initial_rate = 1.0
        max_rate = 1000.0
        congestion_threshold = 0.9
        decrease_factor = 0.5
        increase_increment = 10.0
        num_rounds = 100
        
        result = simulate_congestion_control(
            n, network, initial_rate, max_rate, congestion_threshold, 
            decrease_factor, increase_increment, num_rounds
        )
        
        # All rates should be between initial_rate and max_rate
        for rate in result:
            self.assertLessEqual(rate, max_rate)
            self.assertGreaterEqual(rate, initial_rate)

    def test_large_network(self):
        """Test with a larger network to check performance."""
        n = 100
        network = {}
        for i in range(n-1):
            network[i] = [(i+1, 50)]
        network[n-1] = []
        
        initial_rate = 5.0
        max_rate = 100.0
        congestion_threshold = 0.9
        decrease_factor = 0.5
        increase_increment = 1.0
        num_rounds = 30
        
        result = simulate_congestion_control(
            n, network, initial_rate, max_rate, congestion_threshold, 
            decrease_factor, increase_increment, num_rounds
        )
        
        self.assertEqual(len(result), n)
        for rate in result:
            self.assertLessEqual(rate, max_rate)
            self.assertGreaterEqual(rate, 0)

    def test_cyclic_network(self):
        """Test with a network containing cycles."""
        n = 4
        network = {
            0: [(1, 10)],
            1: [(2, 10)],
            2: [(3, 10), (0, 5)],
            3: [(1, 5)]
        }
        initial_rate = 3.0
        max_rate = 15.0
        congestion_threshold = 0.8
        decrease_factor = 0.6
        increase_increment = 1.5
        num_rounds = 20
        
        result = simulate_congestion_control(
            n, network, initial_rate, max_rate, congestion_threshold, 
            decrease_factor, increase_increment, num_rounds
        )
        
        self.assertEqual(len(result), n)
        for rate in result:
            self.assertLessEqual(rate, max_rate)
            self.assertGreaterEqual(rate, 0)

    def test_edge_case_parameters(self):
        """Test with edge case parameters."""
        n = 3
        network = {0: [(1, 5)], 1: [(2, 5)], 2: []}
        
        # Very small increment and high decrease factor
        result1 = simulate_congestion_control(
            n, network, 1.0, 10.0, 0.9, 0.99, 0.01, 10
        )
        
        # Very high increment and low decrease factor
        result2 = simulate_congestion_control(
            n, network, 1.0, 10.0, 0.9, 0.1, 10.0, 10
        )
        
        self.assertEqual(len(result1), n)
        self.assertEqual(len(result2), n)
        
        for rate in result1 + result2:
            self.assertLessEqual(rate, 10.0)
            self.assertGreaterEqual(rate, 0)

if __name__ == '__main__':
    unittest.main()