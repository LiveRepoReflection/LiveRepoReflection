import unittest
from network_router.network_router import NetworkRouter

class TestNetworkRouter(unittest.TestCase):
    def setUp(self):
        # Simple 4-node network
        self.small_network = [
            (0, 1, 5.0, 10),
            (1, 2, 3.0, 5),
            (2, 3, 7.0, 8),
            (0, 3, 15.0, 20)
        ]
        self.router = NetworkRouter(4, self.small_network)

    def test_simple_path(self):
        path = self.router.find_path(0, 3)
        self.assertEqual(path, [0, 1, 2, 3])

    def test_load_balancing(self):
        # First path should take 0-1-2-3
        path1 = self.router.find_path(0, 3)
        self.assertEqual(path1, [0, 1, 2, 3])

        # After first path, link 1-2 becomes more congested
        # Next path should take 0-3 directly
        path2 = self.router.find_path(0, 3)
        self.assertEqual(path2, [0, 3])

    def test_no_path(self):
        # Disconnect node 3
        disconnected_network = [
            (0, 1, 5.0, 10),
            (1, 2, 3.0, 5)
        ]
        router = NetworkRouter(4, disconnected_network)
        path = router.find_path(0, 3)
        self.assertEqual(path, [])

    def test_large_network(self):
        # Create a 100-node ring network
        large_network = []
        for i in range(100):
            large_network.append((i, (i+1)%100, 1.0, 10))
        
        router = NetworkRouter(100, large_network)
        path = router.find_path(0, 50)
        self.assertEqual(len(path), 51)  # Should take shortest path

    def test_concurrent_requests(self):
        import threading

        results = []
        def worker(src, dest):
            path = self.router.find_path(src, dest)
            results.append(path)

        threads = [
            threading.Thread(target=worker, args=(0, 3)),
            threading.Thread(target=worker, args=(1, 3)),
            threading.Thread(target=worker, args=(0, 2))
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(results), 3)
        self.assertTrue(all(len(path) > 0 for path in results))

    def test_cool_down_period(self):
        # First path loads the links
        path1 = self.router.find_path(0, 3)
        
        # Simulate cool-down period
        self.router.update_loads(-1)  # Decrease all loads by 1
        
        # Path should return to original optimal path
        path2 = self.router.find_path(0, 3)
        self.assertEqual(path2, [0, 1, 2, 3])

if __name__ == '__main__':
    unittest.main()