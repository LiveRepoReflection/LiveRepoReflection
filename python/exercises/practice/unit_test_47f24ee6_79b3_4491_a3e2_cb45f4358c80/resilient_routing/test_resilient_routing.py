import unittest
from resilient_routing.resilient_routing import NetworkRouting

class TestResilientRouting(unittest.TestCase):
    def setUp(self):
        self.network = NetworkRouting(4)
        self.network.add_edge(0, 1, 10)
        self.network.add_edge(1, 2, 5)
        self.network.add_edge(2, 3, 7)

    def test_initial_shortest_path(self):
        self.assertEqual(self.network.query(0, 3), 22)
        self.assertEqual(self.network.query(1, 3), 12)
        self.assertEqual(self.network.query(0, 2), 15)

    def test_after_edge_removal(self):
        self.network.remove_edge(1, 2)
        self.assertEqual(self.network.query(0, 3), -1)
        self.assertEqual(self.network.query(0, 1), 10)
        self.assertEqual(self.network.query(2, 3), 7)

    def test_after_edge_addition(self):
        self.network.remove_edge(1, 2)
        self.network.add_edge(1, 3, 2)
        self.assertEqual(self.network.query(0, 3), 12)
        self.assertEqual(self.network.query(1, 3), 2)
        self.assertEqual(self.network.query(0, 1), 10)

    def test_disconnected_graph(self):
        self.network = NetworkRouting(5)
        self.network.add_edge(0, 1, 3)
        self.network.add_edge(2, 3, 4)
        self.assertEqual(self.network.query(0, 4), -1)
        self.assertEqual(self.network.query(0, 1), 3)
        self.assertEqual(self.network.query(2, 3), 4)

    def test_multiple_updates(self):
        self.network.add_edge(0, 2, 8)
        self.assertEqual(self.network.query(0, 3), 15)
        self.network.remove_edge(1, 2)
        self.assertEqual(self.network.query(0, 3), 15)
        self.network.add_edge(1, 3, 1)
        self.assertEqual(self.network.query(0, 3), 11)

    def test_edge_cost_update(self):
        self.network.add_edge(1, 2, 2)  # Update cost from 5 to 2
        self.assertEqual(self.network.query(0, 3), 19)
        self.assertEqual(self.network.query(1, 3), 9)

    def test_nonexistent_edge_removal(self):
        self.network.remove_edge(0, 3)  # No such edge
        self.assertEqual(self.network.query(0, 3), 22)

    def test_large_network(self):
        self.network = NetworkRouting(100)
        for i in range(99):
            self.network.add_edge(i, i+1, 1)
        self.assertEqual(self.network.query(0, 99), 99)
        self.network.remove_edge(50, 51)
        self.assertEqual(self.network.query(0, 99), -1)
        self.assertEqual(self.network.query(0, 50), 50)
        self.assertEqual(self.network.query(51, 99), 48)

if __name__ == '__main__':
    unittest.main()