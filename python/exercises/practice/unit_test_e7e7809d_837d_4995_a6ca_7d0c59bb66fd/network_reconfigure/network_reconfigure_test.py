import unittest
from network_reconfigure import minimize_max_latency

class TestNetworkReconfigure(unittest.TestCase):
    def test_single_node(self):
        # A single server with no edges. Network is trivially connected.
        num_servers = 1
        edges = []
        critical_edges = []
        # No edge is required, so maximum latency is 0.
        self.assertEqual(minimize_max_latency(num_servers, edges, critical_edges), 0)

    def test_sample_case(self):
        # Sample case: two critical edges forced with original latencies.
        num_servers = 3
        edges = [(0, 1, 5), (1, 2, 3), (0, 2, 10)]
        critical_edges = [(0, 1), (1, 2)]
        # For critical edge (0,1), the minimum possible latency is 5 (from original)
        # For critical edge (1,2), minimum possible latency is 3.
        # An optimal reconfiguration would set (0,1)=5, (1,2)=3 and add (0,2)=0.
        # The maximum latency among edges is max(5,3,0) = 5.
        self.assertEqual(minimize_max_latency(num_servers, edges, critical_edges), 5)

    def test_chain_critical(self):
        # A chain network where all edges are critical.
        num_servers = 4
        edges = [(0, 1, 2), (1, 2, 4), (2, 3, 1), (0, 3, 10)]
        critical_edges = [(0, 1), (1, 2), (2, 3)]
        # Minimum latencies for the critical edges are: 2, 4, and 1 respectively.
        # Connectivity can be achieved by adding non-critical edges with 0 latency.
        # So the optimum maximum latency is max(2,4,1,0) = 4.
        self.assertEqual(minimize_max_latency(num_servers, edges, critical_edges), 4)

    def test_no_critical(self):
        # No critical edges: network can be reconfigured by adding arbitrary edges.
        num_servers = 5
        edges = [(0, 1, 8), (1, 2, 6), (2, 3, 7), (3, 4, 5)]
        critical_edges = []
        # With no critical constraints, one can add new edges to connect all vertices with 0 latency.
        self.assertEqual(minimize_max_latency(num_servers, edges, critical_edges), 0)

    def test_multiple_edges_between_pair(self):
        # Multiple edges between the same pair exist.
        num_servers = 3
        edges = [(0, 1, 7), (0, 1, 3), (1, 2, 5)]
        critical_edges = [(0, 1)]
        # For critical edge (0,1), the minimum original latency is 3.
        self.assertEqual(minimize_max_latency(num_servers, edges, critical_edges), 3)

    def test_self_loop_critical(self):
        # Include a critical self-loop edge.
        num_servers = 3
        # Self loop on server 1 and other edges connecting nodes to ensure connectivity.
        edges = [(1, 1, 8), (0, 1, 4), (1, 2, 2)]
        critical_edges = [(1, 1)]
        # For critical self-loop on 1, the minimum latency is 8.
        # To connect the graph, additional non-critical edges can be added with 0 latency.
        self.assertEqual(minimize_max_latency(num_servers, edges, critical_edges), 8)

if __name__ == '__main__':
    unittest.main()