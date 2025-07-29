from decimal import Decimal
from typing import Dict, Any, List, Optional, Generator, Tuple
from collections import defaultdict
import time
import heapq
from datetime import datetime, timedelta

from .tx_reconcile import reconcile_transactions

class TransactionBuffer:
    """A buffer for storing and retrieving transactions within a time window."""
    
    def __init__(self, max_window: int):
        """
        Initialize the transaction buffer.
        
        Args:
            max_window: Maximum time window in seconds to keep transactions.
        """
        self.max_window = max_window
        self.buffer = defaultdict(list)  # transaction_id -> list of transactions
    
    def add(self, transaction: Dict[str, Any]) -> None:
        """Add a transaction to the buffer."""
        tx_id = transaction["transaction_id"]
        self.buffer[tx_id].append(transaction)
    
    def get_matching(self, tx_id: str, timestamp: int, window: int) -> List[Dict[str, Any]]:
        """Get transactions matching the given ID within the specified time window."""
        matching = []
        if tx_id in self.buffer:
            for tx in self.buffer[tx_id]:
                if abs(tx["timestamp"] - timestamp) <= window:
                    matching.append(tx)
        return matching
    
    def cleanup(self, current_time: int) -> None:
        """Remove transactions older than the maximum window."""
        cutoff_time = current_time - self.max_window
        
        # Create a new buffer with only valid transactions
        new_buffer = defaultdict(list)
        for tx_id, transactions in self.buffer.items():
            valid_transactions = [tx for tx in transactions if tx["timestamp"] >= cutoff_time]
            if valid_transactions:
                new_buffer[tx_id] = valid_transactions
        
        self.buffer = new_buffer
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all transactions in the buffer."""
        all_transactions = []
        for transactions in self.buffer.values():
            all_transactions.extend(transactions)
        return all_transactions


class StreamReconciliation:
    """A streaming reconciliation system for continuous transaction monitoring."""
    
    def __init__(self, time_window: int, amount_tolerance: Decimal, max_buffer_age: int = 86400):
        """
        Initialize the stream reconciliation system.
        
        Args:
            time_window: Time window (in seconds) within which transactions are considered matching.
            amount_tolerance: Tolerance for amount differences.
            max_buffer_age: Maximum age (in seconds) to keep transactions in buffer (default: 24 hours).
        """
        self.time_window = time_window
        self.amount_tolerance = amount_tolerance
        self.max_buffer_age = max_buffer_age
        self.expected_buffer = TransactionBuffer(max_buffer_age)
        self.observed_buffer = TransactionBuffer(max_buffer_age)
        self.last_cleanup_time = int(time.time())
        self.pending_discrepancies = []
    
    def add_expected_transaction(self, transaction: Dict[str, Any]) -> None:
        """Add an expected transaction to the system."""
        self.expected_buffer.add(transaction)
        self._process_new_transaction(transaction, is_expected=True)
    
    def add_observed_transaction(self, transaction: Dict[str, Any]) -> None:
        """Add an observed transaction to the system."""
        self.observed_buffer.add(transaction)
        self._process_new_transaction(transaction, is_expected=False)
    
    def _process_new_transaction(self, transaction: Dict[str, Any], is_expected: bool) -> None:
        """
        Process a newly added transaction.
        
        Args:
            transaction: The transaction to process.
            is_expected: True if this is an expected transaction, False if observed.
        """
        tx_id = transaction["transaction_id"]
        timestamp = transaction["timestamp"]
        
        if is_expected:
            # New expected transaction - check if it matches any observed transactions
            matching_observed = self.observed_buffer.get_matching(tx_id, timestamp, self.time_window)
            
            if not matching_observed:
                # Keep track of this transaction - it might match with future observed transactions
                # We'll check for missing transactions during cleanup
                pass
            else:
                # We found matching observed transactions - check for discrepancies
                for observed_tx in matching_observed:
                    self._check_discrepancies(transaction, observed_tx)
        else:
            # New observed transaction - check if it matches any expected transactions
            matching_expected = self.expected_buffer.get_matching(tx_id, timestamp, self.time_window)
            
            if not matching_expected:
                # This might be an unexpected transaction, or expected transaction might come later
                # We'll check for unexpected transactions during cleanup
                pass
            else:
                # We found matching expected transactions - check for discrepancies
                for expected_tx in matching_expected:
                    self._check_discrepancies(expected_tx, transaction)
        
        # Periodic cleanup
        current_time = int(time.time())
        if current_time - self.last_cleanup_time > 300:  # Clean up every 5 minutes
            self._cleanup(current_time)
            self.last_cleanup_time = current_time
    
    def _check_discrepancies(self, expected_tx: Dict[str, Any], observed_tx: Dict[str, Any]) -> None:
        """Check for discrepancies between expected and observed transactions."""
        tx_id = expected_tx["transaction_id"]
        discrepancies = []
        
        # Amount mismatch
        if abs(expected_tx["amount"] - observed_tx["amount"]) > self.amount_tolerance:
            discrepancies.append({
                "discrepancy_type": "AmountMismatch",
                "transaction_id": tx_id,
                "expected_record": expected_tx,
                "observed_record": observed_tx,
                "details": f"Expected amount: {expected_tx['amount']}, Observed amount: {observed_tx['amount']}"
            })
        
        # Currency mismatch
        if expected_tx["currency"] != observed_tx["currency"]:
            discrepancies.append({
                "discrepancy_type": "CurrencyMismatch",
                "transaction_id": tx_id,
                "expected_record": expected_tx,
                "observed_record": observed_tx,
                "details": f"Expected currency: {expected_tx['currency']}, Observed currency: {observed_tx['currency']}"
            })
        
        # Type mismatch
        if expected_tx["type"] != observed_tx["type"]:
            discrepancies.append({
                "discrepancy_type": "TypeMismatch",
                "transaction_id": tx_id,
                "expected_record": expected_tx,
                "observed_record": observed_tx,
                "details": f"Expected type: {expected_tx['type']}, Observed type: {observed_tx['type']}"
            })
        
        # Add any detected discrepancies to the pending list
        self.pending_discrepancies.extend(discrepancies)
    
    def _cleanup(self, current_time: int) -> None:
        """
        Clean up old transactions and detect missing/unexpected transactions.
        
        Args:
            current_time: Current timestamp.
        """
        # First, identify transactions that are old enough to be checked for missing/unexpected
        cutoff_time = current_time - self.time_window
        
        # Get all transactions from both buffers
        all_expected = self.expected_buffer.get_all()
        all_observed = self.observed_buffer.get_all()
        
        # Filter for transactions older than the cutoff time
        old_expected = [tx for tx in all_expected if tx["timestamp"] < cutoff_time]
        old_observed = [tx for tx in all_observed if tx["timestamp"] < cutoff_time]
        
        # Use the batch reconciliation function to find discrepancies
        new_discrepancies = reconcile_transactions(
            old_expected, old_observed, self.time_window, self.amount_tolerance
        )
        
        # Add new discrepancies to the pending list
        self.pending_discrepancies.extend(new_discrepancies)
        
        # Clean up buffers
        self.expected_buffer.cleanup(current_time)
        self.observed_buffer.cleanup(current_time)
    
    def get_discrepancies(self) -> List[Dict[str, Any]]:
        """Get all pending discrepancies and clear the pending list."""
        discrepancies = self.pending_discrepancies
        self.pending_discrepancies = []
        return discrepancies
    
    def force_reconciliation(self) -> List[Dict[str, Any]]:
        """
        Force a reconciliation of all transactions in the buffer.
        Useful for end-of-day processing or when shutting down the system.
        """
        current_time = int(time.time())
        self._cleanup(current_time)
        return self.get_discrepancies()