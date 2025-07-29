import unittest
from route_optimizer.route_optimizer import optimal_route_plan

class TestOptimalRoutePlan(unittest.TestCase):

    def test_no_orders(self):
        # When there are no orders, the expected plan is an empty list.
        nodes = [
            (1, 0.0, 0.0),
            (2, 0.0, 1.0)
        ]
        edges = [
            (1, 2, 10)
        ]
        orders = []
        expected = []
        result = optimal_route_plan(nodes, edges, orders)
        self.assertEqual(result, expected)

    def test_single_order(self):
        # Single order should return a list with that order id.
        nodes = [
            (1, 37.7749, -122.4194),
            (2, 37.7833, -122.4167)
        ]
        edges = [
            (1, 2, 5)
        ]
        orders = [
            (100, 1, 2, 50, 60, 5)
        ]
        expected = [100]
        result = optimal_route_plan(nodes, edges, orders)
        self.assertEqual(result, expected)

    def test_priority_tiebreak(self):
        # Orders with identical time windows but different priorities.
        # Higher priority order should be delivered first.
        nodes = [
            (1, 0.0, 0.0),
            (2, 0.0, 1.0),
            (3, 1.0, 1.0)
        ]
        edges = [
            (1, 2, 3),
            (2, 3, 3),
            (1, 3, 7)
        ]
        orders = [
            (301, 1, 2, 10, 20, 5),
            (302, 2, 3, 10, 20, 10)
        ]
        # Expected optimal delivery: deliver order 302 first as it has a higher priority,
        # then order 301.
        expected = [302, 301]
        result = optimal_route_plan(nodes, edges, orders)
        self.assertEqual(result, expected)

    def test_multiple_orders(self):
        # More complex test with several orders and varying deadlines.
        # The intended optimal sequence is designed manually, prioritizing
        # higher priority orders and earlier deadlines.
        nodes = [
            (1, 0.0, 0.0),
            (2, 0.0, 1.0),
            (3, 1.0, 0.0),
            (4, 1.0, 1.0),
            (5, 2.0, 2.0)
        ]
        edges = [
            (1, 2, 5),
            (2, 4, 5),
            (1, 3, 7),
            (3, 4, 7),
            (4, 5, 10),
            (2, 5, 12),
            (3, 5, 8)
        ]
        orders = [
            # Order format: (order_id, source_node, destination_node, start_time, end_time, priority)
            (201, 1, 4, 50, 60, 1),  # low priority, later window
            (202, 2, 5, 55, 65, 2),  # medium priority
            (203, 3, 5, 40, 50, 3)   # highest priority, earliest window
        ]
        # Expected optimal ordering: deliver order 203 first to meet its tighter window,
        # then order 202, and finally order 201.
        expected = [203, 202, 201]
        result = optimal_route_plan(nodes, edges, orders)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()