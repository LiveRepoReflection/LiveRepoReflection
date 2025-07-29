import unittest
from order_allocator import allocate_market_order


class OrderAllocatorTest(unittest.TestCase):
    def test_basic_allocation(self):
        order_book = {
            100: ["order1", "order2"],
            101: ["order3"],
            102: ["order4"]
        }
        order_quantities = {
            "order1": 5,
            "order2": 3,
            "order3": 4,
            "order4": 2
        }
        market_buy_order = 8
        expected = [("order1", 5), ("order2", 3)]
        self.assertEqual(allocate_market_order(order_book, order_quantities, market_buy_order), expected)

    def test_empty_order_book(self):
        order_book = {}
        order_quantities = {}
        market_buy_order = 10
        expected = []
        self.assertEqual(allocate_market_order(order_book, order_quantities, market_buy_order), expected)

    def test_insufficient_liquidity(self):
        order_book = {
            100: ["order1"],
            101: ["order2"]
        }
        order_quantities = {
            "order1": 3,
            "order2": 2
        }
        market_buy_order = 10
        expected = [("order1", 3), ("order2", 2)]
        self.assertEqual(allocate_market_order(order_book, order_quantities, market_buy_order), expected)

    def test_multiple_orders_same_price(self):
        order_book = {
            100: ["order1", "order2", "order3"],
            101: ["order4"]
        }
        order_quantities = {
            "order1": 2,
            "order2": 3,
            "order3": 4,
            "order4": 5
        }
        market_buy_order = 7
        expected = [("order1", 2), ("order2", 3), ("order3", 2)]
        self.assertEqual(allocate_market_order(order_book, order_quantities, market_buy_order), expected)

    def test_unsorted_prices(self):
        order_book = {
            102: ["order3"],
            100: ["order1"],
            101: ["order2"]
        }
        order_quantities = {
            "order1": 3,
            "order2": 4,
            "order3": 5
        }
        market_buy_order = 5
        expected = [("order1", 3), ("order2", 2)]
        self.assertEqual(allocate_market_order(order_book, order_quantities, market_buy_order), expected)

    def test_exact_fill(self):
        order_book = {
            100: ["order1", "order2"]
        }
        order_quantities = {
            "order1": 5,
            "order2": 5
        }
        market_buy_order = 10
        expected = [("order1", 5), ("order2", 5)]
        self.assertEqual(allocate_market_order(order_book, order_quantities, market_buy_order), expected)

    def test_small_market_order(self):
        order_book = {
            100: ["order1"],
            101: ["order2"]
        }
        order_quantities = {
            "order1": 10,
            "order2": 10
        }
        market_buy_order = 1
        expected = [("order1", 1)]
        self.assertEqual(allocate_market_order(order_book, order_quantities, market_buy_order), expected)

    def test_large_order_book(self):
        order_book = {i: [f"order{i}"] for i in range(100, 1000)}
        order_quantities = {f"order{i}": 1 for i in range(100, 1000)}
        market_buy_order = 5
        expected = [(f"order{i}", 1) for i in range(100, 105)]
        self.assertEqual(allocate_market_order(order_book, order_quantities, market_buy_order), expected)

    def test_zero_quantity_market_order(self):
        order_book = {
            100: ["order1"],
            101: ["order2"]
        }
        order_quantities = {
            "order1": 5,
            "order2": 5
        }
        market_buy_order = 0
        expected = []
        self.assertEqual(allocate_market_order(order_book, order_quantities, market_buy_order), expected)

    def test_partial_fill_single_order(self):
        order_book = {
            100: ["order1"]
        }
        order_quantities = {
            "order1": 10
        }
        market_buy_order = 5
        expected = [("order1", 5)]
        self.assertEqual(allocate_market_order(order_book, order_quantities, market_buy_order), expected)


if __name__ == '__main__':
    unittest.main()