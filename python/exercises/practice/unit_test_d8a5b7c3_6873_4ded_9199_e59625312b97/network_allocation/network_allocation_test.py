import unittest
from network_allocation import max_network_flow

class TestNetworkAllocation(unittest.TestCase):
    def test_single_source_single_sink(self):
        n = 4
        m = 5
        capacity = [
            (0, 1, 3),
            (0, 2, 2),
            (1, 2, 5),
            (1, 3, 2),
            (2, 3, 3)
        ]
        sources = [(0, 5)]
        sinks = [(3, 5)]
        self.assertEqual(max_network_flow(n, m, capacity, sources, sinks), 5)

    def test_multiple_sources_single_sink(self):
        n = 5
        m = 7
        capacity = [
            (0, 2, 5),
            (1, 2, 3),
            (2, 3, 4),
            (3, 4, 6),
            (0, 3, 2),
            (1, 3, 2),
            (2, 4, 3)
        ]
        sources = [(0, 4), (1, 3)]
        sinks = [(4, 7)]
        self.assertEqual(max_network_flow(n, m, capacity, sources, sinks), 7)

    def test_disconnected_network(self):
        n = 3
        m = 1
        capacity = [(0, 1, 2)]
        sources = [(0, 3)]
        sinks = [(2, 3)]
        self.assertEqual(max_network_flow(n, m, capacity, sources, sinks), 0)

    def test_bottleneck_case(self):
        n = 4
        m = 4
        capacity = [
            (0, 1, 10),
            (1, 2, 1),
            (2, 3, 10),
            (0, 3, 10)
        ]
        sources = [(0, 20)]
        sinks = [(3, 20)]
        self.assertEqual(max_network_flow(n, m, capacity, sources, sinks), 11)

    def test_parallel_links(self):
        n = 3
        m = 4
        capacity = [
            (0, 1, 2),
            (0, 1, 3),
            (1, 2, 4),
            (0, 2, 1)
        ]
        sources = [(0, 6)]
        sinks = [(2, 6)]
        self.assertEqual(max_network_flow(n, m, capacity, sources, sinks), 5)

    def test_large_network(self):
        n = 50
        m = 100
        capacity = [(i, i+1, 100) for i in range(49)] + [(49, 0, 100)]
        sources = [(0, 1000)]
        sinks = [(25, 1000)]
        self.assertEqual(max_network_flow(n, m, capacity, sources, sinks), 100)

    def test_flow_conservation(self):
        n = 3
        m = 2
        capacity = [
            (0, 1, 5),
            (1, 2, 3)
        ]
        sources = [(0, 5)]
        sinks = [(2, 3)]
        self.assertEqual(max_network_flow(n, m, capacity, sources, sinks), 3)

    def test_self_loop(self):
        n = 2
        m = 2
        capacity = [
            (0, 0, 5),
            (0, 1, 3)
        ]
        sources = [(0, 3)]
        sinks = [(1, 3)]
        self.assertEqual(max_network_flow(n, m, capacity, sources, sinks), 3)

    def test_multiple_sinks(self):
        n = 4
        m = 5
        capacity = [
            (0, 1, 4),
            (0, 2, 3),
            (1, 3, 2),
            (2, 3, 2),
            (1, 2, 1)
        ]
        sources = [(0, 5)]
        sinks = [(3, 3), (2, 2)]
        self.assertEqual(max_network_flow(n, m, capacity, sources, sinks), 5)

    def test_zero_capacity(self):
        n = 3
        m = 2
        capacity = [
            (0, 1, 0),
            (1, 2, 5)
        ]
        sources = [(0, 5)]
        sinks = [(2, 5)]
        self.assertEqual(max_network_flow(n, m, capacity, sources, sinks), 0)

if __name__ == '__main__':
    unittest.main()