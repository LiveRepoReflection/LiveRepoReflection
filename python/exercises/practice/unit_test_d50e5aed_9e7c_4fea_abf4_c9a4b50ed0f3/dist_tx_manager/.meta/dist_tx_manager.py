import threading
import uuid
from enum import Enum
from typing import Dict, List, Tuple, Optional
import time

class TransactionState(Enum):
    PENDING = "PENDING"
    PREPARED = "PREPARED"
    COMMITTED = "COMMITTED"
    ABORTED = "ABORTED"

class Transaction:
    def __init__(self, txid: str):
        self.txid = txid
        self.state = TransactionState.PENDING
        self.operations: List[Tuple[str, str, int]] = []
        self.participating_nodes = set()
        self.lock = threading.Lock()

class DistributedTransactionManager:
    def __init__(self):
        self.transactions: Dict[str, Transaction] = {}
        self.global_lock = threading.Lock()
        
        # Simulated service node states (for testing)
        self.node_balances = {
            "node1": 1000,
            "node2": 1000,
            "failing_node": 100,
            "failing_commit_node": 1000
        }
        self.node_locks = {node: threading.Lock() for node in self.node_balances}

    def begin_transaction(self) -> str:
        """Initiates a new transaction and returns its ID."""
        txid = str(uuid.uuid4())
        with self.global_lock:
            self.transactions[txid] = Transaction(txid)
        return txid

    def add_operation(self, txid: str, service_node_id: str, operation_type: str, data: int) -> None:
        """Adds an operation to a transaction."""
        if operation_type not in ['debit', 'credit']:
            raise ValueError("Invalid operation type")
        
        with self.global_lock:
            if txid not in self.transactions:
                raise ValueError("Invalid transaction ID")
            
            transaction = self.transactions[txid]
            with transaction.lock:
                if transaction.state != TransactionState.PENDING:
                    raise ValueError("Transaction is not in PENDING state")
                
                transaction.operations.append((service_node_id, operation_type, data))
                transaction.participating_nodes.add(service_node_id)

    def prepare_transaction(self, txid: str) -> bool:
        """Implements the prepare phase of 2PC."""
        with self.global_lock:
            if txid not in self.transactions:
                raise ValueError("Invalid transaction ID")
            
            transaction = self.transactions[txid]
            with transaction.lock:
                if transaction.state != TransactionState.PENDING:
                    raise ValueError("Transaction is not in PENDING state")

                # Simulate prepare phase for each node
                prepare_results = []
                for node in transaction.participating_nodes:
                    result = self._prepare_node(node, transaction)
                    prepare_results.append(result)

                if all(prepare_results):
                    transaction.state = TransactionState.PREPARED
                    return True
                else:
                    # If any prepare fails, abort the transaction
                    self._abort_transaction_internal(transaction)
                    return False

    def commit_transaction(self, txid: str) -> bool:
        """Implements the commit phase of 2PC."""
        with self.global_lock:
            if txid not in self.transactions:
                raise ValueError("Invalid transaction ID")
            
            transaction = self.transactions[txid]
            with transaction.lock:
                if transaction.state == TransactionState.COMMITTED:
                    return True  # Idempotency
                
                if transaction.state != TransactionState.PREPARED:
                    raise ValueError("Transaction is not in PREPARED state")

                commit_results = []
                for node in transaction.participating_nodes:
                    result = self._commit_node(node, transaction)
                    commit_results.append(result)

                if all(commit_results):
                    transaction.state = TransactionState.COMMITTED
                    return True
                else:
                    transaction.state = TransactionState.ABORTED
                    return False

    def abort_transaction(self, txid: str) -> bool:
        """Aborts a transaction."""
        with self.global_lock:
            if txid not in self.transactions:
                raise ValueError("Invalid transaction ID")
            
            transaction = self.transactions[txid]
            with transaction.lock:
                if transaction.state == TransactionState.ABORTED:
                    return True  # Idempotency
                
                return self._abort_transaction_internal(transaction)

    def _abort_transaction_internal(self, transaction: Transaction) -> bool:
        """Internal method to abort a transaction."""
        abort_results = []
        for node in transaction.participating_nodes:
            result = self._abort_node(node, transaction)
            abort_results.append(result)

        transaction.state = TransactionState.ABORTED
        return all(abort_results)

    def get_transaction_state(self, txid: str) -> str:
        """Returns the current state of a transaction."""
        with self.global_lock:
            if txid not in self.transactions:
                raise ValueError("Invalid transaction ID")
            return self.transactions[txid].state.value

    def _prepare_node(self, node_id: str, transaction: Transaction) -> bool:
        """Simulates preparing a node for transaction commit."""
        if node_id == "failing_node":
            return False

        with self.node_locks[node_id]:
            balance = self.node_balances[node_id]
            for op_node, op_type, amount in transaction.operations:
                if op_node == node_id and op_type == 'debit':
                    if balance < amount:
                        return False
        return True

    def _commit_node(self, node_id: str, transaction: Transaction) -> bool:
        """Simulates committing a transaction on a node."""
        if node_id == "failing_commit_node":
            return False

        with self.node_locks[node_id]:
            for op_node, op_type, amount in transaction.operations:
                if op_node == node_id:
                    if op_type == 'debit':
                        self.node_balances[node_id] -= amount
                    else:  # credit
                        self.node_balances[node_id] += amount
        return True

    def _abort_node(self, node_id: str, transaction: Transaction) -> bool:
        """Simulates aborting a transaction on a node."""
        # In a real system, this would undo any prepared changes
        return True

    def get_account_balance(self, node_id: str) -> int:
        """Returns the current balance of a node (for testing)."""
        with self.node_locks[node_id]:
            return self.node_balances[node_id]