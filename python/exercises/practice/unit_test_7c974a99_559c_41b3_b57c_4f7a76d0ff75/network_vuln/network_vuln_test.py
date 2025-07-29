import unittest
from network_vuln.network_vuln import assess_vulnerability

class TestNetworkVuln(unittest.TestCase):
    def test_no_path(self):
        N = 3
        edges = [(1, 2, 10)]
        entrypoint = 1
        target = 3
        server_processing_power = [5, 10, 15]
        self.assertEqual(assess_vulnerability(N, edges, entrypoint, target, server_processing_power), 0)
        
    def test_direct_path(self):
        # Graph: 1 -> 2 -> 3, simple linear connection.
        N = 3
        edges = [(1, 2, 100), (2, 3, 50)]
        entrypoint = 1
        target = 3
        # For path 1->2->3:
        # Reachability = min(100, 50) = 50
        # Exploitability = min(10, 5, 8) = 5
        # Vulnerability = 50 * 5 = 250
        server_processing_power = [10, 5, 8]
        self.assertEqual(assess_vulnerability(N, edges, entrypoint, target, server_processing_power), 250)
        
    def test_multiple_paths(self):
        # Graph: Two paths from 1 to 3: through 2 and direct.
        N = 3
        edges = [(1, 2, 100), (2, 3, 50), (1, 3, 30)]
        entrypoint = 1
        target = 3
        # Path 1->2->3 gives vulnerability = min(100, 50) * min(10, 5, 8) = 50 * 5 = 250.
        # Direct path 1->3 gives vulnerability = 30 * min(10,8) = 30 * 8 = 240.
        server_processing_power = [10, 5, 8]
        self.assertEqual(assess_vulnerability(N, edges, entrypoint, target, server_processing_power), 250)
        
    def test_cycle(self):
        # Graph: Contains a cycle between nodes 2 and 3.
        N = 3
        edges = [(1, 2, 100), (2, 3, 80), (3, 2, 90), (1, 3, 50)]
        entrypoint = 1
        target = 3
        # Consider simple paths (assuming no repeated nodes):
        # Path 1->2->3: vulnerability = min(100, 80) * min(15,7,20) = 80 * 7 = 560.
        # Direct path 1->3: vulnerability = 50 * min(15,20) = 50 * 15 = 750.
        # Maximum vulnerability is 750.
        server_processing_power = [15, 7, 20]
        self.assertEqual(assess_vulnerability(N, edges, entrypoint, target, server_processing_power), 750)
        
    def test_entry_equals_target(self):
        # When entrypoint equals target:
        # Vulnerability is defined as the (max outgoing bandwidth from that node) * (processing power of that node).
        N = 3
        # Let node 2 be entry and target.
        # Outgoing edges from node 2: 2->1 with bandwidth 40, 2->3 with bandwidth 100.
        edges = [(2, 1, 40), (2, 3, 100)]
        entrypoint = 2
        target = 2
        # The vulnerability score = max(40, 100) * processing_power[1] where node 2 processing power = 12.
        expected = 100 * 12  # 1200
        server_processing_power = [8, 12, 10]
        self.assertEqual(assess_vulnerability(N, edges, entrypoint, target, server_processing_power), expected)
        
    def test_multiple_edges_same_pair(self):
        # Graph with multiple edges between same nodes.
        N = 4
        # Edges: Two edges from 1->2, different bandwidths.
        edges = [
            (1, 2, 70),
            (1, 2, 90),  # Better edge
            (2, 3, 60),
            (3, 4, 80),
            (1, 4, 50)
        ]
        entrypoint = 1
        target = 4
        # Consider path 1->2->3->4: vulnerability = min(max(70, 90), 60, 80) * min(processing_power of nodes)
        # For node values, choose processing powers = [20, 15, 10, 25]:
        # For path 1->2->3->4:
        # The best edge from 1->2 is 90, so bandwidth = min(90, 60, 80) = 60.
        # Exploitability = min(20, 15, 10, 25) = 10.
        # Product = 60 * 10 = 600.
        # Direct path 1->4: vulnerability = 50 * min(20,25) = 50*20 = 1000.
        # Thus maximum vulnerability should be 1000.
        server_processing_power = [20, 15, 10, 25]
        self.assertEqual(assess_vulnerability(N, edges, entrypoint, target, server_processing_power), 1000)

if __name__ == '__main__':
    unittest.main()