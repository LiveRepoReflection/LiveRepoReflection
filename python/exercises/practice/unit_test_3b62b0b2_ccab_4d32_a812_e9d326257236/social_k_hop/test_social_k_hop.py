import unittest
from social_k_hop import compute_k_hop_neighborhood

class TestSocialKHop(unittest.TestCase):
    def setUp(self):
        # Define test sharding and connection functions
        def test_shard_locator(user_id):
            return user_id % 3

        def test_get_connections(shard_index, user_id):
            network = {
                0: {
                    0: [1, 2],
                    3: [4, 5],
                    6: [7, 8]
                },
                1: {
                    1: [0, 9],
                    4: [3, 10],
                    7: [6, 11]
                },
                2: {
                    2: [0, 12],
                    5: [3, 13],
                    8: [6, 14]
                }
            }
            return network.get(shard_index, {}).get(user_id, [])

        self.shard_locator = test_shard_locator
        self.get_connections = test_get_connections

    def test_zero_hop(self):
        result = compute_k_hop_neighborhood(0, 0, self.shard_locator, self.get_connections)
        self.assertEqual(result, {0})

    def test_one_hop(self):
        result = compute_k_hop_neighborhood(0, 1, self.shard_locator, self.get_connections)
        self.assertEqual(result, {0, 1, 2})

    def test_two_hops(self):
        result = compute_k_hop_neighborhood(0, 2, self.shard_locator, self.get_connections)
        self.assertEqual(result, {0, 1, 2, 9, 12})

    def test_isolated_node(self):
        def isolated_get_connections(shard_index, user_id):
            return []
        result = compute_k_hop_neighborhood(15, 3, self.shard_locator, isolated_get_connections)
        self.assertEqual(result, {15})

    def test_cyclic_graph(self):
        def cyclic_get_connections(shard_index, user_id):
            if user_id == 0:
                return [1]
            elif user_id == 1:
                return [2]
            elif user_id == 2:
                return [0]
            return []
        result = compute_k_hop_neighborhood(0, 3, self.shard_locator, cyclic_get_connections)
        self.assertEqual(result, {0, 1, 2})

    def test_duplicate_connections(self):
        def duplicate_get_connections(shard_index, user_id):
            if user_id == 0:
                return [1, 1, 1, 2, 2]
            return []
        result = compute_k_hop_neighborhood(0, 1, self.shard_locator, duplicate_get_connections)
        self.assertEqual(result, {0, 1, 2})

    def test_large_k(self):
        result = compute_k_hop_neighborhood(0, 10, self.shard_locator, self.get_connections)
        expected = {0, 1, 2, 9, 12}  # Same as 2-hop because network diameter is 2
        self.assertEqual(result, expected)

    def test_invalid_k(self):
        with self.assertRaises(ValueError):
            compute_k_hop_neighborhood(0, -1, self.shard_locator, self.get_connections)
        with self.assertRaises(ValueError):
            compute_k_hop_neighborhood(0, 11, self.shard_locator, self.get_connections)

    def test_many_connections(self):
        def many_connections_get_connections(shard_index, user_id):
            if user_id == 0:
                return list(range(1, 101))  # Maximum 100 connections
            return []
        result = compute_k_hop_neighborhood(0, 1, self.shard_locator, many_connections_get_connections)
        expected = {0} | set(range(1, 101))
        self.assertEqual(result, expected)

    def test_performance(self):
        # Test that the function completes within reasonable time
        import time
        start_time = time.time()
        compute_k_hop_neighborhood(0, 5, self.shard_locator, self.get_connections)
        end_time = time.time()
        self.assertLess(end_time - start_time, 1.0)  # Should complete within 1 second

if __name__ == '__main__':
    unittest.main()