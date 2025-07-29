import unittest
from network_scan import network_scan

class NetworkScanTest(unittest.TestCase):

    def test_no_paths(self):
        # Single node with no connections.
        n = 1
        connections = []
        critical_nodes = {0}
        entry_points = {0}
        # With no path from a node to itself (ignoring trivial path), expect no vulnerability.
        result = network_scan(n, connections, critical_nodes, entry_points)
        self.assertEqual(result, set())

    def test_single_path_no_vulnerability(self):
        # Based on the provided example.
        n = 5
        connections = [
            (0, 1, 5),
            (0, 2, 3),
            (1, 3, 2),
            (2, 3, 4),
            (3, 4, 1),
            (0, 4, 8)
        ]
        critical_nodes = {3, 4}
        entry_points = {0}
        result = network_scan(n, connections, critical_nodes, entry_points)
        # Node 3 has two paths with minimum bandwidths 2 and 3; not vulnerable (2 < 2 is false).
        # Node 4 has three paths; one of them has min bandwidth 1 which is less than 3.
        self.assertEqual(result, {4})

    def test_multiple_entry_points(self):
        # Multiple entry points affecting vulnerability.
        n = 6
        connections = [
            (0, 2, 3),
            (1, 2, 2),
            (2, 3, 1),
            (1, 4, 2),
            (4, 5, 2),
            (2, 5, 2)
        ]
        # Add an alternative low-bandwidth path from node 1 to node 5.
        connections.append((1, 5, 1))
        critical_nodes = {3, 5}
        entry_points = {0, 1}
        # For node 5, from entry 1 there are three paths: (1->5) with bandwidth 1,
        # (1->4->5) with min bandwidth 2, and (1->2->5) with min bandwidth 2. 
        # Since 1 < 3, node 5 should be marked vulnerable.
        result = network_scan(n, connections, critical_nodes, entry_points)
        self.assertEqual(result, {5})

    def test_cycle_graph(self):
        # Graph with cycles to test algorithm's handling of repeated paths.
        n = 3
        connections = [
            (0, 1, 4),
            (1, 2, 2),
            (2, 0, 3),
            (1, 0, 1)
        ]
        critical_nodes = {2}
        entry_points = {0}
        # Considering only simple paths to avoid infinite counts,
        # the only simple path from 0 to 2 is 0->1->2 with min bandwidth 2 and path count 1.
        # Therefore, node 2 should not be flagged as vulnerable.
        result = network_scan(n, connections, critical_nodes, entry_points)
        self.assertEqual(result, set())

    def test_disconnected_graph(self):
        # Two disconnected components: one with a cycle and one simple path.
        n = 4
        connections = [
            (0, 1, 3),
            (1, 0, 3),
            (2, 3, 1)
        ]
        critical_nodes = {1, 3}
        entry_points = {0, 2}
        # In component {0,1}: only one path from 0 to 1.
        # In component {2,3}: only one path from 2 to 3.
        # Neither meets the vulnerability condition.
        result = network_scan(n, connections, critical_nodes, entry_points)
        self.assertEqual(result, set())

    def test_entry_point_is_critical(self):
        # When an entry point is also a critical node.
        n = 3
        connections = [
            (0, 1, 4),
            (1, 2, 2),
            (2, 0, 1)
        ]
        critical_nodes = {0}
        entry_points = {0}
        # The trivial path (node 0 to itself) is not considered,
        # and the non-trivial cycle 0->1->2->0 provides one simple path with min bandwidth 1.
        # Since the count of simple distinct paths is 1, vulnerability condition is not met.
        result = network_scan(n, connections, critical_nodes, entry_points)
        self.assertEqual(result, set())

    def test_large_network(self):
        # Create a moderately large linear chain network.
        n = 10
        connections = []
        for i in range(n - 1):
            # Bandwidth decreases as we move along the chain.
            connections.append((i, i + 1, 10 - i))
        critical_nodes = {9}
        entry_points = {0}
        # There is only one simple path from 0 to 9 with a minimum bandwidth of 1.
        # Since 1 is not less than the count of paths (1), node 9 is not vulnerable.
        result = network_scan(n, connections, critical_nodes, entry_points)
        self.assertEqual(result, set())

if __name__ == '__main__':
    unittest.main()