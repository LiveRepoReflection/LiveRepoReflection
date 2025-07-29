import unittest
from transaction_ordering import TransactionOrderingService

class TestTransactionOrderingService(unittest.TestCase):
    def setUp(self):
        self.service = TransactionOrderingService()

    def test_single_resource_ordering(self):
        transactions = [
            ("client1", "tx1", "resourceA", "write"),
            ("client1", "tx2", "resourceA", "read"),
            ("client2", "tx1", "resourceA", "write")
        ]
        for tx in transactions:
            self.service.add_transaction(*tx)
        
        expected = [
            ("client1", "tx1", "resourceA", "write"),
            ("client1", "tx2", "resourceA", "read"),
            ("client2", "tx1", "resourceA", "write")
        ]
        self.assertEqual(self.service.get_ordered_transactions("resourceA"), expected)

    def test_multiple_resources_independent_ordering(self):
        transactions = [
            ("client1", "tx1", "resourceA", "write"),
            ("client2", "tx1", "resourceB", "read"),
            ("client1", "tx2", "resourceA", "read"),
            ("client3", "tx1", "resourceA", "write"),
            ("client2", "tx2", "resourceB", "write")
        ]
        for tx in transactions:
            self.service.add_transaction(*tx)
        
        expected_a = [
            ("client1", "tx1", "resourceA", "write"),
            ("client1", "tx2", "resourceA", "read"),
            ("client3", "tx1", "resourceA", "write")
        ]
        expected_b = [
            ("client2", "tx1", "resourceB", "read"),
            ("client2", "tx2", "resourceB", "write")
        ]
        self.assertEqual(self.service.get_ordered_transactions("resourceA"), expected_a)
        self.assertEqual(self.service.get_ordered_transactions("resourceB"), expected_b)

    def test_out_of_order_submissions(self):
        transactions = [
            ("client1", "tx2", "resourceA", "read"),
            ("client1", "tx1", "resourceA", "write"),
            ("client2", "tx1", "resourceA", "update")
        ]
        for tx in transactions:
            self.service.add_transaction(*tx)
        
        expected = [
            ("client1", "tx2", "resourceA", "read"),
            ("client1", "tx1", "resourceA", "write"),
            ("client2", "tx1", "resourceA", "update")
        ]
        self.assertEqual(self.service.get_ordered_transactions("resourceA"), expected)

    def test_empty_resource(self):
        self.assertEqual(self.service.get_ordered_transactions("nonexistent"), [])

    def test_concurrent_access(self):
        import threading
        
        transactions_a = [
            ("client1", "tx1", "resourceA", "write"),
            ("client1", "tx2", "resourceA", "read")
        ]
        transactions_b = [
            ("client2", "tx1", "resourceB", "read"),
            ("client2", "tx2", "resourceB", "write")
        ]
        
        def add_transactions(transactions):
            for tx in transactions:
                self.service.add_transaction(*tx)
        
        thread_a = threading.Thread(target=add_transactions, args=(transactions_a,))
        thread_b = threading.Thread(target=add_transactions, args=(transactions_b,))
        
        thread_a.start()
        thread_b.start()
        thread_a.join()
        thread_b.join()
        
        expected_a = [
            ("client1", "tx1", "resourceA", "write"),
            ("client1", "tx2", "resourceA", "read")
        ]
        expected_b = [
            ("client2", "tx1", "resourceB", "read"),
            ("client2", "tx2", "resourceB", "write")
        ]
        
        result_a = self.service.get_ordered_transactions("resourceA")
        result_b = self.service.get_ordered_transactions("resourceB")
        
        self.assertEqual(sorted(result_a), sorted(expected_a))
        self.assertEqual(sorted(result_b), sorted(expected_b))

    def test_large_number_of_transactions(self):
        transactions = [("client1", f"tx{i}", "resourceA", "op") for i in range(1000)]
        for tx in transactions:
            self.service.add_transaction(*tx)
        
        self.assertEqual(len(self.service.get_ordered_transactions("resourceA")), 1000)

if __name__ == '__main__':
    unittest.main()