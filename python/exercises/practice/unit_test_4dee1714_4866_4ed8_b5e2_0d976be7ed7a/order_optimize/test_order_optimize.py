import unittest
from order_optimize import optimal_fulfillment_order

class TestOrderOptimize(unittest.TestCase):
    def test_small_case(self):
        orders = [
            {'order_id': 1, 'items': {1: 2, 2: 1}},
            {'order_id': 2, 'items': {2: 3, 3: 1}},
            {'order_id': 3, 'items': {1: 1, 3: 2}}
        ]
        items_size = {1: 5, 2: 3, 3: 2}
        result = optimal_fulfillment_order(orders, items_size)
        self.assertEqual(len(result), 3)
        self.assertEqual(set(result), {1, 2, 3})
        # Check if total waiting time is minimized
        # This checks one possible optimal solution
        self.assertTrue(result in ([2, 3, 1], [3, 2, 1]))

    def test_single_order(self):
        orders = [{'order_id': 1, 'items': {1: 1}}]
        items_size = {1: 5}
        self.assertEqual(optimal_fulfillment_order(orders, items_size), [1])

    def test_equal_fulfillment_time(self):
        orders = [
            {'order_id': 1, 'items': {1: 1}},
            {'order_id': 2, 'items': {2: 1}}
        ]
        items_size = {1: 5, 2: 5}
        result = optimal_fulfillment_order(orders, items_size)
        self.assertEqual(len(result), 2)
        self.assertEqual(set(result), {1, 2})

    def test_large_quantity(self):
        orders = [
            {'order_id': 1, 'items': {1: 1000}},
            {'order_id': 2, 'items': {2: 1}}
        ]
        items_size = {1: 1, 2: 1000}
        result = optimal_fulfillment_order(orders, items_size)
        self.assertEqual(result, [1, 2])

    def test_multiple_items(self):
        orders = [
            {'order_id': 1, 'items': {1: 1, 2: 1, 3: 1}},
            {'order_id': 2, 'items': {1: 2}},
            {'order_id': 3, 'items': {3: 3}}
        ]
        items_size = {1: 4, 2: 3, 3: 2}
        result = optimal_fulfillment_order(orders, items_size)
        self.assertEqual(len(result), 3)
        self.assertEqual(set(result), {1, 2, 3})
        # Check optimal order (3 should come first)
        self.assertEqual(result[0], 3)

    def test_invalid_item(self):
        orders = [{'order_id': 1, 'items': {1: 1}}]
        items_size = {2: 5}
        with self.assertRaises(ValueError):
            optimal_fulfillment_order(orders, items_size)

    def test_empty_orders(self):
        self.assertEqual(optimal_fulfillment_order([], {}), [])

if __name__ == '__main__':
    unittest.main()