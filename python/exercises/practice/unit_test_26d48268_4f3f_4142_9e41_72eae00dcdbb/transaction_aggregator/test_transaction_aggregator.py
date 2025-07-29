import unittest
from time import time
from transaction_aggregator import TransactionAggregator

class TestTransactionAggregator(unittest.TestCase):
    def setUp(self):
        self.aggregator = TransactionAggregator()
        
    def test_empty_aggregator(self):
        # Test empty aggregator returns zeroes and empty lists
        now = int(time())
        self.assertEqual(self.aggregator.get_total_by_category("Electronics", now - 3600, now), 0)
        self.assertEqual(self.aggregator.get_top_users_by_category("Electronics", now - 3600, now, 5), [])
        
    def test_single_transaction(self):
        # Test with a single transaction
        transaction = {
            "transaction_id": "t1",
            "timestamp": 1000,
            "amount": 100.0,
            "category": "Electronics",
            "user_id": 1
        }
        
        self.aggregator.add_transaction(transaction)
        
        # Test exact time window
        self.assertEqual(self.aggregator.get_total_by_category("Electronics", 1000, 1000), 100.0)
        
        # Test wider time window
        self.assertEqual(self.aggregator.get_total_by_category("Electronics", 900, 1100), 100.0)
        
        # Test outside time window
        self.assertEqual(self.aggregator.get_total_by_category("Electronics", 1001, 1100), 0)
        
        # Test top users
        top_users = self.aggregator.get_top_users_by_category("Electronics", 900, 1100, 5)
        self.assertEqual(len(top_users), 1)
        self.assertEqual(top_users[0], (1, 100.0))
        
    def test_multiple_transactions_same_category(self):
        # Test with multiple transactions in the same category
        transactions = [
            {
                "transaction_id": "t1",
                "timestamp": 1000,
                "amount": 100.0,
                "category": "Electronics",
                "user_id": 1
            },
            {
                "transaction_id": "t2",
                "timestamp": 1200,
                "amount": 200.0,
                "category": "Electronics",
                "user_id": 2
            },
            {
                "transaction_id": "t3",
                "timestamp": 1400,
                "amount": 150.0,
                "category": "Electronics",
                "user_id": 1
            }
        ]
        
        for tx in transactions:
            self.aggregator.add_transaction(tx)
        
        # Test total for entire range
        self.assertEqual(self.aggregator.get_total_by_category("Electronics", 900, 1500), 450.0)
        
        # Test top users (user 1 has 250.0, user 2 has 200.0)
        top_users = self.aggregator.get_top_users_by_category("Electronics", 900, 1500, 5)
        self.assertEqual(len(top_users), 2)
        self.assertEqual(top_users[0], (1, 250.0))
        self.assertEqual(top_users[1], (2, 200.0))
        
        # Test with limited K
        top_users = self.aggregator.get_top_users_by_category("Electronics", 900, 1500, 1)
        self.assertEqual(len(top_users), 1)
        self.assertEqual(top_users[0], (1, 250.0))
        
    def test_multiple_categories(self):
        # Test with multiple categories
        transactions = [
            {
                "transaction_id": "t1",
                "timestamp": 1000,
                "amount": 100.0,
                "category": "Electronics",
                "user_id": 1
            },
            {
                "transaction_id": "t2",
                "timestamp": 1200,
                "amount": 200.0,
                "category": "Books",
                "user_id": 1
            },
            {
                "transaction_id": "t3",
                "timestamp": 1400,
                "amount": 150.0,
                "category": "Electronics",
                "user_id": 2
            }
        ]
        
        for tx in transactions:
            self.aggregator.add_transaction(tx)
        
        # Test totals for different categories
        self.assertEqual(self.aggregator.get_total_by_category("Electronics", 900, 1500), 250.0)
        self.assertEqual(self.aggregator.get_total_by_category("Books", 900, 1500), 200.0)
        self.assertEqual(self.aggregator.get_total_by_category("Clothing", 900, 1500), 0)
        
        # Test top users for different categories
        electronics_top_users = self.aggregator.get_top_users_by_category("Electronics", 900, 1500, 5)
        self.assertEqual(len(electronics_top_users), 2)
        self.assertEqual(electronics_top_users[0], (2, 150.0))
        self.assertEqual(electronics_top_users[1], (1, 100.0))
        
        books_top_users = self.aggregator.get_top_users_by_category("Books", 900, 1500, 5)
        self.assertEqual(len(books_top_users), 1)
        self.assertEqual(books_top_users[0], (1, 200.0))
        
    def test_large_time_window(self):
        # Test with transactions across a wide time range
        now = int(time())
        
        transactions = [
            {
                "transaction_id": "t1",
                "timestamp": now - 10000,
                "amount": 100.0,
                "category": "Electronics",
                "user_id": 1
            },
            {
                "transaction_id": "t2",
                "timestamp": now - 5000,
                "amount": 200.0,
                "category": "Electronics",
                "user_id": 2
            },
            {
                "transaction_id": "t3",
                "timestamp": now,
                "amount": 300.0,
                "category": "Electronics",
                "user_id": 3
            }
        ]
        
        for tx in transactions:
            self.aggregator.add_transaction(tx)
        
        # Test with full time range
        self.assertEqual(self.aggregator.get_total_by_category("Electronics", now - 15000, now + 5000), 600.0)
        
        # Test with partial time range
        self.assertEqual(self.aggregator.get_total_by_category("Electronics", now - 7500, now - 2500), 200.0)
        
    def test_out_of_order_transactions(self):
        # Test with transactions arriving out of order
        transactions = [
            {
                "transaction_id": "t2",
                "timestamp": 1200,
                "amount": 200.0,
                "category": "Electronics",
                "user_id": 2
            },
            {
                "transaction_id": "t3",
                "timestamp": 1400,
                "amount": 300.0,
                "category": "Electronics",
                "user_id": 3
            },
            {
                "transaction_id": "t1",
                "timestamp": 1000,
                "amount": 100.0,
                "category": "Electronics",
                "user_id": 1
            }
        ]
        
        for tx in transactions:
            self.aggregator.add_transaction(tx)
        
        # Verify all transactions are counted
        self.assertEqual(self.aggregator.get_total_by_category("Electronics", 900, 1500), 600.0)
        
        # Verify correct order of users
        top_users = self.aggregator.get_top_users_by_category("Electronics", 900, 1500, 5)
        self.assertEqual(len(top_users), 3)
        self.assertEqual(top_users[0], (3, 300.0))
        self.assertEqual(top_users[1], (2, 200.0))
        self.assertEqual(top_users[2], (1, 100.0))
        
    def test_identical_amounts(self):
        # Test with users having identical transaction amounts
        transactions = [
            {
                "transaction_id": "t1",
                "timestamp": 1000,
                "amount": 100.0,
                "category": "Electronics",
                "user_id": 1
            },
            {
                "transaction_id": "t2",
                "timestamp": 1200,
                "amount": 100.0,
                "category": "Electronics",
                "user_id": 2
            },
            {
                "transaction_id": "t3",
                "timestamp": 1400,
                "amount": 100.0,
                "category": "Electronics",
                "user_id": 3
            }
        ]
        
        for tx in transactions:
            self.aggregator.add_transaction(tx)
        
        # Check that all users have equal amounts but are still ordered
        top_users = self.aggregator.get_top_users_by_category("Electronics", 900, 1500, 5)
        self.assertEqual(len(top_users), 3)
        # The exact order might be implementation-dependent, but all should have 100.0
        self.assertEqual({amount for _, amount in top_users}, {100.0})
        self.assertEqual({user_id for user_id, _ in top_users}, {1, 2, 3})
        
    def test_edge_time_boundaries(self):
        # Test transactions exactly at time window boundaries
        transactions = [
            {
                "transaction_id": "t1",
                "timestamp": 1000,  # Exactly at start
                "amount": 100.0,
                "category": "Electronics",
                "user_id": 1
            },
            {
                "transaction_id": "t2",
                "timestamp": 2000,  # Exactly at end
                "amount": 200.0,
                "category": "Electronics",
                "user_id": 2
            }
        ]
        
        for tx in transactions:
            self.aggregator.add_transaction(tx)
        
        # Both transactions should be included (inclusive time window)
        self.assertEqual(self.aggregator.get_total_by_category("Electronics", 1000, 2000), 300.0)
        
        # Only first transaction should be included
        self.assertEqual(self.aggregator.get_total_by_category("Electronics", 1000, 1999), 100.0)
        
        # Only second transaction should be included
        self.assertEqual(self.aggregator.get_total_by_category("Electronics", 1001, 2000), 200.0)

if __name__ == '__main__':
    unittest.main()