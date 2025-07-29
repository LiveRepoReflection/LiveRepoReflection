import unittest
from transaction_graph.transaction_system import TransactionSystem

class TestTransactionGraph(unittest.TestCase):
    def setUp(self):
        self.system = TransactionSystem()

    def test_simple_dependency_chain(self):
        self.system.add_transaction(1, [])
        self.system.add_transaction(2, [1])
        self.system.add_transaction(3, [2])
        
        self.assertEqual(self.system.get_ready_transactions(), [1])
        self.system.mark_transaction_failed(1)
        self.assertEqual(self.system.get_blocked_transactions(), [2, 3])

    def test_circular_dependency_detection(self):
        self.system.add_transaction(1, [2])
        with self.assertRaises(Exception):
            self.system.add_transaction(2, [1])

    def test_multiple_independent_chains(self):
        self.system.add_transaction(1, [])
        self.system.add_transaction(2, [])
        self.system.add_transaction(3, [1])
        self.system.add_transaction(4, [2])
        
        ready = self.system.get_ready_transactions()
        self.assertCountEqual(ready, [1, 2])

    def test_complex_dependency_graph(self):
        self.system.add_transaction(1, [])
        self.system.add_transaction(2, [1])
        self.system.add_transaction(3, [1])
        self.system.add_transaction(4, [2, 3])
        self.system.add_transaction(5, [4])
        
        self.assertEqual(self.system.get_ready_transactions(), [1])
        self.system.mark_transaction_failed(3)
        self.assertCountEqual(self.system.get_blocked_transactions(), [4, 5])

    def test_large_number_of_transactions(self):
        for i in range(1, 1001):
            self.system.add_transaction(i, [i-1] if i > 1 else [])
        
        self.assertEqual(self.system.get_ready_transactions(), [1])
        self.system.mark_transaction_failed(500)
        blocked = self.system.get_blocked_transactions()
        self.assertEqual(len(blocked), 500)
        self.assertTrue(all(x >= 500 for x in blocked))

    def test_concurrent_operations(self):
        import threading
        
        def add_transactions():
            for i in range(1, 101):
                self.system.add_transaction(i, [i-1] if i > 1 else [])
        
        threads = []
        for _ in range(10):
            t = threading.Thread(target=add_transactions)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        self.assertEqual(len(self.system.get_ready_transactions()), 1)

if __name__ == '__main__':
    unittest.main()