from dataclasses import dataclass
from typing import List, Dict, Any
import threading
from collections import defaultdict
import logging
from enum import Enum
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionStatus(Enum):
    PENDING = "pending"
    COMMITTED = "committed"
    ABORTED = "aborted"

@dataclass
class Transaction:
    id: str
    source_account: str
    destination_account: str
    amount: int

class BankError(Exception):
    pass

class InsufficientFundsError(BankError):
    pass

class AccountNotFoundError(BankError):
    pass

class Bank:
    def __init__(self, bank_id: int, initial_state: Dict[str, int]):
        self.bank_id = bank_id
        self.accounts = initial_state.copy()
        self.locks = defaultdict(threading.Lock)
        self.transaction_log = {}
        self.global_lock = threading.Lock()

    def acquire_locks(self, accounts: List[str]) -> bool:
        # Sort accounts to prevent deadlocks
        sorted_accounts = sorted(accounts)
        acquired_locks = []
        
        try:
            for account in sorted_accounts:
                if account in self.accounts:
                    if not self.locks[account].acquire(timeout=1.0):
                        raise TimeoutError("Failed to acquire lock")
                    acquired_locks.append(account)
            return True
        except TimeoutError:
            # Release any acquired locks
            for account in acquired_locks:
                self.locks[account].release()
            return False

    def release_locks(self, accounts: List[str]):
        for account in accounts:
            if account in self.accounts:
                self.locks[account].release()

    def prepare(self, transaction: Transaction) -> bool:
        with self.global_lock:
            # Check if accounts exist
            if (transaction.source_account in self.accounts and 
                self.accounts[transaction.source_account] < transaction.amount):
                return False

            # Log the prepared state
            self.transaction_log[transaction.id] = {
                "status": TransactionStatus.PENDING,
                "changes": {
                    transaction.source_account: -transaction.amount if transaction.source_account in self.accounts else 0,
                    transaction.destination_account: transaction.amount if transaction.destination_account in self.accounts else 0
                }
            }
            return True

    def commit(self, transaction: Transaction):
        with self.global_lock:
            if transaction.id not in self.transaction_log:
                return

            changes = self.transaction_log[transaction.id]["changes"]
            
            # Apply changes
            for account, amount in changes.items():
                if account in self.accounts:
                    self.accounts[account] += amount

            # Update transaction status
            self.transaction_log[transaction.id]["status"] = TransactionStatus.COMMITTED

    def rollback(self, transaction: Transaction):
        with self.global_lock:
            if transaction.id not in self.transaction_log:
                return
            self.transaction_log[transaction.id]["status"] = TransactionStatus.ABORTED

    def get_state(self) -> Dict[str, int]:
        return self.accounts.copy()

class TransactionCoordinator:
    def __init__(self, banks: Dict[int, Bank]):
        self.banks = banks

    def execute_transaction(self, transaction: Transaction) -> Dict[str, Any]:
        # Validate transaction
        if transaction.amount <= 0:
            raise ValueError("Transaction amount must be positive")
        
        if transaction.source_account == transaction.destination_account:
            raise ValueError("Source and destination accounts cannot be the same")

        # Find involved banks
        source_bank = None
        dest_bank = None
        for bank_id, bank in self.banks.items():
            if transaction.source_account in bank.accounts:
                source_bank = bank
            if transaction.destination_account in bank.accounts:
                dest_bank = bank

        if not source_bank:
            raise AccountNotFoundError(f"Source account {transaction.source_account} not found")
        if not dest_bank:
            raise AccountNotFoundError(f"Destination account {transaction.destination_account} not found")

        involved_banks = {source_bank, dest_bank}

        # Phase 1: Prepare
        try:
            # Acquire locks
            for bank in involved_banks:
                accounts = [acc for acc in [transaction.source_account, transaction.destination_account] 
                          if acc in bank.accounts]
                if not bank.acquire_locks(accounts):
                    raise BankError("Failed to acquire locks")

            # Prepare phase
            all_prepared = all(bank.prepare(transaction) for bank in involved_banks)

            if all_prepared:
                # Phase 2: Commit
                for bank in involved_banks:
                    bank.commit(transaction)
                status = "committed"
            else:
                # Phase 2: Rollback
                for bank in involved_banks:
                    bank.rollback(transaction)
                status = "aborted"

        finally:
            # Release locks
            for bank in involved_banks:
                accounts = [acc for acc in [transaction.source_account, transaction.destination_account] 
                          if acc in bank.accounts]
                bank.release_locks(accounts)

        # Prepare final state
        final_state = {bank_id: bank.get_state() for bank_id, bank in self.banks.items()}

        return {
            "transaction_id": transaction.id,
            "status": status,
            "final_state": final_state
        }

def process_transactions(initial_state: Dict[int, Dict[str, int]], transaction_strings: List[str]) -> List[Dict[str, Any]]:
    # Initialize banks
    banks = {bank_id: Bank(bank_id, accounts) for bank_id, accounts in initial_state.items()}
    coordinator = TransactionCoordinator(banks)
    results = []

    # Process each transaction
    for tx_str in transaction_strings:
        try:
            # Parse transaction
            parts = tx_str.split(',')
            if len(parts) != 4:
                raise ValueError(f"Invalid transaction format: {tx_str}")

            tx_id, source, dest, amount = parts
            amount = int(amount)

            transaction = Transaction(tx_id, source, dest, amount)
            result = coordinator.execute_transaction(transaction)
            results.append(result)

        except ValueError as e:
            raise ValueError(f"Invalid transaction format or amount: {str(e)}")
        except (BankError, AccountNotFoundError) as e:
            results.append({
                "transaction_id": tx_id,
                "status": "aborted",
                "final_state": {bank_id: bank.get_state() for bank_id, bank in banks.items()},
                "error": str(e)
            })

    return results