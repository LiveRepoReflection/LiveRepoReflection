import unittest
from txn_validator import validate_transactions

class TransactionValidatorTest(unittest.TestCase):
    def test_empty_batch(self):
        """Test with an empty batch of transactions."""
        transactions = []
        self.assertTrue(validate_transactions(transactions))

    def test_single_transaction(self):
        """Test with a single transaction."""
        transactions = [
            {
                "transaction_id": "a",
                "inputs": ["account1"],
                "outputs": ["account2"]
            }
        ]
        self.assertTrue(validate_transactions(transactions))

    def test_chain_of_transactions(self):
        """Test with a valid chain of transactions."""
        transactions = [
            {
                "transaction_id": "a",
                "inputs": ["account1"],
                "outputs": ["account2"]
            },
            {
                "transaction_id": "b",
                "inputs": ["account2"],
                "outputs": ["account3"]
            },
            {
                "transaction_id": "c",
                "inputs": ["account3"],
                "outputs": ["account4"]
            }
        ]
        self.assertTrue(validate_transactions(transactions))

    def test_independent_transactions(self):
        """Test with multiple independent transactions."""
        transactions = [
            {
                "transaction_id": "a",
                "inputs": ["account1"],
                "outputs": ["account2"]
            },
            {
                "transaction_id": "b",
                "inputs": ["account3"],
                "outputs": ["account4"]
            },
            {
                "transaction_id": "c",
                "inputs": ["account5"],
                "outputs": ["account6"]
            }
        ]
        self.assertTrue(validate_transactions(transactions))

    def test_double_spending(self):
        """Test with double spending (same input used multiple times)."""
        transactions = [
            {
                "transaction_id": "a",
                "inputs": ["account1"],
                "outputs": ["account2"]
            },
            {
                "transaction_id": "b",
                "inputs": ["account1"],
                "outputs": ["account3"]
            }
        ]
        self.assertFalse(validate_transactions(transactions))

    def test_cycle_in_transactions(self):
        """Test with a cycle in the transaction graph."""
        transactions = [
            {
                "transaction_id": "a",
                "inputs": ["account1"],
                "outputs": ["account2"]
            },
            {
                "transaction_id": "b",
                "inputs": ["account2"],
                "outputs": ["account3"]
            },
            {
                "transaction_id": "c",
                "inputs": ["account3"],
                "outputs": ["account2"]
            }
        ]
        self.assertFalse(validate_transactions(transactions))

    def test_complex_cycle(self):
        """Test with a complex cycle in the transaction graph."""
        transactions = [
            {
                "transaction_id": "a",
                "inputs": ["account1"],
                "outputs": ["account2"]
            },
            {
                "transaction_id": "b",
                "inputs": ["account2"],
                "outputs": ["account3", "account4"]
            },
            {
                "transaction_id": "c",
                "inputs": ["account4"],
                "outputs": ["account5"]
            },
            {
                "transaction_id": "d",
                "inputs": ["account5"],
                "outputs": ["account6"]
            },
            {
                "transaction_id": "e",
                "inputs": ["account6"],
                "outputs": ["account2"]
            }
        ]
        self.assertFalse(validate_transactions(transactions))

    def test_insufficient_funds(self):
        """Test with insufficient funds."""
        transactions = [
            {
                "transaction_id": "a",
                "inputs": ["account1"],
                "outputs": ["account2"]
            },
            {
                "transaction_id": "b",
                "inputs": ["account3"],
                "outputs": ["account1"]
            },
            {
                "transaction_id": "c",
                "inputs": ["account1", "account2"],
                "outputs": ["account4"]
            }
        ]
        self.assertFalse(validate_transactions(transactions))

    def test_valid_complex_transaction_flow(self):
        """Test with a complex but valid transaction flow."""
        transactions = [
            {
                "transaction_id": "a",
                "inputs": ["account1"],
                "outputs": ["account2", "account3"]
            },
            {
                "transaction_id": "b",
                "inputs": ["account4"],
                "outputs": ["account1"]
            },
            {
                "transaction_id": "c",
                "inputs": ["account2"],
                "outputs": ["account5"]
            },
            {
                "transaction_id": "d",
                "inputs": ["account5"],
                "outputs": ["account6"]
            }
        ]
        self.assertTrue(validate_transactions(transactions))

    def test_different_order_same_result(self):
        """Test that transactions can be processed in any order."""
        transactions1 = [
            {
                "transaction_id": "a",
                "inputs": ["account1"],
                "outputs": ["account2"]
            },
            {
                "transaction_id": "b",
                "inputs": ["account2"],
                "outputs": ["account3"]
            }
        ]
        
        transactions2 = [
            {
                "transaction_id": "b",
                "inputs": ["account2"],
                "outputs": ["account3"]
            },
            {
                "transaction_id": "a",
                "inputs": ["account1"],
                "outputs": ["account2"]
            }
        ]
        
        self.assertEqual(validate_transactions(transactions1), validate_transactions(transactions2))

    def test_multiple_outputs_and_inputs(self):
        """Test with multiple outputs and inputs."""
        transactions = [
            {
                "transaction_id": "a",
                "inputs": ["account1", "account2"],
                "outputs": ["account3", "account4", "account5"]
            },
            {
                "transaction_id": "b",
                "inputs": ["account3", "account6"],
                "outputs": ["account7", "account8"]
            }
        ]
        self.assertTrue(validate_transactions(transactions))

    def test_large_batch(self):
        """Test with a large batch of transactions."""
        # Create a large batch of valid transactions
        transactions = []
        for i in range(1000):
            transactions.append({
                "transaction_id": f"tx{i}",
                "inputs": [f"account{i}"],
                "outputs": [f"account{i+1}"]
            })
        self.assertTrue(validate_transactions(transactions))

    def test_complex_double_spending(self):
        """Test with complex double spending scenarios."""
        transactions = [
            {
                "transaction_id": "a",
                "inputs": ["account1"],
                "outputs": ["account2", "account3"]
            },
            {
                "transaction_id": "b",
                "inputs": ["account2"],
                "outputs": ["account4"]
            },
            {
                "transaction_id": "c",
                "inputs": ["account2"],  # Double spending of account2
                "outputs": ["account5"]
            }
        ]
        self.assertFalse(validate_transactions(transactions))

if __name__ == '__main__':
    unittest.main()