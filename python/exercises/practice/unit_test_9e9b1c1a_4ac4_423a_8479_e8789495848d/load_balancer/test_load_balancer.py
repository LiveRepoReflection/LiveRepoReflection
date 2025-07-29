import unittest
from load_balancer.load_balancer import LoadBalancer, LoadBalancingAlgorithm

class TestLoadBalancer(unittest.TestCase):
    def setUp(self):
        self.lb = LoadBalancer()
        self.server_ids = ["server1", "server2", "server3", "server4"]
        for server_id in self.server_ids:
            self.lb.add_server(server_id)

    def test_add_server(self):
        new_server = "server5"
        self.lb.add_server(new_server)
        self.assertIn(new_server, self.lb.get_all_servers())

    def test_remove_server(self):
        server_to_remove = "server1"
        self.lb.remove_server(server_to_remove)
        self.assertNotIn(server_to_remove, self.lb.get_all_servers())

    def test_round_robin_distribution(self):
        expected_order = self.server_ids.copy()
        for expected_server in expected_order * 2:  # Test two full cycles
            actual_server = self.lb.get_server("client1", LoadBalancingAlgorithm.ROUND_ROBIN)
            self.assertEqual(expected_server, actual_server)

    def test_consistent_hashing_same_client(self):
        client_id = "client123"
        first_server = self.lb.get_server(client_id, LoadBalancingAlgorithm.CONSISTENT_HASHING)
        for _ in range(10):
            self.assertEqual(first_server, 
                           self.lb.get_server(client_id, LoadBalancingAlgorithm.CONSISTENT_HASHING))

    def test_consistent_hashing_redistribution(self):
        client_id = "client123"
        original_server = self.lb.get_server(client_id, LoadBalancingAlgorithm.CONSISTENT_HASHING)
        self.lb.remove_server(original_server)
        new_server = self.lb.get_server(client_id, LoadBalancingAlgorithm.CONSISTENT_HASHING)
        self.assertNotEqual(original_server, new_server)
        self.assertIn(new_server, self.lb.get_all_servers())

    def test_empty_server_pool(self):
        empty_lb = LoadBalancer()
        self.assertIsNone(empty_lb.get_server("client1", LoadBalancingAlgorithm.ROUND_ROBIN))
        self.assertIsNone(empty_lb.get_server("client1", LoadBalancingAlgorithm.CONSISTENT_HASHING))

    def test_invalid_algorithm(self):
        with self.assertRaises(ValueError):
            self.lb.get_server("client1", "invalid_algorithm")

    def test_thread_safety(self):
        import threading
        test_clients = [f"client{i}" for i in range(100)]
        results = []

        def worker(client_id):
            results.append(self.lb.get_server(client_id, LoadBalancingAlgorithm.ROUND_ROBIN))

        threads = []
        for client_id in test_clients:
            t = threading.Thread(target=worker, args=(client_id,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(test_clients), len(results))
        self.assertTrue(all(server in self.lb.get_all_servers() for server in results))

if __name__ == '__main__':
    unittest.main()