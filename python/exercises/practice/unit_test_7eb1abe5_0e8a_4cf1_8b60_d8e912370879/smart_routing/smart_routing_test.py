import unittest
from math import floor
from smart_routing import optimal_travel_time

class SmartRoutingTest(unittest.TestCase):
    def test_same_source_destination(self):
        # When source and destination are the same, travel time is 0 regardless of edges or STCs.
        n = 3
        edges = [(0, 1, 10), (1, 2, 5)]
        k = 2
        s = 1
        d = 1
        self.assertEqual(optimal_travel_time(n, edges, k, s, d), 0)

    def test_no_path(self):
        # Disconnected graph: no path from source to destination.
        n = 4
        edges = [(0, 1, 5), (1, 2, 5)]
        k = 1
        s = 0
        d = 3
        self.assertEqual(optimal_travel_time(n, edges, k, s, d), -1)

    def test_no_stc(self):
        # k = 0; should compute the shortest path without any reductions.
        n = 4
        edges = [(0, 1, 5), (1, 2, 5), (2, 3, 5)]
        k = 0
        s = 0
        d = 3
        # Expected: 5 + 5 + 5 = 15
        self.assertEqual(optimal_travel_time(n, edges, k, s, d), 15)

    def test_single_stc_optimal_at_source(self):
        # Graph test where placing one STC can improve the result.
        n = 5
        edges = [
            (0, 1, 10),
            (0, 2, 5),
            (1, 2, 2),
            (1, 3, 15),
            (2, 3, 7),
            (2, 4, 1),
            (3, 4, 8)
        ]
        k = 1
        s = 0
        d = 4
        # Reasoning:
        # Without STC best route is 0->2->4 with 5 + 1 = 6.
        # If STC is placed at 0, then:
        #   Edge (0,1)=floor(10/2)=5, Edge (0,2)=floor(5/2)=2.
        #   Best path using edge 0->2 then 2->4: 2 + 1 = 3.
        # If STC is placed elsewhere, best route is higher.
        # So expected optimal travel time is 3.
        self.assertEqual(optimal_travel_time(n, edges, k, s, d), 3)

    def test_two_stcs(self):
        # Using two STCs, further improvements can be achieved.
        n = 5
        edges = [
            (0, 1, 10),
            (0, 2, 5),
            (1, 2, 2),
            (1, 3, 15),
            (2, 3, 7),
            (2, 4, 1),
            (3, 4, 8)
        ]
        k = 2
        s = 0
        d = 4
        # Best placement is at intersections 0 and 2.
        # Transformed weights:
        # At 0: (0,1)=floor(10/2)=5, (0,2)=floor(5/2)=2.
        # At 2: (2,3)=floor(7/2)=3, (2,4)=floor(1/2)=0.
        # Best path: 0->2->4 = 2 + 0 = 2.
        self.assertEqual(optimal_travel_time(n, edges, k, s, d), 2)

    def test_cycle_in_graph(self):
        # Graph includes a cycle. Ensure that the algorithm handles cycles correctly.
        n = 4
        edges = [
            (0, 1, 5),
            (1, 2, 5),
            (2, 1, 1),  # cycle between 1 and 2
            (2, 3, 5)
        ]
        k = 1
        s = 0
        d = 3
        # Without STC, best path: 0->1->2->3 = 5+5+5 = 15.
        # With one STC placed at any of the nodes (0, 1, or 2):
        #   At 0: (0,1)=floor(5/2)=2, then 2+5+5 = 12.
        #   At 1: (1,2)=floor(5/2)=2, then 5+2+5 = 12.
        #   At 2: (2,3)=floor(5/2)=2, then 5+5+2 = 12.
        # Expected best travel time is 12.
        self.assertEqual(optimal_travel_time(n, edges, k, s, d), 12)

    def test_multiple_edges_between_nodes(self):
        # Graph with multiple edges between the same nodes.
        n = 3
        edges = [
            (0, 1, 10),
            (0, 1, 3),
            (1, 2, 5)
        ]
        k = 1
        s = 0
        d = 2
        # Without STC: choose edge (0,1,3) then (1,2,5) = 8.
        # With STC:
        #   If placed at 0: (0,1,3) becomes floor(3/2)=1, total=1+5=6.
        #   If placed at 1: (1,2,5) becomes floor(5/2)=2, total=3+2=5.
        # Expected optimal travel time is 5.
        self.assertEqual(optimal_travel_time(n, edges, k, s, d), 5)

if __name__ == '__main__':
    unittest.main()