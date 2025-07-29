import unittest
from data_replication import replicate_data

class TestDataReplication(unittest.TestCase):
    def test_trivial_k1(self):
        # Single data object with K=1; already present so no replication needed.
        N = 2
        M = 1
        K = 1
        capacity = [10, 10]
        initial_locations = [0b01]  # Object is present in data center 0.
        cost = [
            [100],
            [200]
        ]
        self.assertEqual(replicate_data(N, M, K, capacity, initial_locations, cost), 0)

    def test_example_from_description(self):
        # Example: N=3, M=2, K=2. Object0 in DC0 and Object1 in DC1.
        N = 3
        M = 2
        K = 2
        capacity = [5, 5, 5]
        initial_locations = [0b001, 0b010]
        cost = [
            [1, 2],
            [2, 1],
            [3, 3]
        ]
        self.assertEqual(replicate_data(N, M, K, capacity, initial_locations, cost), 4)

    def test_impossible_due_to_capacity(self):
        # N=2, M=2, K=2. Each DC initially holds one object but capacities are too small to hold an extra object.
        N = 2
        M = 2
        K = 2
        capacity = [1, 1]
        initial_locations = [0b01, 0b10]  # Object0 is in DC0, Object1 is in DC1.
        cost = [
            [5, 5],
            [5, 5]
        ]
        self.assertEqual(replicate_data(N, M, K, capacity, initial_locations, cost), -1)

    def test_complex_case(self):
        # N=4, M=3, K=3.
        # Object0 initially in DC0 and DC1, Object1 in DC1, Object2 in DC2.
        # Expected solution: replicate Object0 -> DC3 (cost 1),
        # Object1 -> DC0 (cost 1) and DC2 (cost 3), Object2 -> DC0 (cost 2) and DC3 (cost 3)
        # Total cost = 1 + (1+3) + (2+3) = 10.
        N = 4
        M = 3
        K = 3
        capacity = [3, 3, 3, 3]
        initial_locations = [0b0011, 0b0010, 0b0100]
        cost = [
            [5, 1, 2],
            [2, 2, 8],
            [10, 3, 1],
            [1, 5, 3]
        ]
        self.assertEqual(replicate_data(N, M, K, capacity, initial_locations, cost), 10)

    def test_already_satisfied(self):
        # K=1 with each object already present in a distinct DC.
        N = 3
        M = 3
        K = 1
        capacity = [5, 5, 5]
        initial_locations = [0b001, 0b010, 0b100]
        cost = [
            [3, 2, 1],
            [6, 5, 4],
            [9, 8, 7]
        ]
        self.assertEqual(replicate_data(N, M, K, capacity, initial_locations, cost), 0)

if __name__ == '__main__':
    unittest.main()