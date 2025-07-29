import unittest
from tx_validator import validate_global_transaction

class TxValidatorTest(unittest.TestCase):
    def test_valid_global_transaction(self):
        # Valid chain: A -> B -> C, all dependencies present,
        # account balance remains non-negative, and timestamps are in order.
        transactions = [
            {"transaction_id": "A", "account_id": "X", "amount": 100, "timestamp": 10, "dependencies": []},
            {"transaction_id": "B", "account_id": "X", "amount": -50, "timestamp": 20, "dependencies": ["A"]},
            {"transaction_id": "C", "account_id": "X", "amount": -30, "timestamp": 30, "dependencies": ["B"]},
            # Extra unrelated transaction (should be ignored)
            {"transaction_id": "D", "account_id": "Y", "amount": 200, "timestamp": 15, "dependencies": []}
        ]
        global_transaction_ids = ["C"]
        self.assertTrue(validate_global_transaction(transactions, global_transaction_ids))

    def test_missing_dependency(self):
        # Transaction B depends on A, but A is missing.
        transactions = [
            {"transaction_id": "B", "account_id": "X", "amount": -50, "timestamp": 20, "dependencies": ["A"]}
        ]
        global_transaction_ids = ["B"]
        self.assertFalse(validate_global_transaction(transactions, global_transaction_ids))

    def test_negative_account_balance(self):
        # Account balance goes negative at some timestamp.
        transactions = [
            {"transaction_id": "A", "account_id": "X", "amount": 50, "timestamp": 10, "dependencies": []},
            {"transaction_id": "B", "account_id": "X", "amount": -100, "timestamp": 20, "dependencies": ["A"]}
        ]
        global_transaction_ids = ["B"]
        self.assertFalse(validate_global_transaction(transactions, global_transaction_ids))

    def test_circular_dependency(self):
        # Circular dependency between A and B.
        transactions = [
            {"transaction_id": "A", "account_id": "X", "amount": 10, "timestamp": 10, "dependencies": ["B"]},
            {"transaction_id": "B", "account_id": "X", "amount": 10, "timestamp": 20, "dependencies": ["A"]}
        ]
        global_transaction_ids = ["A"]
        self.assertFalse(validate_global_transaction(transactions, global_transaction_ids))

    def test_timestamp_inconsistency(self):
        # B depends on A but has an earlier timestamp.
        transactions = [
            {"transaction_id": "A", "account_id": "X", "amount": 100, "timestamp": 20, "dependencies": []},
            {"transaction_id": "B", "account_id": "X", "amount": -50, "timestamp": 10, "dependencies": ["A"]}
        ]
        global_transaction_ids = ["B"]
        self.assertFalse(validate_global_transaction(transactions, global_transaction_ids))

    def test_nonexistent_global_transaction_id(self):
        # Global transaction ID not present in transactions.
        transactions = [
            {"transaction_id": "A", "account_id": "X", "amount": 100, "timestamp": 10, "dependencies": []}
        ]
        global_transaction_ids = ["Z"]
        self.assertFalse(validate_global_transaction(transactions, global_transaction_ids))
    
    def test_empty_inputs(self):
        # Both transactions and global_transaction_ids are empty.
        transactions = []
        global_transaction_ids = []
        self.assertFalse(validate_global_transaction(transactions, global_transaction_ids))
    
    def test_self_dependency(self):
        # Transaction depends on itself.
        transactions = [
            {"transaction_id": "A", "account_id": "X", "amount": 100, "timestamp": 10, "dependencies": ["A"]}
        ]
        global_transaction_ids = ["A"]
        self.assertFalse(validate_global_transaction(transactions, global_transaction_ids))
    
    def test_complex_dependency_graph(self):
        # Complex graph with multiple branches and shared dependencies.
        transactions = [
            {"transaction_id": "A", "account_id": "X", "amount": 200, "timestamp": 5, "dependencies": []},
            {"transaction_id": "B", "account_id": "X", "amount": -50, "timestamp": 10, "dependencies": ["A"]},
            {"transaction_id": "C", "account_id": "Y", "amount": 300, "timestamp": 8, "dependencies": []},
            {"transaction_id": "D", "account_id": "X", "amount": -100, "timestamp": 15, "dependencies": ["B", "C"]},
            {"transaction_id": "E", "account_id": "Z", "amount": 150, "timestamp": 12, "dependencies": []},
            {"transaction_id": "F", "account_id": "Z", "amount": -50, "timestamp": 20, "dependencies": ["E"]},
            {"transaction_id": "G", "account_id": "Y", "amount": -200, "timestamp": 18, "dependencies": ["C"]}
        ]
        global_transaction_ids = ["D", "F", "G"]
        # Expected to be valid: all dependencies exist, and account balances never go negative.
        self.assertTrue(validate_global_transaction(transactions, global_transaction_ids))
        
if __name__ == "__main__":
    unittest.main()