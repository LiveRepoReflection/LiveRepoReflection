import unittest
from optimal_cdn import optimize_cdn

class TestOptimalCDN(unittest.TestCase):
    def total_size(self, content_items, indices):
        # content_items is a list of tuples (size, popularity)
        return sum(content_items[i][0] for i in indices)

    def validate_output_structure(self, routers, user_requests, content_items, capacity, latency_matrix, placement):
        # Check that placement is a list with the same length as routers
        self.assertIsInstance(placement, list)
        self.assertEqual(len(placement), len(routers))
        for router_set in placement:
            self.assertIsInstance(router_set, set)
            # Every content index must be valid
            for idx in router_set:
                self.assertIsInstance(idx, int)
                self.assertTrue(0 <= idx < len(content_items))
            # Check capacity constraint: total size of contents must not exceed capacity
            self.assertTrue(self.total_size(content_items, router_set) <= capacity)

    def test_single_router_single_content(self):
        # One router, one user request, one content item
        routers = [(0, 0)]
        user_requests = [((0, 0), 1)]
        content_items = [(5, 100)]  # (size, popularity)
        capacity = 5
        # Latency matrix has central repo (index 0) and one router (index 1)
        latency_matrix = [
            [0, 10],
            [10, 0]
        ]
        placement = optimize_cdn(routers, user_requests, content_items, capacity, latency_matrix)
        self.validate_output_structure(routers, user_requests, content_items, capacity, latency_matrix, placement)

    def test_two_routers_two_contents(self):
        # Two routers, two user request locations, and two content items
        routers = [(0, 0), (0, 100)]
        user_requests = [((0, 10), 50), ((0, 95), 75)]
        content_items = [
            (3, 150),   # content item 0
            (4, 200)    # content item 1
        ]
        capacity = 5
        # Latency matrix dimensions: 1 central and 2 routers = 3x3
        latency_matrix = [
            [0, 10, 20],
            [10, 0, 15],
            [20, 15, 0]
        ]
        placement = optimize_cdn(routers, user_requests, content_items, capacity, latency_matrix)
        self.validate_output_structure(routers, user_requests, content_items, capacity, latency_matrix, placement)

    def test_multiple_routers_varied_contents(self):
        # Three routers, three user request locations and three content items.
        routers = [(10, 10), (50, 50), (90, 90)]
        user_requests = [
            ((15, 15), 100),
            ((55, 55), 150),
            ((85, 85), 200)
        ]
        content_items = [
            (2, 300),   # content 0
            (4, 250),   # content 1
            (3, 400)    # content 2
        ]
        capacity = 6
        # Latency matrix: 1 central + 3 routers = 4x4 matrix
        latency_matrix = [
            [0, 12, 25, 30],
            [12, 0, 18, 22],
            [25, 18, 0, 15],
            [30, 22, 15, 0]
        ]
        placement = optimize_cdn(routers, user_requests, content_items, capacity, latency_matrix)
        self.validate_output_structure(routers, user_requests, content_items, capacity, latency_matrix, placement)

    def test_zero_popularity_content(self):
        # Test with content items that have zero popularity; these items should be optional to store.
        routers = [(0, 0), (100, 100)]
        user_requests = [((10, 10), 100), ((90, 90), 100)]
        content_items = [
            (3, 0),     # content item 0: not popular
            (3, 300)    # content item 1: popular
        ]
        capacity = 3
        latency_matrix = [
            [0, 25, 30],
            [25, 0, 20],
            [30, 20, 0]
        ]
        placement = optimize_cdn(routers, user_requests, content_items, capacity, latency_matrix)
        self.validate_output_structure(routers, user_requests, content_items, capacity, latency_matrix, placement)

if __name__ == '__main__':
    unittest.main()