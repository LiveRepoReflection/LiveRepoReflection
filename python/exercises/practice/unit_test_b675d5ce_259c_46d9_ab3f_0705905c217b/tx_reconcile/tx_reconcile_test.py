import unittest
from decimal import Decimal
from tx_reconcile import reconcile_transactions

class TransactionReconcileTest(unittest.TestCase):
    def test_missing_transaction(self):
        expected = [
            {
                "transaction_id": "tx123",
                "timestamp": 1678886400,
                "amount": Decimal('100.00'),
                "currency": "USD",
                "source": "BankA",
                "type": "deposit"
            }
        ]
        observed = []
        time_window = 60
        amount_tolerance = Decimal('1.00')
        
        expected_discrepancies = [
            {
                "discrepancy_type": "Missing",
                "transaction_id": "tx123",
                "expected_record": expected[0],
                "observed_record": None,
                "details": "Transaction tx123 is missing in observed transactions"
            }
        ]
        
        discrepancies = reconcile_transactions(expected, observed, time_window, amount_tolerance)
        self.assertEqual(discrepancies, expected_discrepancies)

    def test_unexpected_transaction(self):
        expected = []
        observed = [
            {
                "transaction_id": "tx456",
                "timestamp": 1678886400,
                "amount": Decimal('50.00'),
                "currency": "EUR",
                "source": "BankB",
                "type": "withdrawal"
            }
        ]
        time_window = 60
        amount_tolerance = Decimal('1.00')
        
        expected_discrepancies = [
            {
                "discrepancy_type": "Unexpected",
                "transaction_id": "tx456",
                "expected_record": None,
                "observed_record": observed[0],
                "details": "Transaction tx456 is unexpected in observed transactions"
            }
        ]
        
        discrepancies = reconcile_transactions(expected, observed, time_window, amount_tolerance)
        self.assertEqual(discrepancies, expected_discrepancies)

    def test_amount_mismatch(self):
        expected = [
            {
                "transaction_id": "tx123",
                "timestamp": 1678886400,
                "amount": Decimal('100.00'),
                "currency": "USD",
                "source": "BankA",
                "type": "deposit"
            }
        ]
        observed = [
            {
                "transaction_id": "tx123",
                "timestamp": 1678886410,  # 10 seconds difference
                "amount": Decimal('97.00'),  # 3.00 difference (beyond tolerance)
                "currency": "USD",
                "source": "BankA",
                "type": "deposit"
            }
        ]
        time_window = 60
        amount_tolerance = Decimal('1.00')
        
        expected_discrepancies = [
            {
                "discrepancy_type": "AmountMismatch",
                "transaction_id": "tx123",
                "expected_record": expected[0],
                "observed_record": observed[0],
                "details": "Expected amount: 100.00, Observed amount: 97.00"
            }
        ]
        
        discrepancies = reconcile_transactions(expected, observed, time_window, amount_tolerance)
        self.assertEqual(discrepancies, expected_discrepancies)

    def test_amount_within_tolerance(self):
        expected = [
            {
                "transaction_id": "tx123",
                "timestamp": 1678886400,
                "amount": Decimal('100.00'),
                "currency": "USD",
                "source": "BankA",
                "type": "deposit"
            }
        ]
        observed = [
            {
                "transaction_id": "tx123",
                "timestamp": 1678886410,  # 10 seconds difference
                "amount": Decimal('99.50'),  # 0.50 difference (within tolerance)
                "currency": "USD",
                "source": "BankA",
                "type": "deposit"
            }
        ]
        time_window = 60
        amount_tolerance = Decimal('1.00')
        
        expected_discrepancies = []  # No discrepancies, within tolerance
        
        discrepancies = reconcile_transactions(expected, observed, time_window, amount_tolerance)
        self.assertEqual(discrepancies, expected_discrepancies)

    def test_currency_mismatch(self):
        expected = [
            {
                "transaction_id": "tx123",
                "timestamp": 1678886400,
                "amount": Decimal('100.00'),
                "currency": "USD",
                "source": "BankA",
                "type": "deposit"
            }
        ]
        observed = [
            {
                "transaction_id": "tx123",
                "timestamp": 1678886410,  # 10 seconds difference
                "amount": Decimal('100.00'),
                "currency": "EUR",  # Currency mismatch
                "source": "BankA",
                "type": "deposit"
            }
        ]
        time_window = 60
        amount_tolerance = Decimal('1.00')
        
        expected_discrepancies = [
            {
                "discrepancy_type": "CurrencyMismatch",
                "transaction_id": "tx123",
                "expected_record": expected[0],
                "observed_record": observed[0],
                "details": "Expected currency: USD, Observed currency: EUR"
            }
        ]
        
        discrepancies = reconcile_transactions(expected, observed, time_window, amount_tolerance)
        self.assertEqual(discrepancies, expected_discrepancies)

    def test_type_mismatch(self):
        expected = [
            {
                "transaction_id": "tx123",
                "timestamp": 1678886400,
                "amount": Decimal('100.00'),
                "currency": "USD",
                "source": "BankA",
                "type": "deposit"
            }
        ]
        observed = [
            {
                "transaction_id": "tx123",
                "timestamp": 1678886410,  # 10 seconds difference
                "amount": Decimal('100.00'),
                "currency": "USD",
                "source": "BankA",
                "type": "withdrawal"  # Type mismatch
            }
        ]
        time_window = 60
        amount_tolerance = Decimal('1.00')
        
        expected_discrepancies = [
            {
                "discrepancy_type": "TypeMismatch",
                "transaction_id": "tx123",
                "expected_record": expected[0],
                "observed_record": observed[0],
                "details": "Expected type: deposit, Observed type: withdrawal"
            }
        ]
        
        discrepancies = reconcile_transactions(expected, observed, time_window, amount_tolerance)
        self.assertEqual(discrepancies, expected_discrepancies)

    def test_out_of_time_window(self):
        expected = [
            {
                "transaction_id": "tx123",
                "timestamp": 1678886400,
                "amount": Decimal('100.00'),
                "currency": "USD",
                "source": "BankA",
                "type": "deposit"
            }
        ]
        observed = [
            {
                "transaction_id": "tx123",
                "timestamp": 1678886500,  # 100 seconds difference, beyond time window
                "amount": Decimal('100.00'),
                "currency": "USD",
                "source": "BankA",
                "type": "deposit"
            }
        ]
        time_window = 60  # 60 seconds
        amount_tolerance = Decimal('1.00')
        
        expected_discrepancies = [
            {
                "discrepancy_type": "Missing",
                "transaction_id": "tx123",
                "expected_record": expected[0],
                "observed_record": None,
                "details": "Transaction tx123 is missing in observed transactions"
            },
            {
                "discrepancy_type": "Unexpected",
                "transaction_id": "tx123",
                "expected_record": None,
                "observed_record": observed[0],
                "details": "Transaction tx123 is unexpected in observed transactions"
            }
        ]
        
        discrepancies = reconcile_transactions(expected, observed, time_window, amount_tolerance)
        self.assertEqual(len(discrepancies), 2)
        self.assertIn(expected_discrepancies[0], discrepancies)
        self.assertIn(expected_discrepancies[1], discrepancies)

    def test_multiple_discrepancies(self):
        expected = [
            {
                "transaction_id": "tx123",
                "timestamp": 1678886400,
                "amount": Decimal('100.00'),
                "currency": "USD",
                "source": "BankA",
                "type": "deposit"
            },
            {
                "transaction_id": "tx456",
                "timestamp": 1678886500,
                "amount": Decimal('200.00'),
                "currency": "EUR",
                "source": "BankB",
                "type": "withdrawal"
            }
        ]
        observed = [
            {
                "transaction_id": "tx123",
                "timestamp": 1678886410,  # 10 seconds difference
                "amount": Decimal('97.00'),  # Amount mismatch
                "currency": "USD",
                "source": "BankA",
                "type": "deposit"
            },
            {
                "transaction_id": "tx789",  # Unexpected transaction
                "timestamp": 1678886600,
                "amount": Decimal('300.00'),
                "currency": "GBP",
                "source": "BankC",
                "type": "payment"
            }
        ]
        time_window = 60
        amount_tolerance = Decimal('1.00')
        
        expected_discrepancies = [
            {
                "discrepancy_type": "AmountMismatch",
                "transaction_id": "tx123",
                "expected_record": expected[0],
                "observed_record": observed[0],
                "details": "Expected amount: 100.00, Observed amount: 97.00"
            },
            {
                "discrepancy_type": "Missing",
                "transaction_id": "tx456",
                "expected_record": expected[1],
                "observed_record": None,
                "details": "Transaction tx456 is missing in observed transactions"
            },
            {
                "discrepancy_type": "Unexpected",
                "transaction_id": "tx789",
                "expected_record": None,
                "observed_record": observed[1],
                "details": "Transaction tx789 is unexpected in observed transactions"
            }
        ]
        
        discrepancies = reconcile_transactions(expected, observed, time_window, amount_tolerance)
        self.assertEqual(len(discrepancies), 3)
        
        # Check each expected discrepancy is in the result
        for expected_disc in expected_discrepancies:
            matching = [d for d in discrepancies 
                      if d["discrepancy_type"] == expected_disc["discrepancy_type"] and 
                         d["transaction_id"] == expected_disc["transaction_id"]]
            self.assertEqual(len(matching), 1, f"Missing expected discrepancy: {expected_disc}")

    def test_large_dataset(self):
        # Generate large datasets
        expected = []
        observed = []
        
        # Create 1000 matching transactions
        for i in range(1000):
            tx_id = f"tx{i}"
            timestamp = 1678886400 + i
            expected.append({
                "transaction_id": tx_id,
                "timestamp": timestamp,
                "amount": Decimal('100.00'),
                "currency": "USD",
                "source": "BankA",
                "type": "deposit"
            })
            observed.append({
                "transaction_id": tx_id,
                "timestamp": timestamp + 5,  # Small time difference
                "amount": Decimal('100.00'),
                "currency": "USD",
                "source": "BankA",
                "type": "deposit"
            })
        
        # Add a few discrepancies
        expected.append({
            "transaction_id": "missing_tx",
            "timestamp": 1678896400,
            "amount": Decimal('500.00'),
            "currency": "USD",
            "source": "BankA",
            "type": "deposit"
        })
        
        observed.append({
            "transaction_id": "unexpected_tx",
            "timestamp": 1678897400,
            "amount": Decimal('600.00'),
            "currency": "EUR",
            "source": "BankB",
            "type": "withdrawal"
        })
        
        # Add one with amount mismatch
        expected.append({
            "transaction_id": "mismatch_tx",
            "timestamp": 1678898400,
            "amount": Decimal('700.00'),
            "currency": "USD",
            "source": "BankC",
            "type": "payment"
        })
        
        observed.append({
            "transaction_id": "mismatch_tx",
            "timestamp": 1678898420,
            "amount": Decimal('710.00'),  # Beyond tolerance
            "currency": "USD",
            "source": "BankC",
            "type": "payment"
        })
        
        time_window = 60
        amount_tolerance = Decimal('1.00')
        
        # Expected discrepancies
        discrepancies = reconcile_transactions(expected, observed, time_window, amount_tolerance)
        
        # We should have 3 discrepancies
        self.assertEqual(len(discrepancies), 3)
        
        # Check types of discrepancies
        discrepancy_types = [d["discrepancy_type"] for d in discrepancies]
        self.assertIn("Missing", discrepancy_types)
        self.assertIn("Unexpected", discrepancy_types)
        self.assertIn("AmountMismatch", discrepancy_types)

if __name__ == '__main__':
    unittest.main()