import unittest
from traffic_optim import min_travel_time

class TrafficOptimTest(unittest.TestCase):
    
    def test_basic_no_events(self):
        N = 4
        edges = [(0, 1, 10), (0, 2, 5), (1, 2, 2), (1, 3, 1), (2, 1, 3), (2, 3, 9)]
        queries = [
            (0, 3, 10, [], []),
        ]
        self.assertEqual(min_travel_time(N, edges, queries), [9])
    
    def test_with_congestion(self):
        N = 4
        edges = [(0, 1, 10), (0, 2, 5), (1, 2, 2), (1, 3, 1), (2, 1, 3), (2, 3, 9)]
        queries = [
            (0, 3, 15, [(0, 1, 12, 18, 2)], []),
        ]
        self.assertEqual(min_travel_time(N, edges, queries), [9])
    
    def test_with_blockage(self):
        N = 4
        edges = [(0, 1, 10), (0, 2, 5), (1, 2, 2), (1, 3, 1), (2, 1, 3), (2, 3, 9)]
        queries = [
            (0, 3, 20, [], [(1, 3, 18, 22)]),
        ]
        self.assertEqual(min_travel_time(N, edges, queries), [14])
    
    def test_full_example(self):
        N = 4
        edges = [(0, 1, 10), (0, 2, 5), (1, 2, 2), (1, 3, 1), (2, 1, 3), (2, 3, 9)]
        queries = [
            (0, 3, 10, [], []),
            (0, 3, 15, [(0, 1, 12, 18, 2)], []),
            (0, 3, 20, [], [(1, 3, 18, 22)]),
        ]
        self.assertEqual(min_travel_time(N, edges, queries), [9, 9, 14])
    
    def test_no_path(self):
        N = 4
        edges = [(0, 1, 10), (0, 2, 5), (1, 2, 2)]  # No path to node 3
        queries = [
            (0, 3, 10, [], []),
        ]
        self.assertEqual(min_travel_time(N, edges, queries), [-1])
    
    def test_disconnected_graph(self):
        N = 5
        edges = [(0, 1, 10), (1, 2, 2), (3, 4, 5)]  # Two separate components
        queries = [
            (0, 2, 10, [], []),  # Path exists
            (0, 4, 10, [], []),  # No path exists
        ]
        self.assertEqual(min_travel_time(N, edges, queries), [12, -1])
    
    def test_multiple_congestion(self):
        N = 4
        edges = [(0, 1, 10), (0, 2, 5), (1, 3, 1), (2, 3, 10)]
        queries = [
            (0, 3, 15, [(0, 1, 12, 18, 2), (2, 3, 10, 20, 3)], []),  # Multiple congestion events
        ]
        self.assertEqual(min_travel_time(N, edges, queries), [21])  # 0->1->3 = 20+1 = 21, 0->2->3 = 5+30 = 35
    
    def test_overlapping_congestion(self):
        N = 3
        edges = [(0, 1, 5), (1, 2, 5)]
        queries = [
            (0, 2, 15, [(0, 1, 10, 20, 2), (0, 1, 12, 18, 3)], []),  # Overlapping congestion
        ]
        # The worst congestion factor should apply: 5*3 + 5 = 20
        self.assertEqual(min_travel_time(N, edges, queries), [20])
    
    def test_congestion_and_blockage(self):
        N = 5
        edges = [(0, 1, 5), (0, 2, 10), (1, 3, 10), (2, 3, 5), (3, 4, 5)]
        queries = [
            (0, 4, 15, [(0, 1, 10, 20, 2)], [(2, 3, 10, 20)]),  # Congestion + Blockage
        ]
        # Route: 0->1->3->4 = 10+10+5 = 25, since 0->2->3->4 is blocked
        self.assertEqual(min_travel_time(N, edges, queries), [25])
    
    def test_all_paths_blocked(self):
        N = 3
        edges = [(0, 1, 5), (1, 2, 5)]
        queries = [
            (0, 2, 15, [], [(0, 1, 10, 20), (1, 2, 10, 20)]),  # All paths blocked
        ]
        self.assertEqual(min_travel_time(N, edges, queries), [-1])
    
    def test_large_graph(self):
        # Create a larger test case
        N = 50
        edges = []
        # Create a grid-like graph structure
        for i in range(7):
            for j in range(7):
                node = i * 7 + j
                if i < 6:  # Connect vertically
                    edges.append((node, (i + 1) * 7 + j, (i + j) % 10 + 1))
                if j < 6:  # Connect horizontally
                    edges.append((node, i * 7 + (j + 1), (i + j) % 10 + 1))
        
        queries = [
            (0, 48, 100, [], []),  # Simple path
            (0, 48, 100, [(0, 7, 90, 110, 2)], []),  # With congestion
            (0, 48, 100, [], [(0, 7, 90, 110)]),  # With blockage
        ]
        
        result = min_travel_time(N, edges, queries)
        # We don't assert the exact values, but ensure the function runs and returns 3 results
        self.assertEqual(len(result), 3)
        self.assertTrue(isinstance(result[0], int))
        self.assertTrue(isinstance(result[1], int))
        self.assertTrue(isinstance(result[2], int))
    
    def test_timestamp_outside_events(self):
        N = 4
        edges = [(0, 1, 10), (1, 3, 5)]
        queries = [
            # Events that don't affect the query because timestamp is outside the event time range
            (0, 3, 5, [(0, 1, 10, 20, 3)], [(1, 3, 30, 40)]),
        ]
        self.assertEqual(min_travel_time(N, edges, queries), [15])  # Normal path 0->1->3 = 10+5 = 15
    
    def test_congestion_after_timestamp(self):
        N = 4
        edges = [(0, 1, 10), (1, 3, 5)]
        # Congestion starts after the timestamp
        queries = [(0, 3, 5, [(0, 1, 6, 10, 2)], [])]
        self.assertEqual(min_travel_time(N, edges, queries), [15])  # Normal path since congestion is after timestamp

    def test_complex_routes(self):
        N = 6
        edges = [(0, 1, 5), (0, 2, 10), (1, 2, 2), (1, 3, 15), 
                 (2, 3, 10), (2, 4, 5), (3, 5, 5), (4, 5, 10)]
        queries = [
            (0, 5, 10, [(1, 3, 5, 15, 2)], [(2, 4, 5, 15)]),
        ]
        # Best route: 0->1->2->3->5 = 5+2+10+5 = 22
        # Route 0->1->3->5 = 5+30+5 = 40 (congested)
        # Route 0->2->4->5 is blocked
        self.assertEqual(min_travel_time(N, edges, queries), [22])

if __name__ == '__main__':
    unittest.main()