import unittest
import copy
from bank_tx import coordinate_transaction

class BankTxTest(unittest.TestCase):
    def test_successful_transaction(self):
        bank_servers = [
            {101: 100, 102: 50},  # Server 0
            {201: 200, 202: 75}   # Server 1
        ]
        transaction = [
            (0, 101, -20),  # Withdraw 20 from account 101 on server 0
            (1, 201, 20)    # Deposit 20 to account 201 on server 1
        ]
        expected_servers = [
            {101: 80, 102: 50},
            {201: 220, 202: 75}
        ]
        result = coordinate_transaction(bank_servers, transaction)
        self.assertTrue(result)
        self.assertEqual(bank_servers, expected_servers)

    def test_insufficient_funds(self):
        bank_servers = [
            {101: 100},  # Server 0
            {201: 50}    # Server 1
        ]
        transaction = [
            (0, 101, -50),   # Valid withdrawal
            (1, 201, -60)    # Withdrawal causing negative balance on server 1
        ]
        original_servers = copy.deepcopy(bank_servers)
        result = coordinate_transaction(bank_servers, transaction)
        self.assertFalse(result)
        self.assertEqual(bank_servers, original_servers)

    def test_invalid_account(self):
        bank_servers = [
            {101: 100},  # Server 0
            {201: 200}   # Server 1
        ]
        transaction = [
            (0, 999, -10),  # Account 999 does not exist on server 0
            (1, 201, 10)
        ]
        original_servers = copy.deepcopy(bank_servers)
        result = coordinate_transaction(bank_servers, transaction)
        self.assertFalse(result)
        self.assertEqual(bank_servers, original_servers)

    def test_zero_amount_transaction(self):
        bank_servers = [
            {101: 100},
            {201: 200}
        ]
        transaction = [
            (0, 101, 0),   # Zero amount, valid operation
            (1, 201, 0)    # Zero amount, valid operation
        ]
        expected_servers = copy.deepcopy(bank_servers)
        result = coordinate_transaction(bank_servers, transaction)
        self.assertTrue(result)
        self.assertEqual(bank_servers, expected_servers)

    def test_multiple_operations_same_account(self):
        bank_servers = [
            {101: 100},
            {201: 200}
        ]
        transaction = [
            (0, 101, -30),
            (0, 101, 50),
            (1, 201, -100),
            (1, 201, 25)
        ]
        expected_servers = [
            {101: 120},  # 100 - 30 + 50
            {201: 125}   # 200 - 100 + 25
        ]
        result = coordinate_transaction(bank_servers, transaction)
        self.assertTrue(result)
        self.assertEqual(bank_servers, expected_servers)

    def test_negative_initial_balance(self):
        bank_servers = [
            {101: -10},    # Already negative
            {201: 5}
        ]
        # Withdrawing further from already negative account should fail
        transaction = [
            (0, 101, -5),
            (1, 201, 10)
        ]
        original_servers = copy.deepcopy(bank_servers)
        result = coordinate_transaction(bank_servers, transaction)
        self.assertFalse(result)
        self.assertEqual(bank_servers, original_servers)

    def test_atomicity_on_failure(self):
        bank_servers = [
            {101: 100},
            {201: 200}
        ]
        transaction = [
            (0, 101, -30),   # Valid operation: 100 -> 70
            (1, 201, -250)   # Invalid operation: 200 - 250 = -50 (failure)
        ]
        original_servers = copy.deepcopy(bank_servers)
        result = coordinate_transaction(bank_servers, transaction)
        self.assertFalse(result)
        self.assertEqual(bank_servers, original_servers)

    def test_large_transaction(self):
        # Create a larger test case with many operations
        # We simulate 100 servers each with 100 accounts
        num_servers = 100
        accounts_per_server = 100
        bank_servers = []
        for s in range(num_servers):
            server_accounts = {1000 + s * accounts_per_server + a: 1000 for a in range(accounts_per_server)}
            bank_servers.append(server_accounts)
        
        # Create a transaction that deposits 10 to every account and withdraws 5 from every account in an interleaved fashion
        transaction = []
        for s in range(num_servers):
            for a in range(accounts_per_server):
                account = 1000 + s * accounts_per_server + a
                transaction.append((s, account, 10))
                transaction.append((s, account, -5))
        
        # After transaction, every account should have an increase of +5 (1000 + 5)
        expected_servers = []
        for s in range(num_servers):
            server_accounts = {1000 + s * accounts_per_server + a: 1005 for a in range(accounts_per_server)}
            expected_servers.append(server_accounts)
        
        result = coordinate_transaction(bank_servers, transaction)
        self.assertTrue(result)
        self.assertEqual(bank_servers, expected_servers)

if __name__ == '__main__':
    unittest.main()