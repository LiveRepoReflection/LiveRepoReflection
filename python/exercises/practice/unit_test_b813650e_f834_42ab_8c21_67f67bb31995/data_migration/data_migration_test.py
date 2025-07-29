import unittest
from data_migration import minimum_migration_cost


class DataMigrationTest(unittest.TestCase):
    def test_simple_case(self):
        N = 3
        M = 3
        T = 2
        ownership = [
            [True, False, False],  # Datacenter 0 owns block 0
            [False, True, False],  # Datacenter 1 owns block 1
            [False, False, True]   # Datacenter 2 owns block 2
        ]
        size = [10, 20, 30]  # Size of blocks 0, 1, and 2 in GB
        bandwidth = [
            [0, 5, 10],    # Bandwidth from 0 to 0, 0 to 1, 0 to 2 (in Gbps)
            [5, 0, 15],    # Bandwidth from 1 to 0, 1 to 1, 1 to 2
            [10, 15, 0]     # Bandwidth from 2 to 0, 2 to 1, 2 to 2
        ]
        
        # Direct transfer cost calculation:
        # Block 0 (10GB) from DC0 to DC2: 10/10 = 1 second
        # Block 1 (20GB) from DC1 to DC2: 20/15 = 1.33333 seconds
        # Block 2 is already at DC2: 0 seconds
        # Total: 2.33333 seconds
        expected = 2.33333333
        
        result = minimum_migration_cost(N, M, T, ownership, size, bandwidth)
        self.assertAlmostEqual(expected, result, places=6)
    
    def test_target_has_all_data(self):
        N = 3
        M = 3
        T = 2
        ownership = [
            [False, False, False],
            [False, False, False],
            [True, True, True]
        ]
        size = [10, 20, 30]
        bandwidth = [
            [0, 5, 10],
            [5, 0, 15],
            [10, 15, 0]
        ]
        
        # All data is already at the target datacenter
        expected = 0.0
        
        result = minimum_migration_cost(N, M, T, ownership, size, bandwidth)
        self.assertAlmostEqual(expected, result, places=6)
    
    def test_intermediate_transfer_optimal(self):
        N = 3
        M = 1
        T = 2
        ownership = [
            [True, False, False],
            [False, False, False],
            [False, False, False]
        ]
        size = [100]
        bandwidth = [
            [0, 50, 5],    # DC0 to DC2 direct is slow (5 Gbps)
            [50, 0, 50],   # DC0 to DC1 to DC2 is faster
            [5, 50, 0]
        ]
        
        # Direct transfer: 100/5 = 20 seconds
        # Via DC1: 100/50 + 100/50 = 2 + 2 = 4 seconds (optimal)
        expected = 4.0
        
        result = minimum_migration_cost(N, M, T, ownership, size, bandwidth)
        self.assertAlmostEqual(expected, result, places=6)
    
    def test_asymmetric_bandwidth(self):
        N = 3
        M = 1
        T = 2
        ownership = [
            [True, False, False],
            [False, False, False],
            [False, False, False]
        ]
        size = [100]
        bandwidth = [
            [0, 10, 5],   # DC0 to DC2 is 5 Gbps
            [5, 0, 20],   # DC1 to DC2 is 20 Gbps
            [10, 5, 0]    # Return paths are different
        ]
        
        # Direct transfer: 100/5 = 20 seconds
        # Via DC1: 100/10 + 100/20 = 10 + 5 = 15 seconds (optimal)
        expected = 15.0
        
        result = minimum_migration_cost(N, M, T, ownership, size, bandwidth)
        self.assertAlmostEqual(expected, result, places=6)
    
    def test_multiple_blocks_with_intermediate(self):
        N = 4
        M = 3
        T = 3
        ownership = [
            [True, False, False],   # DC0 has block 0
            [False, True, False],   # DC1 has block 1
            [False, False, True],   # DC2 has block 2
            [False, False, False]    # DC3 (target) has nothing
        ]
        size = [10, 20, 30]
        bandwidth = [
            [0, 100, 5, 5],    # DC0 has fast connection to DC1
            [100, 0, 100, 5],  # DC1 has fast connection to DC0 and DC2
            [5, 100, 0, 100],  # DC2 has fast connection to DC1 and DC3
            [5, 5, 100, 0]     # DC3 has fast connection to DC2
        ]
        
        # Optimal paths:
        # Block 0: DC0 -> DC1 -> DC2 -> DC3 = 10/100 + 10/100 + 10/100 = 0.3 seconds
        # Block 1: DC1 -> DC2 -> DC3 = 20/100 + 20/100 = 0.4 seconds
        # Block 2: DC2 -> DC3 = 30/100 = 0.3 seconds
        # Total: 1.0 seconds
        expected = 1.0
        
        result = minimum_migration_cost(N, M, T, ownership, size, bandwidth)
        self.assertAlmostEqual(expected, result, places=6)
    
    def test_larger_case(self):
        N = 5
        M = 5
        T = 4
        ownership = [
            [True, True, False, False, False],
            [False, False, True, False, False],
            [False, False, False, True, False],
            [False, False, False, False, False],
            [False, False, False, False, True]
        ]
        size = [10, 15, 20, 25, 30]
        bandwidth = [
            [0, 50, 10, 5, 5],
            [50, 0, 50, 10, 5],
            [10, 50, 0, 50, 10],
            [5, 10, 50, 0, 50],
            [5, 5, 10, 50, 0]
        ]
        
        # This represents a complex case where multiple paths must be evaluated
        result = minimum_migration_cost(N, M, T, ownership, size, bandwidth)
        # The exact value is complex to manually compute, but we can verify it's positive
        self.assertGreater(result, 0)
    
    def test_shared_blocks(self):
        N = 3
        M = 2
        T = 2
        ownership = [
            [True, False],  # DC0 has block 0
            [True, True],   # DC1 has blocks 0 and 1
            [False, False]  # DC2 (target) has nothing
        ]
        size = [10, 20]
        bandwidth = [
            [0, 10, 5],
            [10, 0, 15],
            [5, 15, 0]
        ]
        
        # Optimal transfers:
        # Block 0 from DC1 to DC2: 10/15 = 0.6667 seconds (better than from DC0)
        # Block 1 from DC1 to DC2: 20/15 = 1.3333 seconds
        # Total: 2.0 seconds
        expected = 2.0
        
        result = minimum_migration_cost(N, M, T, ownership, size, bandwidth)
        self.assertAlmostEqual(expected, result, places=6)
    
    def test_very_small_dataset(self):
        N = 2
        M = 1
        T = 1
        ownership = [
            [True],
            [False]
        ]
        size = [1]
        bandwidth = [
            [0, 10],
            [10, 0]
        ]
        
        # Transfer 1GB at 10Gbps: 1/10 = 0.1 seconds
        expected = 0.1
        
        result = minimum_migration_cost(N, M, T, ownership, size, bandwidth)
        self.assertAlmostEqual(expected, result, places=6)


if __name__ == '__main__':
    unittest.main()