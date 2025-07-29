import unittest
import time
from dynamic_connect import DynamicConnectivityOracle


class DynamicConnectTest(unittest.TestCase):
    def test_basic_connectivity(self):
        oracle = DynamicConnectivityOracle(10)
        self.assertFalse(oracle.are_connected(1, 2))
        
        oracle.connect(1, 2)
        self.assertTrue(oracle.are_connected(1, 2))
        self.assertTrue(oracle.are_connected(2, 1))  # symmetry
        
        self.assertFalse(oracle.are_connected(1, 3))
        self.assertFalse(oracle.are_connected(2, 3))

    def test_transitive_connections(self):
        oracle = DynamicConnectivityOracle(10)
        
        oracle.connect(1, 2)
        oracle.connect(2, 3)
        
        self.assertTrue(oracle.are_connected(1, 3))
        self.assertTrue(oracle.are_connected(3, 1))
        
        oracle.connect(4, 5)
        self.assertTrue(oracle.are_connected(4, 5))
        self.assertFalse(oracle.are_connected(1, 5))
        
        oracle.connect(3, 4)
        self.assertTrue(oracle.are_connected(1, 5))

    def test_self_loops(self):
        oracle = DynamicConnectivityOracle(10)
        
        oracle.connect(1, 1)
        self.assertTrue(oracle.are_connected(1, 1))
        
        # Self-loops shouldn't affect other connections
        self.assertFalse(oracle.are_connected(1, 2))

    def test_duplicate_connections(self):
        oracle = DynamicConnectivityOracle(10)
        
        oracle.connect(1, 2)
        oracle.connect(1, 2)  # Duplicate connection
        self.assertTrue(oracle.are_connected(1, 2))
        
        # Ensure multiple calls to connect don't break the structure
        oracle.connect(2, 3)
        self.assertTrue(oracle.are_connected(1, 3))

    def test_large_component(self):
        oracle = DynamicConnectivityOracle(1000)
        
        # Create a large component
        for i in range(999):
            oracle.connect(i, i + 1)
        
        self.assertTrue(oracle.are_connected(0, 999))
        self.assertTrue(oracle.are_connected(123, 456))

    def test_disjoint_components(self):
        oracle = DynamicConnectivityOracle(1000)
        
        # Create two disjoint components
        for i in range(0, 499):
            oracle.connect(i, i + 1)
            
        for i in range(500, 999):
            oracle.connect(i, i + 1)
        
        self.assertTrue(oracle.are_connected(100, 200))
        self.assertTrue(oracle.are_connected(600, 700))
        self.assertFalse(oracle.are_connected(100, 600))
        
        # Connect the components
        oracle.connect(0, 999)
        self.assertTrue(oracle.are_connected(100, 600))

    def test_max_node_value(self):
        # Test with very large node values
        large_n = 10**9
        oracle = DynamicConnectivityOracle(large_n)
        
        big_node1 = 10**9 - 2
        big_node2 = 10**9 - 1
        
        oracle.connect(big_node1, big_node2)
        self.assertTrue(oracle.are_connected(big_node1, big_node2))
        self.assertFalse(oracle.are_connected(0, big_node1))

    def test_sparse_connections(self):
        # Test with large node space but few connections
        oracle = DynamicConnectivityOracle(10**6)
        
        sparse_nodes = [0, 10000, 100000, 500000, 999999]
        for i in range(len(sparse_nodes) - 1):
            oracle.connect(sparse_nodes[i], sparse_nodes[i + 1])
        
        self.assertTrue(oracle.are_connected(0, 999999))
        self.assertFalse(oracle.are_connected(1, 999999))

    def test_performance(self):
        # This is a basic performance test to ensure operations are efficient
        start_time = time.time()
        
        n = 10**5  # Large but not too large for a unit test
        oracle = DynamicConnectivityOracle(n)
        
        # Test many connect operations
        for i in range(0, n-1, 2):
            oracle.connect(i, i + 1)
        
        # Test many queries
        for i in range(0, n-2, 2):
            oracle.are_connected(i, i + 2)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # This is a soft assertion - actual time will depend on hardware
        # Just ensuring it completes in a reasonable time
        self.assertLess(execution_time, 10, "Performance test took too long")

    def test_stress_test(self):
        oracle = DynamicConnectivityOracle(10**6)
        
        # Create a number of small clusters
        clusters = 100
        nodes_per_cluster = 100
        
        for c in range(clusters):
            base = c * nodes_per_cluster
            for i in range(nodes_per_cluster - 1):
                oracle.connect(base + i, base + i + 1)
        
        # Verify intra-cluster connectivity
        for c in range(clusters):
            base = c * nodes_per_cluster
            self.assertTrue(oracle.are_connected(base, base + nodes_per_cluster - 1))
        
        # Verify inter-cluster isolation
        for c1 in range(clusters):
            for c2 in range(c1 + 1, clusters):
                base1 = c1 * nodes_per_cluster
                base2 = c2 * nodes_per_cluster
                self.assertFalse(oracle.are_connected(base1, base2))
        
        # Now connect all clusters
        for c in range(clusters - 1):
            base1 = c * nodes_per_cluster
            base2 = (c + 1) * nodes_per_cluster
            oracle.connect(base1, base2)
        
        # Verify full connectivity
        self.assertTrue(oracle.are_connected(0, (clusters - 1) * nodes_per_cluster))


if __name__ == '__main__':
    unittest.main()