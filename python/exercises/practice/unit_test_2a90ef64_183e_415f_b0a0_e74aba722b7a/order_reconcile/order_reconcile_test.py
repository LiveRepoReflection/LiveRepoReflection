import unittest
from order_reconcile import reconcile

class OrderReconcileTest(unittest.TestCase):
    def test_single_order_book(self):
        order_books = [
            {
                "bids": [(100.0, 5, "order1"), (99.5, 3, "order2")],
                "asks": [(101.0, 2, "order3"), (101.5, 4, "order4")]
            }
        ]
        expected = {
            "bids": [(100.0, 5, "order1"), (99.5, 3, "order2")],
            "asks": [(101.0, 2, "order3"), (101.5, 4, "order4")]
        }
        self.assertEqual(reconcile(order_books), expected)

    def test_multiple_order_books(self):
        order_books = [
            {
                "bids": [(100.0, 5, "order1"), (99.5, 3, "order2")],
                "asks": [(101.0, 2, "order3"), (101.5, 4, "order4")]
            },
            {
                "bids": [(100.0, 5, "order1"), (99.0, 2, "order5")],
                "asks": [(101.0, 2, "order3"), (102.0, 1, "order6")]
            },
            {
                "bids": [(100.0, 5, "order1")],
                "asks": [(101.0, 2, "order3"), (101.5, 4, "order4")]
            }
        ]
        expected = {
            "bids": [(100.0, 5, "order1"), (99.5, 3, "order2"), (99.0, 2, "order5")],
            "asks": [(101.0, 2, "order3"), (101.5, 4, "order4"), (102.0, 1, "order6")]
        }
        self.assertEqual(reconcile(order_books), expected)

    def test_quantity_resolution(self):
        # Two entries with same order_id but different quantities;
        # should pick the larger quantity.
        order_books = [
            {
                "bids": [(100.0, 5, "order1")],
                "asks": []
            },
            {
                "bids": [(100.0, 7, "order1")],
                "asks": []
            }
        ]
        expected = {
            "bids": [(100.0, 7, "order1")],
            "asks": []
        }
        self.assertEqual(reconcile(order_books), expected)

    def test_bid_sorting(self):
        # Test that bids are sorted descending by price, breaking ties with order_id.
        order_books = [
            {
                "bids": [(100.0, 5, "order2"), (100.0, 5, "order1"), (99.0, 2, "order3")],
                "asks": []
            }
        ]
        expected = {
            "bids": [(100.0, 5, "order1"), (100.0, 5, "order2"), (99.0, 2, "order3")],
            "asks": []
        }
        self.assertEqual(reconcile(order_books), expected)

    def test_ask_sorting(self):
        # Test that asks are sorted ascending by price, breaking ties with order_id.
        order_books = [
            {
                "bids": [],
                "asks": [(101.0, 2, "order2"), (101.0, 2, "order1"), (102.0, 1, "order3")]
            }
        ]
        expected = {
            "bids": [],
            "asks": [(101.0, 2, "order1"), (101.0, 2, "order2"), (102.0, 1, "order3")]
        }
        self.assertEqual(reconcile(order_books), expected)

    def test_empty_order_books_list(self):
        # If no order books are provided, expect an empty reconciled order book.
        order_books = []
        expected = {"bids": [], "asks": []}
        self.assertEqual(reconcile(order_books), expected)
    
    def test_partial_data_in_order_book(self):
        # Simulate a scenario where one of the order books returns incomplete data.
        # The function should reconcile using the valid order books.
        valid_order_book = {
            "bids": [(100.0, 5, "order1")],
            "asks": [(101.0, 2, "order3")]
        }
        corrupted_order_book = {}  # Missing bids and asks keys.
        order_books = [valid_order_book, corrupted_order_book]
        expected = {
            "bids": [(100.0, 5, "order1")],
            "asks": [(101.0, 2, "order3")]
        }
        self.assertEqual(reconcile(order_books), expected)
    
    def test_duplicate_orders_across_books(self):
        # Test that duplicate orders with identical values are merged correctly.
        order_books = [
            {
                "bids": [(99.0, 3, "order1")],
                "asks": [(102.0, 1, "order2")]
            },
            {
                "bids": [(99.0, 3, "order1")],
                "asks": [(102.0, 1, "order2")]
            }
        ]
        expected = {
            "bids": [(99.0, 3, "order1")],
            "asks": [(102.0, 1, "order2")]
        }
        self.assertEqual(reconcile(order_books), expected)

if __name__ == '__main__':
    unittest.main()