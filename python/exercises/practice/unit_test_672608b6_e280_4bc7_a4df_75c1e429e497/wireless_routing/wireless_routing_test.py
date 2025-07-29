import unittest
from wireless_routing import find_optimal_path
import math

class WirelessRoutingTest(unittest.TestCase):
    def test_basic_path(self):
        # Basic test with a possible direct path
        nodes = [(0, 0, 10), (10, 0, 5), (5, 5, 7), (10, 10, 8), (0, 10, 6)]
        path = find_optimal_path(5, nodes, 12, 0, 3, 0.5)
        
        # Check that we got a valid path
        self.assertIsNotNone(path)
        self.assertIsInstance(path, list)
        
        # Check that the path starts with source and ends with destination
        self.assertEqual(path[0], 0)
        self.assertEqual(path[-1], 3)
        
        # Verify the path is valid (nodes are within range and have enough battery)
        self.verify_path_validity(path, nodes, 12, 0.5)

    def test_no_path_exists(self):
        # Test when no path exists due to range limitations
        nodes = [(0, 0, 10), (100, 0, 5), (200, 0, 7), (300, 0, 8)]
        path = find_optimal_path(4, nodes, 50, 0, 3, 0.5)
        self.assertEqual(path, [])

    def test_insufficient_battery(self):
        # Test when path exists physically but battery is insufficient
        nodes = [(0, 0, 10), (10, 0, 1), (20, 0, 7), (30, 0, 8)]
        # Node 1 doesn't have enough battery to relay to node 2
        path = find_optimal_path(4, nodes, 15, 0, 3, 0.5)
        
        # Should find an alternate path or return empty if none exists
        if path:
            self.verify_path_validity(path, nodes, 15, 0.5)
        else:
            self.assertEqual(path, [])

    def test_multiple_possible_paths(self):
        # Test with multiple possible paths - should choose minimum hops
        nodes = [(0, 0, 50), (10, 0, 50), (20, 0, 50), (30, 0, 50), (40, 0, 50)]
        path = find_optimal_path(5, nodes, 50, 0, 4, 0.1)
        
        # The minimum hop path would be directly from 0 to 4 (if in range)
        # or minimal number of intermediate nodes
        self.verify_path_validity(path, nodes, 50, 0.1)
        
        # Since R = 50, nodes can reach 5 positions away (50/10 = 5)
        # So the optimal path should be [0, 4]
        if self.calculate_distance(nodes[0], nodes[4]) <= 50:
            self.assertEqual(path, [0, 4])
        else:
            # If direct path not possible, check that # of hops is minimal
            self.assertLessEqual(len(path), 4)  # at most [0,1,2,3,4] which is 5 nodes

    def test_equal_hop_paths_choose_energy_efficient(self):
        # Test that among equal-hop paths, choose the most energy efficient
        # Three possible 2-hop paths from 0 to 4:
        # [0,1,4], [0,2,4], [0,3,4]
        # Path through node 2 should be most energy efficient
        nodes = [
            (0, 0, 100),    # Node 0 (source)
            (8, 1, 100),    # Node 1 (longer path)
            (5, 0, 100),    # Node 2 (shortest path)
            (7, 3, 100),    # Node 3 (medium path)
            (10, 0, 100)    # Node 4 (destination)
        ]
        
        path = find_optimal_path(5, nodes, 6, 0, 4, 0.5)
        
        # All nodes have enough battery, so should choose path [0, 2, 4]
        # as distances are minimized
        self.verify_path_validity(path, nodes, 6, 0.5)
        
        # Check if selected path is energy optimal
        if len(path) == 3:  # If it's a 2-hop path
            # Calculate total energy of the selected path
            selected_energy = self.calculate_path_energy(path, nodes, 0.5)
            
            # Try other possible 2-hop paths
            possible_paths = [[0, 1, 4], [0, 2, 4], [0, 3, 4]]
            for possible_path in possible_paths:
                if self.is_valid_path(possible_path, nodes, 6, 0.5):
                    possible_energy = self.calculate_path_energy(possible_path, nodes, 0.5)
                    # Selected path should be the most energy efficient
                    self.assertLessEqual(selected_energy, possible_energy)

    def test_long_complex_network(self):
        # Create a long line network to test complex routing
        nodes = []
        for i in range(50):
            # Place nodes in a line with varying battery levels
            nodes.append((i*10, 0, 5 + (i % 20)))
        
        # Test routing from one end to the other
        path = find_optimal_path(50, nodes, 15, 0, 49, 0.5)
        
        # Verify the path is valid
        self.verify_path_validity(path, nodes, 15, 0.5)
        
        # Check that the path has a reasonable number of hops
        # Maximum possible direct hops with range 15 is ⌊15/10⌋ = 1 position
        min_hops = math.ceil(49 / 1)  # Minimum theoretical hops needed
        self.assertLessEqual(len(path) - 1, min_hops * 1.5)  # Allow some inefficiency

    def test_edge_case_source_destination_in_range(self):
        # Test when source and destination are directly in range
        nodes = [(0, 0, 10), (5, 0, 5)]
        path = find_optimal_path(2, nodes, 10, 0, 1, 0.5)
        
        # Path should be direct: [0, 1]
        self.assertEqual(path, [0, 1])

    def test_edge_case_insufficient_source_battery(self):
        # Test when source doesn't have enough battery
        nodes = [(0, 0, 1), (10, 0, 10)]
        path = find_optimal_path(2, nodes, 10, 0, 1, 0.5)
        
        # Energy required for 0->1: 0.5 * 10 = 5, but battery is only 1
        self.assertEqual(path, [])

    def test_edge_case_destination_unreachable(self):
        # Test when destination is out of range from all other nodes
        nodes = [(0, 0, 100), (10, 0, 100), (20, 0, 100), (100, 100, 100)]
        path = find_optimal_path(4, nodes, 30, 0, 3, 0.5)
        
        # Destination (node 3) should be unreachable
        self.assertEqual(path, [])

    def test_sparse_network_with_bottlenecks(self):
        # Test a sparse network with potential bottlenecks
        nodes = [
            (0, 0, 100),     # Node 0 (source)
            (40, 10, 10),    # Node 1 - potential relay
            (80, 0, 100),    # Node 2 - potential relay
            (60, 40, 5),     # Node 3 - battery bottleneck
            (100, 50, 100)   # Node 4 (destination)
        ]
        
        path = find_optimal_path(5, nodes, 50, 0, 4, 0.5)
        
        # Verify the path validity
        if path:
            self.verify_path_validity(path, nodes, 50, 0.5)
            # Path should avoid node 3 due to battery bottleneck
            self.assertNotIn(3, path)
        else:
            # If no path found, that's also acceptable
            self.assertEqual(path, [])

    # Helper methods
    def calculate_distance(self, node1, node2):
        """Calculate Euclidean distance between two nodes."""
        x1, y1, _ = node1
        x2, y2, _ = node2
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    
    def is_valid_path(self, path, nodes, R, C):
        """Check if a path is valid given range and battery constraints."""
        for i in range(len(path) - 1):
            node1_idx = path[i]
            node2_idx = path[i+1]
            
            # Check if within range
            dist = self.calculate_distance(nodes[node1_idx], nodes[node2_idx])
            if dist > R:
                return False
            
            # Check if sufficient battery
            energy_needed = C * dist
            if nodes[node1_idx][2] < energy_needed:
                return False
                
        return True
    
    def calculate_path_energy(self, path, nodes, C):
        """Calculate total energy consumption of a path."""
        total_energy = 0
        for i in range(len(path) - 1):
            node1_idx = path[i]
            node2_idx = path[i+1]
            dist = self.calculate_distance(nodes[node1_idx], nodes[node2_idx])
            total_energy += C * dist
        return total_energy
    
    def verify_path_validity(self, path, nodes, R, C):
        """Verify that a path is valid and makes sense."""
        # If path is empty, nothing to check
        if not path:
            return
            
        # Check that path starts with source and ends with destination
        self.assertTrue(self.is_valid_path(path, nodes, R, C), 
                        "Path is invalid with respect to range or battery constraints")
        
        # Check that the path is connected (no jumps beyond range)
        for i in range(len(path) - 1):
            node1_idx = path[i]
            node2_idx = path[i+1]
            dist = self.calculate_distance(nodes[node1_idx], nodes[node2_idx])
            self.assertLessEqual(dist, R, 
                                f"Nodes {node1_idx} and {node2_idx} are too far apart ({dist} > {R})")
            
            # Check battery sufficiency
            energy_needed = C * dist
            self.assertLessEqual(energy_needed, nodes[node1_idx][2], 
                                f"Node {node1_idx} has insufficient battery ({energy_needed} > {nodes[node1_idx][2]})")

if __name__ == '__main__':
    unittest.main()