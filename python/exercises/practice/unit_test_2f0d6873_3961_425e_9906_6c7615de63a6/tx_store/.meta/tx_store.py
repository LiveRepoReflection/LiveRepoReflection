import uuid
import threading
from collections import defaultdict
from typing import Dict, Optional, Any

class KeyValueStore:
    def __init__(self):
        """
        Initialize the KeyValueStore with the necessary data structures:
        - committed_data: stores the committed key-value pairs
        - transactions: stores the pending changes for each transaction
        - transaction_status: tracks the status of each transaction
        - client_transactions: maps client IDs to their active transaction IDs
        - lock: ensures thread safety in concurrent operations
        """
        self.committed_data: Dict[str, str] = {}
        self.transactions: Dict[str, Dict[str, str]] = {}
        self.transaction_status: Dict[str, str] = {}  # 'active', 'committed', 'rolled_back'
        self.client_transactions: Dict[str, str] = {}
        self.lock = threading.RLock()  # Reentrant lock for thread safety

    def begin_transaction(self, client_id: str) -> str:
        """
        Starts a new transaction for the given client_id.
        Returns a unique transaction ID.
        
        Args:
            client_id: A string identifier for the client starting the transaction
            
        Returns:
            A unique transaction ID as a string
            
        Raises:
            Exception: If the client already has an active transaction
        """
        with self.lock:
            # Check if the client already has an active transaction
            if client_id in self.client_transactions:
                active_tx = self.client_transactions[client_id]
                if self.transaction_status.get(active_tx) == 'active':
                    raise Exception(f"Client {client_id} already has an active transaction")
            
            # Generate a unique transaction ID
            tx_id = str(uuid.uuid4())
            
            # Initialize transaction data structures
            self.transactions[tx_id] = {}
            self.transaction_status[tx_id] = 'active'
            self.client_transactions[client_id] = tx_id
            
            return tx_id

    def put(self, tx_id: str, key: str, value: str) -> None:
        """
        Within the transaction identified by tx_id, associates the key with the value.
        
        Args:
            tx_id: The transaction ID
            key: The key to associate with the value
            value: The value to store
            
        Raises:
            Exception: If the transaction doesn't exist or is not active
        """
        with self.lock:
            # Validate transaction
            self._validate_transaction(tx_id)
            
            # Store the key-value pair in the transaction's pending changes
            self.transactions[tx_id][key] = value

    def get(self, tx_id: str, key: str) -> Optional[str]:
        """
        Within the transaction identified by tx_id, retrieves the value associated with the key.
        
        Args:
            tx_id: The transaction ID
            key: The key to look up
            
        Returns:
            The value associated with the key in the current transaction, or the latest committed
            value if the key is not modified in the current transaction, or None if the key doesn't exist
            
        Raises:
            Exception: If the transaction doesn't exist or is not active
        """
        with self.lock:
            # Validate transaction
            self._validate_transaction(tx_id)
            
            # Check if the key exists in the transaction's pending changes
            if key in self.transactions[tx_id]:
                return self.transactions[tx_id][key]
            
            # If not found in the transaction, look for the key in the committed data
            return self.committed_data.get(key)

    def commit_transaction(self, tx_id: str) -> None:
        """
        Atomically commits the transaction identified by tx_id, making all its changes visible.
        
        Args:
            tx_id: The transaction ID to commit
            
        Raises:
            Exception: If the transaction doesn't exist or is not active
        """
        with self.lock:
            # Validate transaction
            self._validate_transaction(tx_id)
            
            # Apply all pending changes to the committed data
            for key, value in self.transactions[tx_id].items():
                self.committed_data[key] = value
            
            # Update transaction status
            self.transaction_status[tx_id] = 'committed'
            
            # Clean up client mapping
            self._cleanup_client_mapping(tx_id)

    def rollback_transaction(self, tx_id: str) -> None:
        """
        Rolls back (aborts) the transaction identified by tx_id, discarding all its changes.
        
        Args:
            tx_id: The transaction ID to roll back
            
        Raises:
            Exception: If the transaction doesn't exist or is not active
        """
        with self.lock:
            # Validate transaction
            self._validate_transaction(tx_id)
            
            # Update transaction status
            self.transaction_status[tx_id] = 'rolled_back'
            
            # Clean up client mapping
            self._cleanup_client_mapping(tx_id)
            
            # Clear transaction data (optional, for potential garbage collection)
            self.transactions[tx_id].clear()

    def _validate_transaction(self, tx_id: str) -> None:
        """
        Helper method to validate that a transaction exists and is active.
        
        Args:
            tx_id: The transaction ID to validate
            
        Raises:
            Exception: If the transaction doesn't exist or is not active
        """
        if tx_id not in self.transaction_status:
            raise Exception(f"Transaction {tx_id} does not exist")
        
        if self.transaction_status[tx_id] != 'active':
            status = self.transaction_status[tx_id]
            raise Exception(f"Transaction {tx_id} is not active (status: {status})")

    def _cleanup_client_mapping(self, tx_id: str) -> None:
        """
        Helper method to clean up the client-to-transaction mapping.
        
        Args:
            tx_id: The transaction ID to clean up
        """
        # Remove the client-transaction mapping for this transaction
        clients_to_remove = []
        for client_id, active_tx in self.client_transactions.items():
            if active_tx == tx_id:
                clients_to_remove.append(client_id)
                
        for client_id in clients_to_remove:
            del self.client_transactions[client_id]

    def get_transaction_snapshot(self, tx_id: str) -> Dict[str, str]:
        """
        Returns a snapshot of the data as visible to the given transaction.
        This includes both the transaction's pending changes and the committed data.
        
        Args:
            tx_id: The transaction ID
            
        Returns:
            A dictionary containing all key-value pairs visible to the transaction
            
        Raises:
            Exception: If the transaction doesn't exist or is not active
        """
        with self.lock:
            # Validate transaction
            self._validate_transaction(tx_id)
            
            # Start with the committed data
            snapshot = self.committed_data.copy()
            
            # Apply the transaction's pending changes
            snapshot.update(self.transactions[tx_id])
            
            return snapshot

    def cleanup_transaction_data(self) -> None:
        """
        Garbage collection method to clean up completed transactions.
        This should be called periodically in a production environment.
        """
        with self.lock:
            # Identify transactions that can be cleaned up
            completed_txs = [tx_id for tx_id, status in self.transaction_status.items() 
                            if status != 'active']
            
            # Remove completed transactions from data structures
            for tx_id in completed_txs:
                if tx_id in self.transactions:
                    del self.transactions[tx_id]
                if tx_id in self.transaction_status:
                    del self.transaction_status[tx_id]