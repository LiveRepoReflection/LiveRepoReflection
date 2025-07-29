import threading

class BankService:
    def __init__(self):
        self.accounts = {}
        self._prepared_transactions = {}
        self._lock = threading.Lock()

    def deposit(self, account_id, amount):
        with self._lock:
            self.accounts[account_id] = self.accounts.get(account_id, 0) + amount

    def withdraw(self, account_id, amount):
        with self._lock:
            if self.accounts.get(account_id, 0) < amount:
                raise Exception("Insufficient funds")
            self.accounts[account_id] -= amount

    def get_balance(self, account_id):
        with self._lock:
            return self.accounts.get(account_id, 0)

    def prepare(self, transaction_id, operations):
        with self._lock:
            if transaction_id in self._prepared_transactions:
                # Already prepared: idempotency
                return True
            # Validate that all withdraw operations have sufficient funds.
            for (account_id, amount, op_type) in operations:
                if op_type == "withdraw":
                    if self.accounts.get(account_id, 0) < amount:
                        return False
                elif op_type == "deposit":
                    continue
                else:
                    return False
            # Reserve the operations for this transaction.
            self._prepared_transactions[transaction_id] = operations.copy()
            return True

    def commit(self, transaction_id):
        with self._lock:
            if transaction_id in self._prepared_transactions:
                operations = self._prepared_transactions.pop(transaction_id)
                for (account_id, amount, op_type) in operations:
                    if op_type == "withdraw":
                        self.accounts[account_id] -= amount
                    elif op_type == "deposit":
                        self.accounts[account_id] += amount

    def rollback(self, transaction_id):
        with self._lock:
            if transaction_id in self._prepared_transactions:
                self._prepared_transactions.pop(transaction_id)