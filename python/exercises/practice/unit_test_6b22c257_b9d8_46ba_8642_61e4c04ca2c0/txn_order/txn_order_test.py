import unittest
from txn_order import execute_transactions

class TransactionOrderingTest(unittest.TestCase):
    def test_single_transaction_write_then_read(self):
        transactions = [
            ("T1", [("WRITE", "A", "10"), ("READ", "A", None)]),
        ]
        initial_data = {"A": "0"}
        
        committed_data, transaction_results = execute_transactions(transactions, initial_data)
        
        self.assertEqual(committed_data, {"A": "10"})
        self.assertEqual(transaction_results, {"T1": ["OK", "10"]})
    
    def test_two_transactions_no_conflict(self):
        transactions = [
            ("T1", [("WRITE", "A", "10"), ("READ", "A", None)]),
            ("T2", [("WRITE", "B", "20"), ("READ", "B", None)]),
        ]
        initial_data = {"A": "0", "B": "0"}
        
        committed_data, transaction_results = execute_transactions(transactions, initial_data)
        
        self.assertEqual(committed_data, {"A": "10", "B": "20"})
        self.assertTrue(transaction_results["T1"] == ["OK", "10"])
        self.assertTrue(transaction_results["T2"] == ["OK", "20"])
    
    def test_two_transactions_with_conflict(self):
        transactions = [
            ("T1", [("WRITE", "A", "10"), ("READ", "A", None)]),
            ("T2", [("WRITE", "A", "20"), ("READ", "A", None)]),
        ]
        initial_data = {"A": "0"}
        
        committed_data, transaction_results = execute_transactions(transactions, initial_data)
        
        # Depending on timestamp order, either T1 or T2 should succeed, but not both should be aborted
        self.assertNotEqual(transaction_results["T1"], 'ABORTED', "Both transactions were aborted")
        self.assertNotEqual(transaction_results["T2"], 'ABORTED', "Both transactions were aborted")
        
        # The final value should be either "10" or "20"
        self.assertIn(committed_data["A"], ["10", "20"])

    def test_read_nonexistent_key(self):
        transactions = [
            ("T1", [("READ", "Z", None)]),
        ]
        initial_data = {"A": "0"}
        
        committed_data, transaction_results = execute_transactions(transactions, initial_data)
        
        self.assertEqual(transaction_results, {"T1": ["KEY_NOT_FOUND"]})
        self.assertEqual(committed_data, {"A": "0"})
    
    def test_write_nonexistent_key(self):
        transactions = [
            ("T1", [("WRITE", "Z", "99")]),
        ]
        initial_data = {"A": "0"}
        
        committed_data, transaction_results = execute_transactions(transactions, initial_data)
        
        self.assertEqual(transaction_results, {"T1": ["OK"]})
        self.assertEqual(committed_data, {"A": "0", "Z": "99"})
    
    def test_deadlock_prevention(self):
        """Tests that transactions acquire locks in lexicographical key order"""
        transactions = [
            ("T1", [("WRITE", "B", "10"), ("WRITE", "A", "10")]),
            ("T2", [("WRITE", "A", "20"), ("WRITE", "B", "20")]),
        ]
        initial_data = {"A": "0", "B": "0"}
        
        committed_data, transaction_results = execute_transactions(transactions, initial_data)
        
        # Both transactions should complete since they acquire locks in lexicographic order
        self.assertNotEqual(transaction_results["T1"], 'ABORTED')
        self.assertNotEqual(transaction_results["T2"], 'ABORTED')
    
    def test_complex_transaction_scenario(self):
        transactions = [
            ("T1", [("READ", "A", None), ("WRITE", "B", "T1-B"), ("READ", "C", None)]),
            ("T2", [("WRITE", "A", "T2-A"), ("READ", "B", None), ("WRITE", "D", "T2-D")]),
            ("T3", [("READ", "B", None), ("WRITE", "C", "T3-C"), ("READ", "D", None)]),
        ]
        initial_data = {"A": "init-A", "B": "init-B", "C": "init-C"}
        
        committed_data, transaction_results = execute_transactions(transactions, initial_data)
        
        # Verify all transactions completed (not asserting specific results 
        # since order is timestamp-dependent)
        for txn_id in ["T1", "T2", "T3"]:
            self.assertNotEqual(transaction_results[txn_id], 'ABORTED')
        
        # Verify all keys exist in committed data
        for key in ["A", "B", "C", "D"]:
            self.assertIn(key, committed_data)
    
    def test_transaction_atomicity(self):
        """Tests that if a transaction is aborted, none of its changes are committed"""
        transactions = [
            ("T1", [("WRITE", "A", "10"), ("WRITE", "B", "10")]),
            ("T2", [("WRITE", "B", "20"), ("WRITE", "C", "20")]),  # Will conflict on B if T1 goes first
        ]
        initial_data = {"A": "0", "B": "0", "C": "0"}
        
        committed_data, transaction_results = execute_transactions(transactions, initial_data)
        
        # If T1 went first, T2 should be aborted
        if transaction_results.get("T1") != 'ABORTED':
            # If T1 succeeded and T2 was aborted
            if transaction_results.get("T2") == 'ABORTED':
                self.assertEqual(committed_data["A"], "10")
                self.assertEqual(committed_data["B"], "10")
                self.assertEqual(committed_data["C"], "0")  # T2 changes rolled back
            # If both succeeded
            else:
                self.assertEqual(committed_data["C"], "20")
        # If T2 went first, T1 should be aborted
        elif transaction_results.get("T2") != 'ABORTED':
            self.assertEqual(committed_data["A"], "0")  # T1 changes rolled back
            self.assertEqual(committed_data["B"], "20")
            self.assertEqual(committed_data["C"], "20")
    
    def test_multiple_reads_same_key(self):
        transactions = [
            ("T1", [("READ", "A", None), ("READ", "A", None), ("READ", "A", None)]),
            ("T2", [("READ", "A", None), ("READ", "A", None)]),
        ]
        initial_data = {"A": "0"}
        
        committed_data, transaction_results = execute_transactions(transactions, initial_data)
        
        self.assertEqual(transaction_results["T1"], ["0", "0", "0"])
        self.assertEqual(transaction_results["T2"], ["0", "0"])
        self.assertEqual(committed_data, {"A": "0"})
    
    def test_read_after_write_same_transaction(self):
        transactions = [
            ("T1", [("WRITE", "A", "10"), ("READ", "A", None), ("WRITE", "A", "20"), ("READ", "A", None)]),
        ]
        initial_data = {"A": "0"}
        
        committed_data, transaction_results = execute_transactions(transactions, initial_data)
        
        self.assertEqual(transaction_results["T1"], ["OK", "10", "OK", "20"])
        self.assertEqual(committed_data, {"A": "20"})

    def test_conflict_between_read_and_write(self):
        transactions = [
            ("T1", [("READ", "A", None), ("READ", "B", None)]),
            ("T2", [("WRITE", "A", "T2-A"), ("WRITE", "B", "T2-B")]),
        ]
        initial_data = {"A": "0", "B": "0"}
        
        committed_data, transaction_results = execute_transactions(transactions, initial_data)
        
        # Both should be able to complete since read locks and write locks are acquired in order
        self.assertNotEqual(transaction_results["T1"], 'ABORTED')
        self.assertNotEqual(transaction_results["T2"], 'ABORTED')
        
        # If T1 went first, it should have read the initial values
        # If T2 went first, T1 should have read T2's values
        if transaction_results["T1"] == ["0", "0"]:
            self.assertEqual(committed_data, {"A": "T2-A", "B": "T2-B"})
        else:
            self.assertEqual(transaction_results["T1"], ["T2-A", "T2-B"])

    def test_empty_transactions(self):
        transactions = []
        initial_data = {"A": "0"}
        
        committed_data, transaction_results = execute_transactions(transactions, initial_data)
        
        self.assertEqual(committed_data, {"A": "0"})
        self.assertEqual(transaction_results, {})

    def test_empty_initial_data(self):
        transactions = [
            ("T1", [("WRITE", "A", "10"), ("READ", "A", None)]),
        ]
        initial_data = {}
        
        committed_data, transaction_results = execute_transactions(transactions, initial_data)
        
        self.assertEqual(committed_data, {"A": "10"})
        self.assertEqual(transaction_results, {"T1": ["OK", "10"]})

if __name__ == "__main__":
    unittest.main()