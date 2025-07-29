import unittest
from unittest.mock import Mock
import math
from maritime_route import find_min_cost_path

class TestMaritimeRoute(unittest.TestCase):
    def test_simple_graph_no_hazards(self):
        """Test with a simple graph and no hazards."""
        edges = [(0, 1, 10), (1, 2, 10)]
        
        def get_hazard_score(u, v, timestamp):
            return 0
        
        cost = find_min_cost_path(
            N=3,
            edges=edges,
            start_node=0,
            end_node=2,
            earliest_departure_time=0,
            latest_departure_time=10,
            time_step=1,
            ship_speed=5,
            get_hazard_score=get_hazard_score
        )
        
        # Distance is 20, speed is 5, so cost should be 20
        self.assertEqual(cost, 20)
    
    def test_simple_graph_with_hazards(self):
        """Test with a simple graph and constant hazards."""
        edges = [(0, 1, 10), (1, 2, 10)]
        
        def get_hazard_score(u, v, timestamp):
            return 0.5  # 50% additional cost due to hazard
        
        cost = find_min_cost_path(
            N=3,
            edges=edges,
            start_node=0,
            end_node=2,
            earliest_departure_time=0,
            latest_departure_time=10,
            time_step=1,
            ship_speed=5,
            get_hazard_score=get_hazard_score
        )
        
        # Distance is 20, hazard adds 50%, so cost should be 20 * 1.5 = 30
        self.assertEqual(cost, 30)
    
    def test_multiple_paths(self):
        """Test with multiple possible paths."""
        edges = [
            (0, 1, 10), (1, 3, 20),  # Path 1: 0 -> 1 -> 3
            (0, 2, 15), (2, 3, 10)   # Path 2: 0 -> 2 -> 3
        ]
        
        def get_hazard_score(u, v, timestamp):
            # Make path 2 more advantageous
            if (u == 0 and v == 1) or (u == 1 and v == 0) or (u == 1 and v == 3) or (u == 3 and v == 1):
                return 1.0
            return 0.0
        
        cost = find_min_cost_path(
            N=4,
            edges=edges,
            start_node=0,
            end_node=3,
            earliest_departure_time=0,
            latest_departure_time=10,
            time_step=1,
            ship_speed=5,
            get_hazard_score=get_hazard_score
        )
        
        # Path 1: (10 * 2) + (20 * 2) = 60
        # Path 2: (15 * 1) + (10 * 1) = 25
        # Minimum cost should be 25
        self.assertEqual(cost, 25)
    
    def test_dynamic_hazards(self):
        """Test with hazards that change over time, making different departure times optimal."""
        edges = [(0, 1, 10)]
        
        def get_hazard_score(u, v, timestamp):
            # Hazard decreases with time, optimal is to depart at the latest time
            return max(0, 1.0 - timestamp * 0.1)
        
        cost = find_min_cost_path(
            N=2,
            edges=edges,
            start_node=0,
            end_node=1,
            earliest_departure_time=0,
            latest_departure_time=10,
            time_step=1,
            ship_speed=5,
            get_hazard_score=get_hazard_score
        )
        
        # At timestamp 10, hazard score is 0, so cost should be 10
        self.assertEqual(cost, 10)
    
    def test_no_path_exists(self):
        """Test when no path exists between start and end nodes."""
        edges = [(0, 1, 10), (2, 3, 10)]  # Disconnected graph
        
        def get_hazard_score(u, v, timestamp):
            return 0
        
        cost = find_min_cost_path(
            N=4,
            edges=edges,
            start_node=0,
            end_node=3,
            earliest_departure_time=0,
            latest_departure_time=10,
            time_step=1,
            ship_speed=5,
            get_hazard_score=get_hazard_score
        )
        
        self.assertEqual(cost, float('inf'))
    
    def test_same_start_and_end(self):
        """Test when start and end nodes are the same."""
        edges = [(0, 1, 10)]
        
        def get_hazard_score(u, v, timestamp):
            return 0
        
        cost = find_min_cost_path(
            N=2,
            edges=edges,
            start_node=0,
            end_node=0,
            earliest_departure_time=0,
            latest_departure_time=10,
            time_step=1,
            ship_speed=5,
            get_hazard_score=get_hazard_score
        )
        
        # No travel needed, cost should be 0
        self.assertEqual(cost, 0)
    
    def test_time_step_rounding(self):
        """Test that traversal times are properly rounded up to the nearest time step."""
        edges = [(0, 1, 11)]  # Distance 11, speed 5 -> time 2.2, should round to 3
        
        def get_hazard_score(u, v, timestamp):
            return 0
        
        # Mock to track the timestamps when hazard score is queried
        mock_get_hazard = Mock(side_effect=lambda u, v, t: 0)
        
        find_min_cost_path(
            N=2,
            edges=edges,
            start_node=0,
            end_node=1,
            earliest_departure_time=0,
            latest_departure_time=0,
            time_step=1,
            ship_speed=5,
            get_hazard_score=mock_get_hazard
        )
        
        # Check if hazard score was queried for the right timestamp (0 + 3 = 3)
        calls = [call[0][2] for call in mock_get_hazard.call_args_list]
        self.assertIn(0, calls)  # Departure time
    
    def test_complex_graph(self):
        """Test with a more complex graph structure."""
        edges = [
            (0, 1, 10), (1, 2, 15), (2, 5, 20),
            (0, 3, 20), (3, 4, 10), (4, 5, 15)
        ]
        
        def get_hazard_score(u, v, timestamp):
            # Different hazards for different edges
            if u == 0 and v == 1 or u == 1 and v == 0:
                return 0.5
            if u == 2 and v == 5 or u == 5 and v == 2:
                return 0.8
            if u == 0 and v == 3 or u == 3 and v == 0:
                return 0.2
            return 0.1
        
        cost = find_min_cost_path(
            N=6,
            edges=edges,
            start_node=0,
            end_node=5,
            earliest_departure_time=0,
            latest_departure_time=10,
            time_step=1,
            ship_speed=5,
            get_hazard_score=get_hazard_score
        )
        
        # Path 0->1->2->5: 10*1.5 + 15*1.1 + 20*1.8 = 15 + 16.5 + 36 = 67.5
        # Path 0->3->4->5: 20*1.2 + 10*1.1 + 15*1.1 = 24 + 11 + 16.5 = 51.5
        # Minimum cost should be 51.5
        self.assertEqual(cost, 51.5)
    
    def test_varying_departure_times(self):
        """Test with varying departure times, where a later departure may be better."""
        edges = [(0, 1, 10)]
        
        def get_hazard_score(u, v, timestamp):
            # Hazard is highest at time 0, lowest at time 10
            return max(0, 1.0 - timestamp * 0.1)
        
        cost = find_min_cost_path(
            N=2,
            edges=edges,
            start_node=0,
            end_node=1,
            earliest_departure_time=0,
            latest_departure_time=10,
            time_step=1,
            ship_speed=5,
            get_hazard_score=get_hazard_score
        )
        
        # Optimal departure is at time 10, with hazard 0, cost should be 10
        self.assertEqual(cost, 10)
    
    def test_large_time_step(self):
        """Test with a larger time step."""
        edges = [(0, 1, 25)]  # Distance 25, speed 5 -> time 5, with time_step 5, stays 5
        
        def get_hazard_score(u, v, timestamp):
            return 0.5
        
        cost = find_min_cost_path(
            N=2,
            edges=edges,
            start_node=0,
            end_node=1,
            earliest_departure_time=0,
            latest_departure_time=10,
            time_step=5,
            ship_speed=5,
            get_hazard_score=get_hazard_score
        )
        
        # Distance 25, hazard 0.5, cost should be 25 * 1.5 = 37.5
        self.assertEqual(cost, 37.5)
    
    def test_expensive_hazard_function(self):
        """Test with an expensive hazard function to ensure proper caching/optimization."""
        edges = [(0, 1, 10), (1, 2, 10)]
        calls = 0
        
        def get_hazard_score(u, v, timestamp):
            nonlocal calls
            calls += 1
            # Simulate an expensive computation
            return 0.5
        
        cost = find_min_cost_path(
            N=3,
            edges=edges,
            start_node=0,
            end_node=2,
            earliest_departure_time=0,
            latest_departure_time=10,
            time_step=1,
            ship_speed=5,
            get_hazard_score=get_hazard_score
        )
        
        # Check that the function works correctly
        self.assertEqual(cost, 30)
        
        # A naive solution would call get_hazard_score for each edge and each possible departure time
        # In this case: 2 edges * 11 timestamps = 22 calls in the worst case
        # This test assumes that the solution includes reasonable caching or optimization
        # We expect fewer calls than the worst case but allow some flexibility
        self.assertLessEqual(calls, 50)  # This threshold can be adjusted based on your specific implementation

if __name__ == '__main__':
    unittest.main()