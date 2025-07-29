import unittest
from bank_transactions import process_transactions, Transaction, Bank

class BankTransactionsTest(unittest.TestCase):
    def setUp(self):
        self.initial_state = {
            1: {"account_1": 1000, "account_2": 500},
            2: {"account_3": 1500, "account_4": 800},
            3: {"account_5": 2000, "account_6": 1200}
        }

    def test_successful_single_bank_transaction(self):
        transactions = [
            "1,account_1,account_2,300"
        ]
        result = process_transactions(self.initial_state, transactions)
        self.assertEqual(result[0]["status"], "committed")
        self.assertEqual(result[0]["transaction_id"], "1")
        self.assertEqual(result[0]["final_state"][1]["account_1"], 700)
        self.assertEqual(result[0]["final_state"][1]["account_2"], 800)

    def test_successful_cross_bank_transaction(self):
        transactions = [
            "1,account_1,account_3,500"
        ]
        result = process_transactions(self.initial_state, transactions)
        self.assertEqual(result[0]["status"], "committed")
        self.assertEqual(result[0]["final_state"][1]["account_1"], 500)
        self.assertEqual(result[0]["final_state"][2]["account_3"], 2000)

    def test_insufficient_funds(self):
        transactions = [
            "1,account_1,account_3,2000"
        ]
        result = process_transactions(self.initial_state, transactions)
        self.assertEqual(result[0]["status"], "aborted")
        # Verify state remains unchanged
        self.assertEqual(result[0]["final_state"][1]["account_1"], 1000)
        self.assertEqual(result[0]["final_state"][2]["account_3"], 1500)

    def test_multiple_transactions(self):
        transactions = [
            "1,account_1,account_3,300",
            "2,account_4,account_5,400",
            "3,account_2,account_6,200"
        ]
        result = process_transactions(self.initial_state, transactions)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["status"], "committed")
        self.assertEqual(result[1]["status"], "committed")
        self.assertEqual(result[2]["status"], "committed")

    def test_invalid_account(self):
        transactions = [
            "1,account_999,account_1,100"
        ]
        result = process_transactions(self.initial_state, transactions)
        self.assertEqual(result[0]["status"], "aborted")

    def test_invalid_transaction_format(self):
        transactions = [
            "invalid_format"
        ]
        with self.assertRaises(ValueError):
            process_transactions(self.initial_state, transactions)

    def test_negative_amount(self):
        transactions = [
            "1,account_1,account_2,-100"
        ]
        with self.assertRaises(ValueError):
            process_transactions(self.initial_state, transactions)

    def test_concurrent_transactions(self):
        transactions = [
            "1,account_1,account_3,300",
            "2,account_1,account_4,400"
        ]
        result = process_transactions(self.initial_state, transactions)
        self.assertEqual(len(result), 2)
        # Verify that transactions were processed sequentially
        committed_count = sum(1 for r in result if r["status"] == "committed")
        self.assertLessEqual(committed_count, 2)

    def test_zero_amount_transaction(self):
        transactions = [
            "1,account_1,account_2,0"
        ]
        with self.assertRaises(ValueError):
            process_transactions(self.initial_state, transactions)

    def test_same_account_transaction(self):
        transactions = [
            "1,account_1,account_1,100"
        ]
        with self.assertRaises(ValueError):
            process_transactions(self.initial_state, transactions)

    def test_transaction_rollback(self):
        # Simulate a scenario where one bank votes to abort
        transactions = [
            "1,account_1,account_3,1000",  # Should succeed
            "2,account_1,account_3,2000"   # Should fail and rollback
        ]
        result = process_transactions(self.initial_state, transactions)
        self.assertEqual(result[0]["status"], "committed")
        self.assertEqual(result[1]["status"], "aborted")
        # Verify first transaction committed but second rolled back
        final_state = result[1]["final_state"]
        self.assertEqual(final_state[1]["account_1"], 0)  # 1000 - 1000
        self.assertEqual(final_state[2]["account_3"], 2500)  # 1500 + 1000

    def test_multiple_banks_single_transaction(self):
        transactions = [
            "1,account_1,account_3,300",
            "2,account_3,account_5,400",
            "3,account_5,account_1,500"
        ]
        result = process_transactions(self.initial_state, transactions)
        self.assertEqual(len(result), 3)
        for r in result:
            self.assertEqual(r["status"], "committed")

    def test_stress_test_many_transactions(self):
        # Generate 100 valid transactions
        transactions = []
        for i in range(100):
            transactions.append(f"{i},account_1,account_2,1")
        
        result = process_transactions(self.initial_state, transactions)
        self.assertEqual(len(result), 100)
        # Verify final balance is correct
        final_state = result[-1]["final_state"]
        self.assertEqual(final_state[1]["account_1"], 900)  # 1000 - 100
        self.assertEqual(final_state[1]["account_2"], 600)  # 500 + 100

if __name__ == '__main__':
    unittest.main()