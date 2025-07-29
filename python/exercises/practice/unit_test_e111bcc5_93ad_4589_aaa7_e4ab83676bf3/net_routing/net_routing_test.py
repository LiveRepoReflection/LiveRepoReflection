import unittest
from net_routing import (
    initialize_network,
    add_edge,
    remove_edge,
    update_latency,
    send_packet,
    receive_packet,
    find_optimal_path
)

class TestNetRouting(unittest.TestCase):

    def setUp(self):
        # Before each test, we initialize the network.
        pass

    def test_no_edges(self):
        # Initialize network with 3 nodes, no edges.
        initialize_network(3)
        # There is no path from 0 to 1, so expect empty list.
        path = find_optimal_path(0, 1, latency_weight=1, congestion_weight=1)
        self.assertEqual(path, [])

    def test_single_edge_path(self):
        # Simple case: direct connection.
        initialize_network(2)
        add_edge(0, 1, 10)
        path = find_optimal_path(0, 1, latency_weight=1, congestion_weight=1)
        self.assertEqual(path, [0, 1])

    def test_bidirectional_edge_update(self):
        # Test that updating latency reflects in pathfinding.
        initialize_network(3)
        add_edge(0, 1, 10)
        add_edge(1, 2, 10)
        add_edge(0, 2, 30)
        # Without congestion, the path 0-1-2 is optimal.
        path = find_optimal_path(0, 2, latency_weight=1, congestion_weight=0)
        self.assertEqual(path, [0, 1, 2])
        
        # Update the latency for edge (0,2) to be lower.
        update_latency(0, 2, 5)
        # Now the direct path should be optimal.
        path = find_optimal_path(0, 2, latency_weight=1, congestion_weight=0)
        self.assertEqual(path, [0, 2])

    def test_congestion_effect(self):
        # Test that congestion plays a role along with latency.
        initialize_network(3)
        add_edge(0, 1, 10)
        add_edge(1, 2, 10)
        add_edge(0, 2, 30)
        # Initially, without any congestion, path 0-1-2 has total latency 20.
        path = find_optimal_path(0, 2, latency_weight=1, congestion_weight=5)
        self.assertEqual(path, [0, 1, 2])
        
        # Increase congestion on node 1 so that its cost increases.
        send_packet(1)  # congestion at node 1 becomes 1.
        # Now, compare:
        # Path 0-1-2: latency=20, congestion= (0 + 1 + 0)*5 = 5, total=25.
        # Direct path 0-2: latency=30, congestion= (0 + 0)*5 = 0, total=30.
        # So still [0,1,2] is optimal.
        path = find_optimal_path(0, 2, latency_weight=1, congestion_weight=5)
        self.assertEqual(path, [0, 1, 2])
        
        # Increase congestion further on node 1.
        send_packet(1)  # congestion becomes 2.
        # Now: 0-1-2: latency=20, congestion= (0+2+0)*5 = 10, total cost=30.
        # Direct: latency=30, congestion=0, total cost=30.
        # Either path is acceptable; check that it returns one of these two.
        path = find_optimal_path(0, 2, latency_weight=1, congestion_weight=5)
        self.assertTrue(path == [0, 1, 2] or path == [0, 2])
        
        # Reduce congestion on node 1.
        receive_packet(1)
        # Now congestion at node 1 becomes 1 again.
        path = find_optimal_path(0, 2, latency_weight=1, congestion_weight=5)
        self.assertEqual(path, [0, 1, 2])
        
    def test_remove_edge(self):
        # Test removing an edge from the network.
        initialize_network(3)
        add_edge(0, 1, 10)
        add_edge(1, 2, 10)
        # Ensure path exists.
        path = find_optimal_path(0, 2, latency_weight=1, congestion_weight=1)
        self.assertEqual(path, [0, 1, 2])
        # Remove edge (1,2)
        remove_edge(1, 2)
        # Now there should be no path between 0 and 2.
        path = find_optimal_path(0, 2, latency_weight=1, congestion_weight=1)
        self.assertEqual(path, [])
        # Re-add edge and test again.
        add_edge(1, 2, 10)
        path = find_optimal_path(0, 2, latency_weight=1, congestion_weight=1)
        self.assertEqual(path, [0, 1, 2])

    def test_multiple_paths_with_varied_weights(self):
        # Create a more complex network with multiple routes.
        initialize_network(5)
        # Graph topology:
        # 0-1: 5, 0-2: 10
        # 1-3: 5, 2-3: 5, 3-4: 5
        add_edge(0, 1, 5)
        add_edge(0, 2, 10)
        add_edge(1, 3, 5)
        add_edge(2, 3, 5)
        add_edge(3, 4, 5)
        
        # Initially, congestion is 0 and latency is the only factor.
        # Both paths: 0-1-3-4 cost 15 and 0-2-3-4 cost 20 latency.
        path = find_optimal_path(0, 4, latency_weight=1, congestion_weight=1)
        self.assertEqual(path, [0, 1, 3, 4])
        
        # Increase congestion on node 1.
        send_packet(1)  # congestion at node 1 = 1.
        # Now, cost for 0-1-3-4 becomes: latency 5+5+5 =15, congestion: 0+1+0+0=1*weight 1 = 1, total =16.
        # Path 0-2-3-4 has: latency 10+5+5 =20, congestion 0, total=20.
        path = find_optimal_path(0, 4, latency_weight=1, congestion_weight=1)
        self.assertEqual(path, [0, 1, 3, 4])
        
        # Increase congestion on node 1 further so that alternative path becomes better.
        send_packet(1)  # now congestion at node 1 = 2.
        # Now, path 0-1-3-4 cost = 15+2 =17.
        # If we modify weights: if congestion weight is high, say 5.
        path = find_optimal_path(0, 4, latency_weight=1, congestion_weight=5)
        # Cost path 0-1-3-4 = 15 + 2*5 = 25.
        # Cost path 0-2-3-4 = 20 + 0 =20.
        self.assertEqual(path, [0, 2, 3, 4])

    def test_congestion_never_negative(self):
        # Test that receive_packet does not let congestion fall below 0.
        initialize_network(3)
        # Initially, congestion at each node is 0.
        receive_packet(0)
        receive_packet(1)
        receive_packet(2)
        # Add an edge and look for a valid path.
        add_edge(0, 1, 10)
        add_edge(1, 2, 10)
        path = find_optimal_path(0, 2, latency_weight=1, congestion_weight=1)
        self.assertEqual(path, [0, 1, 2])
        # Now, send and receive packets.
        send_packet(1)
        receive_packet(1)
        # Congestion at node 1 should be 0 now.
        path = find_optimal_path(0, 2, latency_weight=1, congestion_weight=10)
        self.assertEqual(path, [0, 1, 2])

if __name__ == '__main__':
    unittest.main()