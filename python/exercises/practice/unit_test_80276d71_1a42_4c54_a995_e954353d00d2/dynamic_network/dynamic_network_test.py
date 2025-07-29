import unittest
from dynamic_network import shortest_distances

class TestDynamicNetwork(unittest.TestCase):
    def test_basic_triangle(self):
        # Graph: 0-1-2 triangle
        N = 3
        edges = [
            (0, 1, 10),
            (1, 2, 20),
            (0, 2, 30)
        ]
        alpha = 1
        sources = [0]
        queries = [
            # After updating node 0 by 5:
            # New loads: [5, 0, 0]
            # weight(0,1)=10+1*(5+0)=15, weight(0,2)=30+1*(5+0)=35, weight(1,2)=20+1*(0+0)=20.
            # Shortest path from 0->1 is 15.
            (1, {0: 5}),
            # Now cumulative loads: [5, 0, 0] then add {1:10} to get [5, 10, 0].
            # weight(0,1)=10+1*(5+10)=25, weight(0,2)=30+1*(5+0)=35, weight(1,2)=20+1*(10+0)=30.
            # Shortest path from 0->1 remains directly 25, and from 0->2 remains 35.
            (2, {1: 10})
        ]
        expected = [15, 35]
        result = shortest_distances(N, edges, alpha, sources, queries)
        self.assertEqual(result, expected)

    def test_multi_sources_and_disconnected(self):
        # Graph with two disconnected components
        N = 4
        edges = [
            (0, 1, 5),
            (2, 3, 5)
        ]
        alpha = 0  # dynamic component is zero, so weights equal base_cost
        sources = [0, 2]
        queries = [
            # Query for node 1, available from source 0 with cost 5.
            (1, {}),
            # Query for node 3, available from source 2 with cost 5.
            (3, {})
        ]
        expected = [5, 5]
        result = shortest_distances(N, edges, alpha, sources, queries)
        self.assertEqual(result, expected)

    def test_cumulative_updates_line_graph(self):
        # Line graph of 5 nodes: 0-1-2-3-4
        N = 5
        edges = [
            (0, 1, 10),
            (1, 2, 10),
            (2, 3, 10),
            (3, 4, 10)
        ]
        alpha = 2
        sources = [0]
        queries = [
            # Query1: update node 1 by 5. Loads become: [0,5,0,0,0]
            # Weights:
            # (0,1)=10+2*(0+5)=20, (1,2)=10+2*(5+0)=20, (2,3)=10, (3,4)=10.
            # Shortest path from 0 to 2: 0->1->2: 20+20=40.
            (2, {1: 5}),
            # Query2: update node 3 by 3 and node 2 by 2.
            # Cumulative loads become: [0,5,2,3,0]
            # Weights:
            # (0,1)=10+2*(0+5)=20, (1,2)=10+2*(5+2)=10+14=24,
            # (2,3)=10+2*(2+3)=10+10=20, (3,4)=10+2*(3+0)=16.
            # Shortest path from 0 to 4: 20+24+20+16 = 80.
            (4, {3: 3, 2: 2})
        ]
        expected = [40, 80]
        result = shortest_distances(N, edges, alpha, sources, queries)
        self.assertEqual(result, expected)

    def test_unreachable_node(self):
        # Graph: three nodes, edge only between 0 and 1.
        N = 3
        edges = [
            (0, 1, 10)
        ]
        alpha = 1
        sources = [0]
        queries = [
            # Query for node 2 which is disconnected.
            (2, {})
        ]
        expected = [-1]
        result = shortest_distances(N, edges, alpha, sources, queries)
        self.assertEqual(result, expected)

    def test_multiple_updates_same_query(self):
        # Graph: simple direct edge
        N = 2
        edges = [
            (0, 1, 50)
        ]
        alpha = 5
        sources = [0]
        # Although dictionary keys are unique, simulate multiple updates by summing the update values.
        # So update of node 0 with {0: 3} and then later with additional {0:2} effectively is {0:5}.
        queries = [
            (1, {0: 5})
        ]
        # Load updated: [5, 0]
        # Weight: (0,1)=50+5*(5+0)=50+25=75.
        expected = [75]
        result = shortest_distances(N, edges, alpha, sources, queries)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()