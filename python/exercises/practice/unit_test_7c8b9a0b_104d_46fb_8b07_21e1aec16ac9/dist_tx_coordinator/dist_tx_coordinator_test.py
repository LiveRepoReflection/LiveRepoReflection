import unittest
import threading
import time

from bank_service import BankService
from transaction_coordinator import TransactionCoordinator

# Dummy bank services for testing.
class DummyBankService(BankService):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.accounts = {}
        self.prepared_transactions = {}
        self.lock = threading.Lock()

    def deposit(self, account_id, amount):
        with self.lock:
            self.accounts[account_id] = self.accounts.get(account_id, 0) + amount

    def withdraw(self, account_id, amount):
        with self.lock:
            if self.accounts.get(account_id, 0) < amount:
                raise Exception("Insufficient funds")
            self.accounts[account_id] -= amount

    def get_balance(self, account_id):
        with self.lock:
            return self.accounts.get(account_id, 0)

    def prepare(self, transaction_id, operations):
        with self.lock:
            # Begin a new prepared transaction entry.
            self.prepared_transactions[transaction_id] = []
            for (account_id, amount, op_type) in operations:
                if op_type == "withdraw":
                    if self.accounts.get(account_id, 0) < amount:
                        del self.prepared_transactions[transaction_id]
                        return False
                    # Reserve funds (simulate by storing negative change)
                    self.prepared_transactions[transaction_id].append((account_id, -amount))
                elif op_type == "deposit":
                    self.prepared_transactions[transaction_id].append((account_id, amount))
                else:
                    del self.prepared_transactions[transaction_id]
                    return False
            return True

    def commit(self, transaction_id):
        with self.lock:
            if transaction_id in self.prepared_transactions:
                for (account_id, change) in self.prepared_transactions[transaction_id]:
                    self.accounts[account_id] = self.accounts.get(account_id, 0) + change
                del self.prepared_transactions[transaction_id]
            # Idempotency is maintained: if not found, do nothing.

    def rollback(self, transaction_id):
        with self.lock:
            if transaction_id in self.prepared_transactions:
                del self.prepared_transactions[transaction_id]
            # Idempotency: repeated rollback is safe.

# A delayed bank service to simulate timeout scenarios.
class DelayedBankService(DummyBankService):
    def prepare(self, transaction_id, operations):
        time.sleep(1.5)  # Delay longer than the expected timeout (assumed 1 second)
        return super().prepare(transaction_id, operations)

# Global bank services registry for testing.
bank_services = {
    "A": DummyBankService("A"),
    "B": DummyBankService("B")
}

# Dummy implementation of get_bank_service used by the coordinator.
def get_bank_service(account_id):
    # For testing, accounts starting with "A" use bank_service "A", others use "B".
    if account_id.startswith("A"):
        return bank_services["A"]
    else:
        return bank_services["B"]

# Monkey-patch the get_bank_service function in the transaction_coordinator module.
import transaction_coordinator
transaction_coordinator.get_bank_service = get_bank_service

class TestDistTxCoordinator(unittest.TestCase):
    def setUp(self):
        # Reset bank services state.
        for svc in bank_services.values():
            svc.accounts.clear()
            svc.prepared_transactions.clear()
        self.coordinator = TransactionCoordinator()
        # Initialize accounts with starting balances.
        bank_services["A"].accounts["A1"] = 1000
        bank_services["B"].accounts["B1"] = 500

    def test_successful_transfer(self):
        # Test a successful transfer of 200 from A1 to B1.
        self.coordinator.begin_transaction()
        self.coordinator.transfer("A1", "B1", 200)
        status = self.coordinator.end_transaction()
        self.assertEqual(status, "committed")
        self.assertEqual(bank_services["A"].get_balance("A1"), 800)
        self.assertEqual(bank_services["B"].get_balance("B1"), 700)

    def test_insufficient_funds(self):
        # Attempt to transfer 1100 from A1 (insufficient funds) to B1.
        self.coordinator.begin_transaction()
        self.coordinator.transfer("A1", "B1", 1100)
        status = self.coordinator.end_transaction()
        self.assertEqual(status, "aborted")
        # Verify that account balances remain unchanged.
        self.assertEqual(bank_services["A"].get_balance("A1"), 1000)
        self.assertEqual(bank_services["B"].get_balance("B1"), 500)

    def test_concurrent_transfers(self):
        # Test concurrent transfers running in parallel.
        results = []

        def transfer_A_to_B():
            tc = TransactionCoordinator()
            tc.begin_transaction()
            tc.transfer("A1", "B1", 300)
            res = tc.end_transaction()
            results.append(res)

        def transfer_B_to_A():
            tc = TransactionCoordinator()
            tc.begin_transaction()
            tc.transfer("B1", "A1", 400)
            res = tc.end_transaction()
            results.append(res)

        t1 = threading.Thread(target=transfer_A_to_B)
        t2 = threading.Thread(target=transfer_B_to_A)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Determine final balances.
        balance_A = bank_services["A"].get_balance("A1")
        balance_B = bank_services["B"].get_balance("B1")
        # Possible outcomes:
        # If both transactions commit: A1 = 1000 -300 +400, B1 = 500 +300 -400
        # If one aborts due to conflict/insufficient funds: balances remain closer to initial.
        possible_outcomes = [(1100, 400), (700, 800), (1000, 500)]
        self.assertIn((balance_A, balance_B), possible_outcomes)
        # Ensure at least one transaction succeeded.
        self.assertIn("committed", results)

    def test_timeout_abort(self):
        # Replace bank service for account A1 with a delayed version to simulate timeout.
        original_service = bank_services["A"]
        bank_services["A"] = DelayedBankService("A_delayed")
        bank_services["A"].accounts["A1"] = 1000
        self.coordinator.begin_transaction()
        self.coordinator.transfer("A1", "B1", 100)
        status = self.coordinator.end_transaction()
        self.assertEqual(status, "aborted")
        self.assertEqual(bank_services["A"].get_balance("A1"), 1000)
        self.assertEqual(bank_services["B"].get_balance("B1"), 500)
        # Restore original service.
        bank_services["A"] = original_service

    def test_idempotent_commit_and_rollback(self):
        # Test that repeated commits and rollbacks do not affect state.
        self.coordinator.begin_transaction()
        self.coordinator.transfer("A1", "B1", 50)
        tx_id = self.coordinator.current_transaction_id
        status = self.coordinator.end_transaction()
        # Invoke commit and rollback manually multiple times.
        for svc in bank_services.values():
            svc.commit(tx_id)
            svc.commit(tx_id)
            svc.rollback(tx_id)
            svc.rollback(tx_id)
        if status == "committed":
            self.assertEqual(bank_services["A"].get_balance("A1"), 950)
            self.assertEqual(bank_services["B"].get_balance("B1"), 550)
        else:
            self.assertEqual(bank_services["A"].get_balance("A1"), 1000)
            self.assertEqual(bank_services["B"].get_balance("B1"), 500)

if __name__ == "__main__":
    unittest.main()