import unittest
from flow_expansion import minimum_cost_expansion

class FlowExpansionTest(unittest.TestCase):
    def test_no_expansion_needed(self):
        # Graph: 2 nodes, one edge with ample initial capacity.
        n = 2
        edges = [
            (0, 1, 5)
        ]
        # Single commodity: demand 3 from node 0 to 1.
        commodities = [
            (0, 1, 3)
        ]
        # Expansion cost function: returns a fixed cost 2 per unit (should not be used).
        def cost(u, v):
            return 2
        # Since initial capacity is enough, expected cost is 0.
        expected = 0
        result = minimum_cost_expansion(n, edges, commodities, cost)
        self.assertEqual(result, expected)

    def test_with_expansion(self):
        # Graph: 2 nodes, one edge with insufficient initial capacity.
        n = 2
        edges = [
            (0, 1, 2)
        ]
        # Single commodity: demand 3 from node 0 to 1.
        commodities = [
            (0, 1, 3)
        ]
        # Expansion cost function: cost 4 per unit expansion.
        def cost(u, v):
            return 4
        # Need to expand by 1 unit on edge (0,1). Expected cost is 4.
        expected = 4
        result = minimum_cost_expansion(n, edges, commodities, cost)
        self.assertEqual(result, expected)

    def test_impossible_flow(self):
        # Graph: Disconnected graph.
        n = 3
        edges = [
            (0, 1, 10)
        ]
        # Commodity from node 0 to node 2, which is unreachable.
        commodities = [
            (0, 2, 5)
        ]
        # Even with expansion, there is no path from 0 to 2.
        def cost(u, v):
            return 1
        expected = -1
        result = minimum_cost_expansion(n, edges, commodities, cost)
        self.assertEqual(result, expected)

    def test_multi_commodity_conflict(self):
        # Graph: 4 nodes with two distinct paths from 0 to 3.
        n = 4
        edges = [
            (0, 1, 1),  # Path A: from 0 to 1
            (1, 3, 1),  # Path A: from 1 to 3
            (0, 2, 2),  # Path B: from 0 to 2
            (2, 3, 2)   # Path B: from 2 to 3
        ]
        # Two commodities with same source and destination.
        # Total demanded flow = 3 + 2 = 5.
        commodities = [
            (0, 3, 3),
            (0, 3, 2)
        ]
        # Define individual expansion costs:
        def cost(u, v):
            if (u, v) == (0, 1):
                return 2
            if (u, v) == (1, 3):
                return 3
            if (u, v) == (0, 2):
                return 1
            if (u, v) == (2, 3):
                return 4
            return 0

        # Explanation:
        # Without expansion, Path A can carry 1 and Path B can carry 2, totalling 3.
        # To deliver 5 units, we need an extra 2 units.
        #
        # One optimal strategy could be:
        #   Expand Path A by 2 units: on both edges (0,1) and (1,3),
        #   costing (2*2 + 2*3) = 4 + 6 = 10, while using Path B as-is.
        # Alternatively, distribute the expansion between paths.
        # In either case, the minimum total cost comes out to 10.
        expected = 10
        result = minimum_cost_expansion(n, edges, commodities, cost)
        self.assertEqual(result, expected)

    def test_zero_cost_expansion(self):
        # Graph: 3 nodes with zero initial capacity edges.
        n = 3
        edges = [
            (0, 1, 0),
            (1, 2, 0)
        ]
        # Single commodity: demand 10 from node 0 to 2.
        commodities = [
            (0, 2, 10)
        ]
        # Expansion cost function: zero cost for any expansion.
        def cost(u, v):
            return 0
        # Even though expansion is required, the cost is 0.
        expected = 0
        result = minimum_cost_expansion(n, edges, commodities, cost)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()