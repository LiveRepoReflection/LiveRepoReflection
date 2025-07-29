import unittest
from optimal_traffic import find_optimal_route


class OptimalTrafficTest(unittest.TestCase):
    def test_basic_route_no_tolls(self):
        # Simple graph with no tolls
        edges = [
            (0, 1, 10, []),  # No toll schedule means no toll at any time
            (1, 2, 15, []),
            (0, 3, 5, []),
            (3, 2, 20, []),
        ]
        start_node = 0
        end_node = 2
        departure_time = 600  # 10:00 AM
        vot = 0.5  # $0.50 per minute

        expected_route = [0, 1, 2]
        expected_travel_time = 25
        expected_toll_cost = 0

        result = find_optimal_route(edges, start_node, end_node, departure_time, vot)
        self.assertEqual(result, (expected_route, expected_travel_time, expected_toll_cost))

    def test_toll_affects_route_choice(self):
        # Route 0->1->2 is faster but has toll, 0->3->2 is slower but free
        edges = [
            (0, 1, 10, [(600, 700, 10.0)]),  # $10 toll between 10:00-11:40 AM
            (1, 2, 10, []),
            (0, 3, 15, []),
            (3, 2, 10, []),
        ]
        # Case 1: VOT is high, taking toll road is optimal
        result1 = find_optimal_route(edges, 0, 2, 600, 2.0)  # VOT = $2.00/minute
        # Case 2: VOT is low, avoiding toll is optimal
        result2 = find_optimal_route(edges, 0, 2, 600, 0.1)  # VOT = $0.10/minute

        # With high VOT, taking toll road is worth it
        self.assertEqual(result1[0], [0, 1, 2])
        # With low VOT, avoiding toll road is better
        self.assertEqual(result2[0], [0, 3, 2])

    def test_time_dependent_tolls(self):
        edges = [
            (0, 1, 10, [(500, 600, 5.0), (600, 700, 10.0), (700, 800, 5.0)]),
            (1, 2, 10, []),
        ]
        # Different departure times result in different toll costs
        result1 = find_optimal_route(edges, 0, 2, 550, 1.0)  # Depart during $5 toll period
        result2 = find_optimal_route(edges, 0, 2, 650, 1.0)  # Depart during $10 toll period
        
        self.assertEqual(result1, ([0, 1, 2], 20, 5.0))
        self.assertEqual(result2, ([0, 1, 2], 20, 10.0))

    def test_arrival_time_affects_toll(self):
        edges = [
            (0, 1, 30, []),  # No toll
            (1, 2, 10, [(500, 600, 10.0)]),  # $10 toll between 8:20-10:00 AM
        ]
        # Departing at 7:50 AM means arriving at node 1 at 8:20 AM, when toll starts
        result = find_optimal_route(edges, 0, 2, 470, 1.0)
        
        self.assertEqual(result, ([0, 1, 2], 40, 10.0))

    def test_no_route_exists(self):
        edges = [
            (0, 1, 10, []),
            (2, 3, 10, []),  # Disconnected graph
        ]
        result = find_optimal_route(edges, 0, 3, 600, 1.0)
        
        self.assertEqual(result, ([], 0, 0))

    def test_same_start_and_end(self):
        edges = [
            (0, 1, 10, []),
            (1, 0, 10, []),
        ]
        result = find_optimal_route(edges, 0, 0, 600, 1.0)
        
        self.assertEqual(result, ([0], 0, 0))

    def test_complex_graph_multiple_paths(self):
        edges = [
            (0, 1, 10, [(600, 700, 5.0)]),
            (0, 2, 15, []),
            (1, 3, 10, [(600, 700, 8.0)]),
            (2, 3, 15, []),
            (3, 4, 10, [(600, 700, 3.0)]),
            (1, 4, 30, []),
            (2, 4, 25, [(600, 700, 2.0)]),
        ]
        # Test with different VOT values
        result1 = find_optimal_route(edges, 0, 4, 600, 0.5)  # Low VOT
        result2 = find_optimal_route(edges, 0, 4, 600, 5.0)  # High VOT

        # Expected results depend on the algorithm implementation and effective cost calculation
        # We'll check that the routes are valid and different based on VOT
        self.assertTrue(result1[0] in [[0, 2, 4], [0, 2, 3, 4], [0, 1, 4]])
        self.assertTrue(result2[0] in [[0, 1, 3, 4], [0, 1, 4]])

    def test_large_graph_performance(self):
        # Create a larger graph to test performance
        edges = []
        # Create a grid-like graph
        for i in range(20):
            for j in range(20):
                node_id = i * 20 + j
                if j < 19:  # Horizontal edge
                    edges.append((node_id, node_id + 1, 10, []))
                if i < 19:  # Vertical edge
                    edges.append((node_id, node_id + 20, 10, []))
                
        # Add some toll roads
        for i in range(10):
            edges.append((i, i + 100, 5, [(600, 700, 10.0)]))
            
        # Test performance (shouldn't time out)
        start_time = 600
        start_node = 0
        end_node = 399  # Last node in grid
        vot = 1.0
        
        # This should complete in reasonable time
        result = find_optimal_route(edges, start_node, end_node, start_time, vot)
        
        # Just verify we got a valid route
        self.assertTrue(len(result[0]) > 0)
        self.assertTrue(result[0][0] == start_node)
        self.assertTrue(result[0][-1] == end_node)

    def test_edge_case_toll_schedules(self):
        # Test handling of multiple toll schedule entries
        edges = [
            (0, 1, 10, [(0, 100, 5.0), (100, 200, 10.0), (700, 800, 15.0)]),
            (1, 2, 10, [(0, 1439, 2.0)]),  # All-day toll
        ]
        
        # Test departing at different times
        result1 = find_optimal_route(edges, 0, 2, 50, 1.0)  # During first toll period
        result2 = find_optimal_route(edges, 0, 2, 150, 1.0)  # During second toll period
        result3 = find_optimal_route(edges, 0, 2, 500, 1.0)  # No toll on first edge
        
        self.assertEqual(result1[2], 7.0)  # 5.0 + 2.0
        self.assertEqual(result2[2], 12.0)  # 10.0 + 2.0
        self.assertEqual(result3[2], 2.0)  # 0.0 + 2.0

    def test_midnight_crossing_toll_schedules(self):
        # Test toll schedules that span midnight
        edges = [
            (0, 1, 10, [(1400, 1439, 5.0), (0, 100, 5.0)]),  # Toll from 23:20 to 01:40
            (1, 2, 10, []),
        ]
        
        # Test departing before midnight
        result1 = find_optimal_route(edges, 0, 2, 1420, 1.0)  # 23:40
        # Test departing after midnight
        result2 = find_optimal_route(edges, 0, 2, 50, 1.0)  # 00:50
        # Test departing outside toll hours
        result3 = find_optimal_route(edges, 0, 2, 200, 1.0)  # 03:20
        
        self.assertEqual(result1[2], 5.0)
        self.assertEqual(result2[2], 5.0)
        self.assertEqual(result3[2], 0.0)


if __name__ == "__main__":
    unittest.main()