import unittest
from network_hubs.network_hubs import min_max_latency

class TestNetworkHubs(unittest.TestCase):
    def test_single_node(self):
        # Single node graph: only one intersection, which is also a hub.
        graph = {0: []}
        num_hubs = 1
        # The only node is the hub so the latency is 0.
        self.assertEqual(min_max_latency(graph, num_hubs), 0)

    def test_chain_single_hub(self):
        # Chain graph: 0 --10-- 1 --10-- 2.
        graph = {
            0: [(1, 10)],
            1: [(0, 10), (2, 10)],
            2: [(1, 10)]
        }
        num_hubs = 1
        # Best placement is at the middle node giving max distance 10.
        self.assertEqual(min_max_latency(graph, num_hubs), 10)

    def test_chain_two_hubs(self):
        # Chain graph: 0 --10-- 1 --10-- 2.
        graph = {
            0: [(1, 10)],
            1: [(0, 10), (2, 10)],
            2: [(1, 10)]
        }
        num_hubs = 2
        # Optimal placement may be at nodes 0 and 2; max latency becomes 10.
        self.assertEqual(min_max_latency(graph, num_hubs), 10)

    def test_disconnected_graph_single_hub(self):
        # Two disconnected components:
        # Component 1: 0 --5-- 1, Component 2: 2 --7-- 3.
        graph = {
            0: [(1, 5)],
            1: [(0, 5)],
            2: [(3, 7)],
            3: [(2, 7)]
        }
        num_hubs = 1
        # With only one hub, nodes in the unchosen component are unreachable.
        self.assertEqual(min_max_latency(graph, num_hubs), -1)

    def test_disconnected_graph_two_hubs(self):
        # Two disconnected components:
        # Component 1: 0 --5-- 1, Component 2: 2 --7-- 3.
        graph = {
            0: [(1, 5)],
            1: [(0, 5)],
            2: [(3, 7)],
            3: [(2, 7)]
        }
        num_hubs = 2
        # Optimal placement: one hub in each component yields max latency max(5, 7) = 7.
        self.assertEqual(min_max_latency(graph, num_hubs), 7)

    def test_example_complex_graph(self):
        # Provided complex example
        graph = {
            0: [(1, 10), (2, 15)],
            1: [(0, 10), (3, 20)],
            2: [(0, 15), (4, 25)],
            3: [(1, 20), (5, 30)],
            4: [(2, 25), (5, 35)],
            5: [(3, 30), (4, 35)]
        }
        num_hubs = 2
        # Expected optimal max latency is 30
        self.assertEqual(min_max_latency(graph, num_hubs), 30)

    def test_cycle_single_hub(self):
        # Cycle graph: 0-1-2-3-0 with equal latencies 10.
        graph = {
            0: [(1, 10), (3, 10)],
            1: [(0, 10), (2, 10)],
            2: [(1, 10), (3, 10)],
            3: [(2, 10), (0, 10)]
        }
        num_hubs = 1
        # With a single hub, the furthest node will be 2 hops away giving a latency of 20.
        self.assertEqual(min_max_latency(graph, num_hubs), 20)

    def test_cycle_two_hubs(self):
        # Cycle graph: 0-1-2-3-0 with equal latencies 10.
        graph = {
            0: [(1, 10), (3, 10)],
            1: [(0, 10), (2, 10)],
            2: [(1, 10), (3, 10)],
            3: [(2, 10), (0, 10)]
        }
        num_hubs = 2
        # With two hubs, optimal placement (e.g., nodes 0 and 2) gives a max distance of 10.
        self.assertEqual(min_max_latency(graph, num_hubs), 10)

if __name__ == '__main__':
    unittest.main()