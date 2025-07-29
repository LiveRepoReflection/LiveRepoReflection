import unittest
from network_divider import min_links_removal

class NetworkDividerTestCase(unittest.TestCase):
    def test_single_node(self):
        # Single node, no edges so no removal required.
        N = 1
        D = 1
        edges = []
        self.assertEqual(min_links_removal(N, D, edges), 0)

    def test_fully_connected_no_removal(self):
        # Fully connected graph of 4 nodes (complete graph) with latency 1.
        # Diameter is 1, which is <= D.
        N = 4
        D = 2
        edges = [
            (0, 1, 1), (0, 2, 1), (0, 3, 1),
            (1, 2, 1), (1, 3, 1),
            (2, 3, 1)
        ]
        self.assertEqual(min_links_removal(N, D, edges), 0)

    def test_chain_graph(self):
        # Chain: 0-1-2-3 with edge latencies all 1.
        # For D = 1, the maximum allowed path length (diameter) is 1.
        # Best partition: remove edge (1,2) to get two components: {0,1} and {2,3}.
        N = 4
        D = 1
        edges = [
            (0, 1, 1),
            (1, 2, 1),
            (2, 3, 1)
        ]
        self.assertEqual(min_links_removal(N, D, edges), 1)

    def test_bridge_cut(self):
        # Two clusters connected by a bridge.
        # Cluster1: Nodes 0, 1, 2 fully connected. Cluster2: Nodes 3, 4, 5 fully connected.
        # Bridge: Edge (2,3) with latency 2. D = 2, so whole graph's diameter
        # would exceed D if clusters remain connected. Removal of this bridge
        # yields two clusters with diameters <= 1.
        N = 6
        D = 2
        edges = [
            # Cluster 1
            (0, 1, 1), (0, 2, 1), (1, 2, 1),
            # Cluster 2
            (3, 4, 1), (3, 5, 1), (4, 5, 1),
            # Bridge between clusters
            (2, 3, 2)
        ]
        self.assertEqual(min_links_removal(N, D, edges), 1)
        
    def test_chain_with_higher_latency(self):
        # Chain: 0-1-2-3-4 with edge latencies 2.
        # For D = 3, the entire chain would have a diameter of 8 if unbroken.
        # One possible optimal partition:
        # Remove edges (1,2) and (2,3) to obtain components:
        # Component1: nodes [0,1] with diameter 2.
        # Component2: node [2] with diameter 0.
        # Component3: nodes [3,4] with diameter 2.
        # Hence, expected removal count is 2.
        N = 5
        D = 3
        edges = [
            (0, 1, 2),
            (1, 2, 2),
            (2, 3, 2),
            (3, 4, 2)
        ]
        self.assertEqual(min_links_removal(N, D, edges), 2)

    def test_complex_graph(self):
        # A more complex graph that mixes cycles and chains.
        # Graph structure:
        # 0 - 1 - 2 - 3 is a chain (all edges latency 1)
        # There is an extra edge (0,2) with latency 2 forming a cycle.
        # D is set such that the uncut graph's diameter exceeds D.
        # Optimal partition might require removal of at least one edge.
        N = 4
        D = 2
        edges = [
            (0, 1, 1),
            (1, 2, 1),
            (2, 3, 1),
            (0, 2, 2)
        ]
        # One possibility: remove edge (1,2), then Component1: (0,1) with diameter=1,
        # and Component2: (2,3) with diameter=1.
        self.assertEqual(min_links_removal(N, D, edges), 1)

if __name__ == '__main__':
    unittest.main()