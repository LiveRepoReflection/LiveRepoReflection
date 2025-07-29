import unittest
import uuid
from efficient_routing import find_path

class MockNetwork:
    def __init__(self, connections=None):
        """Initialize the mock network with given connections."""
        self.connections = connections or {}
        self.neighbor_calls = 0
    
    def neighbors(self, node_uuid):
        """Return the neighbors of the given node."""
        self.neighbor_calls += 1
        return self.connections.get(node_uuid, [])
    
    def reset_call_counter(self):
        """Reset the neighbor call counter."""
        self.neighbor_calls = 0

class EfficientRoutingTest(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        # Create UUIDs for test cases
        self.nodes = {chr(ord('A') + i): uuid.uuid4() for i in range(10)}
        
        # Example network as described in the problem
        connections = {
            self.nodes['A']: [self.nodes['B']],
            self.nodes['B']: [self.nodes['A'], self.nodes['C'], self.nodes['E']],
            self.nodes['C']: [self.nodes['B'], self.nodes['D']],
            self.nodes['D']: [self.nodes['C']],
            self.nodes['E']: [self.nodes['B']]
        }
        self.small_network = MockNetwork(connections)
        
        # Create a larger network for performance testing
        self.large_connections = self._create_large_network(500)
        self.large_network = MockNetwork(self.large_connections)

    def _create_large_network(self, size):
        """Create a larger network for testing scalability."""
        large_connections = {}
        # Create a ring network with some random connections
        node_ids = [uuid.uuid4() for _ in range(size)]
        
        for i in range(size):
            neighbors = [node_ids[(i + 1) % size], node_ids[(i - 1) % size]]
            # Add some random long-distance connections
            if i % 10 == 0 and i + 5 < size:
                neighbors.append(node_ids[i + 5])
            if i % 20 == 0 and i + 50 < size:
                neighbors.append(node_ids[i + 50])
            large_connections[node_ids[i]] = neighbors
        
        return large_connections, node_ids

    def test_same_source_destination(self):
        """Test when source and destination are the same."""
        path = find_path(self.small_network, self.nodes['A'], self.nodes['A'])
        self.assertEqual(path, [self.nodes['A']])
        self.assertLessEqual(self.small_network.neighbor_calls, 1, 
                          "Should make at most 1 call to neighbors() when source and destination are the same")

    def test_direct_connection(self):
        """Test when source and destination are directly connected."""
        self.small_network.reset_call_counter()
        path = find_path(self.small_network, self.nodes['A'], self.nodes['B'])
        self.assertEqual(path, [self.nodes['A'], self.nodes['B']])
        self.assertLessEqual(self.small_network.neighbor_calls, 2, 
                          "Should make at most 2 calls to neighbors() for direct connections")

    def test_two_hop_path(self):
        """Test finding a path with two hops."""
        self.small_network.reset_call_counter()
        path = find_path(self.small_network, self.nodes['A'], self.nodes['C'])
        self.assertEqual(path, [self.nodes['A'], self.nodes['B'], self.nodes['C']])

    def test_three_hop_path(self):
        """Test finding a path with three hops."""
        self.small_network.reset_call_counter()
        path = find_path(self.small_network, self.nodes['A'], self.nodes['D'])
        self.assertEqual(path, [self.nodes['A'], self.nodes['B'], self.nodes['C'], self.nodes['D']])

    def test_no_path_exists(self):
        """Test when no path exists between source and destination."""
        non_existent_node = uuid.uuid4()
        path = find_path(self.small_network, self.nodes['A'], non_existent_node)
        self.assertEqual(path, [])

    def test_alternative_paths(self):
        """Test where there are multiple possible paths."""
        # Add a connection to create an alternative path
        original_connections = self.small_network.connections.copy()
        self.small_network.connections[self.nodes['A']] = [self.nodes['B'], self.nodes['E']]
        self.small_network.connections[self.nodes['E']].append(self.nodes['A'])
        
        self.small_network.reset_call_counter()
        path = find_path(self.small_network, self.nodes['A'], self.nodes['E'])
        
        # Either [A, E] or [A, B, E] should be valid, but [A, E] is shorter
        self.assertIn(path, [[self.nodes['A'], self.nodes['E']], 
                           [self.nodes['A'], self.nodes['B'], self.nodes['E']]])
        
        # If the algorithm is optimal, it should find the shortest path
        if len(path) == 2:
            self.assertEqual(path, [self.nodes['A'], self.nodes['E']])
        
        # Restore original connections
        self.small_network.connections = original_connections

    def test_large_network_performance(self):
        """Test performance on a larger network."""
        large_connections, node_ids = self._create_large_network(500)
        large_network = MockNetwork(large_connections)
        
        # Test a path that should be relatively short (neighboring nodes)
        source = node_ids[100]
        destination = node_ids[101]
        large_network.reset_call_counter()
        path = find_path(large_network, source, destination)
        
        # Path should exist and be short
        self.assertGreater(len(path), 0)
        self.assertLessEqual(len(path), 3)
        
        # Test a longer path
        source = node_ids[100]
        destination = node_ids[200]
        large_network.reset_call_counter()
        path = find_path(large_network, source, destination)
        
        # Path should exist
        self.assertGreater(len(path), 0)
        
        # Check that the algorithm doesn't explore the entire network
        # 500 nodes in the network, but should make far fewer calls
        self.assertLess(large_network.neighbor_calls, 500)

    def test_dynamic_network_changes(self):
        """Test handling of dynamic network changes."""
        # First, find a path
        self.small_network.reset_call_counter()
        original_path = find_path(self.small_network, self.nodes['A'], self.nodes['D'])
        original_calls = self.small_network.neighbor_calls
        
        # Now, add a direct connection and find the path again
        self.small_network.connections[self.nodes['A']].append(self.nodes['D'])
        self.small_network.connections[self.nodes['D']].append(self.nodes['A'])
        
        self.small_network.reset_call_counter()
        new_path = find_path(self.small_network, self.nodes['A'], self.nodes['D'])
        
        # The new path should be shorter
        self.assertLess(len(new_path), len(original_path))
        self.assertEqual(new_path, [self.nodes['A'], self.nodes['D']])

    def test_cycle_handling(self):
        """Test handling of cycles in the network."""
        # Create a network with a cycle
        cycle_connections = {
            self.nodes['A']: [self.nodes['B']],
            self.nodes['B']: [self.nodes['A'], self.nodes['C']],
            self.nodes['C']: [self.nodes['B'], self.nodes['D'], self.nodes['A']],
            self.nodes['D']: [self.nodes['C']]
        }
        cycle_network = MockNetwork(cycle_connections)
        
        # Find a path through the cycle
        cycle_network.reset_call_counter()
        path = find_path(cycle_network, self.nodes['A'], self.nodes['D'])
        
        # Should find a valid path despite the cycle
        self.assertGreater(len(path), 0)
        self.assertEqual(path[0], self.nodes['A'])
        self.assertEqual(path[-1], self.nodes['D'])

if __name__ == '__main__':
    unittest.main()