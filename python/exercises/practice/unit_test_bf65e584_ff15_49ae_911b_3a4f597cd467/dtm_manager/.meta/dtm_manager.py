import uuid
import threading
from enum import Enum


class TransactionState(Enum):
    """Enum representing the possible states of a transaction."""
    ACTIVE = 1
    PREPARING = 2
    PREPARED = 3
    COMMITTING = 4
    COMMITTED = 5
    ROLLING_BACK = 6
    ROLLED_BACK = 7


class TransactionNotFound(Exception):
    """Exception raised when a transaction ID doesn't exist."""
    pass


class ResourceManagerNotFound(Exception):
    """Exception raised when a resource manager ID doesn't exist."""
    pass


class ResourceManagerAlreadyEnlisted(Exception):
    """Exception raised when a resource manager is already enlisted in another transaction."""
    pass


class InvalidTransactionState(Exception):
    """Exception raised when an operation is performed on a transaction in an invalid state."""
    pass


class DistributedTransactionManager:
    """
    A simplified, in-memory distributed transaction manager that coordinates 
    transactions across multiple independent resource managers using the two-phase commit protocol.
    """

    def __init__(self):
        """Initialize the Distributed Transaction Manager."""
        self._transactions = {}  # txid -> {state, rms, vote_results}
        self._rm_locks = {}  # rm_id -> lock
        self._rm_txid_map = {}  # rm_id -> txid
        self._transaction_lock = threading.RLock()
        self._max_transactions = 1000
        self._max_rms = 100
        self._max_concurrent_txs_per_rm = 10

    def begin_transaction(self):
        """
        Start a new distributed transaction.
        
        Returns:
            str: A unique transaction ID (TXID).
        
        Raises:
            RuntimeError: If the maximum number of concurrent transactions is reached.
        """
        with self._transaction_lock:
            # Check if we've reached the maximum number of concurrent transactions
            if len(self._transactions) >= self._max_transactions:
                raise RuntimeError("Maximum number of concurrent transactions reached")
            
            # Generate a unique transaction ID
            txid = str(uuid.uuid4())
            
            # Initialize transaction data structure
            self._transactions[txid] = {
                "state": TransactionState.ACTIVE,
                "rms": set(),  # Set of enlisted resource managers
                "vote_results": {},  # Dict to store prepare votes (rm_id -> bool)
                "lock": threading.RLock()  # Transaction-specific lock
            }
            
            return txid

    def enlist_resource(self, txid, rm_id):
        """
        Register a resource manager with a transaction.
        
        Args:
            txid (str): Transaction ID.
            rm_id (str): Resource Manager ID.
        
        Raises:
            TransactionNotFound: If the transaction ID doesn't exist.
            ResourceManagerAlreadyEnlisted: If the resource manager is already enlisted in another transaction.
            RuntimeError: If the maximum number of resource managers is reached.
            InvalidTransactionState: If the transaction is not in the ACTIVE state.
        """
        # Validate transaction
        if txid not in self._transactions:
            raise TransactionNotFound(f"Transaction {txid} not found")
        
        # Ensure RM ID is valid
        if not isinstance(rm_id, str) or not rm_id:
            raise ResourceManagerNotFound(f"Invalid resource manager ID: {rm_id}")
        
        with self._transaction_lock:
            # Check RM count limit
            if len(self._rm_locks) >= self._max_rms:
                raise RuntimeError("Maximum number of resource managers reached")
            
            # Create lock for this RM if it doesn't exist yet
            if rm_id not in self._rm_locks:
                self._rm_locks[rm_id] = threading.RLock()
            
            # Check if RM is already enlisted in another transaction
            if rm_id in self._rm_txid_map and self._rm_txid_map[rm_id] != txid:
                raise ResourceManagerAlreadyEnlisted(
                    f"Resource manager {rm_id} is already enlisted in transaction {self._rm_txid_map[rm_id]}"
                )
        
        # Get transaction-specific lock
        tx_lock = self._transactions[txid]["lock"]
        
        with tx_lock:
            tx_data = self._transactions[txid]
            
            # Check transaction state
            if tx_data["state"] != TransactionState.ACTIVE:
                raise InvalidTransactionState(
                    f"Cannot enlist resource in transaction {txid} with state {tx_data['state']}"
                )
            
            # Check concurrent transactions limit per RM
            rm_txs = sum(1 for tx_id, tx in self._transactions.items() 
                         if rm_id in tx["rms"] and tx["state"] not in 
                         (TransactionState.COMMITTED, TransactionState.ROLLED_BACK))
            
            if rm_txs >= self._max_concurrent_txs_per_rm:
                raise RuntimeError(f"Resource manager {rm_id} has reached its transaction limit")
            
            # Register RM with this transaction
            with self._rm_locks[rm_id]:
                tx_data["rms"].add(rm_id)
                self._rm_txid_map[rm_id] = txid

    def execute_operation(self, txid, rm_id, operation):
        """
        Simulate an operation executed within a transaction on a specific resource manager.
        
        Args:
            txid (str): Transaction ID.
            rm_id (str): Resource Manager ID.
            operation (str): Description of the operation.
        
        Raises:
            TransactionNotFound: If the transaction ID doesn't exist.
            ResourceManagerNotFound: If the resource manager ID doesn't exist or isn't enlisted.
            InvalidTransactionState: If the transaction is not in the ACTIVE state.
        """
        # Validate transaction
        if txid not in self._transactions:
            raise TransactionNotFound(f"Transaction {txid} not found")
        
        tx_data = self._transactions[txid]
        tx_lock = tx_data["lock"]
        
        with tx_lock:
            # Check transaction state
            if tx_data["state"] != TransactionState.ACTIVE:
                raise InvalidTransactionState(
                    f"Cannot execute operation in transaction {txid} with state {tx_data['state']}"
                )
            
            # Check if RM is enlisted in this transaction
            if rm_id not in tx_data["rms"]:
                raise ResourceManagerNotFound(
                    f"Resource manager {rm_id} is not enlisted in transaction {txid}"
                )
            
            # Simulate operation execution
            print(f"RM {rm_id}: Executing operation '{operation}' for TXID {txid}")
            # In a real implementation, this would communicate with the actual resource manager

    def prepare_transaction(self, txid):
        """
        Initiate the prepare phase of the 2PC protocol.
        
        Args:
            txid (str): Transaction ID.
        
        Returns:
            bool: True if all resource managers voted to commit, False otherwise.
        
        Raises:
            TransactionNotFound: If the transaction ID doesn't exist.
            InvalidTransactionState: If the transaction is not in the ACTIVE state.
        """
        # Validate transaction
        if txid not in self._transactions:
            raise TransactionNotFound(f"Transaction {txid} not found")
        
        tx_data = self._transactions[txid]
        tx_lock = tx_data["lock"]
        
        with tx_lock:
            # Check transaction state
            if tx_data["state"] != TransactionState.ACTIVE:
                raise InvalidTransactionState(
                    f"Cannot prepare transaction {txid} with state {tx_data['state']}"
                )
            
            # Update transaction state
            tx_data["state"] = TransactionState.PREPARING
            
            # Simulate prepare phase by asking all RMs to vote
            all_voted_yes = True
            for rm_id in tx_data["rms"]:
                with self._rm_locks[rm_id]:
                    # In a real implementation, this would send a prepare message to the RM
                    # and wait for its response
                    
                    # Simulate RM voting "yes" (in a real scenario, the RM could vote "no")
                    vote = True
                    tx_data["vote_results"][rm_id] = vote
                    
                    print(f"RM {rm_id}: Voted {'YES' if vote else 'NO'} for TXID {txid}")
                    
                    if not vote:
                        all_voted_yes = False
            
            # Update transaction state based on voting results
            if all_voted_yes:
                tx_data["state"] = TransactionState.PREPARED
            else:
                tx_data["state"] = TransactionState.ACTIVE  # Revert to active state if any RM voted "no"
            
            return all_voted_yes

    def commit_transaction(self, txid):
        """
        Initiate the commit phase of the 2PC protocol.
        
        Args:
            txid (str): Transaction ID.
        
        Raises:
            TransactionNotFound: If the transaction ID doesn't exist.
            InvalidTransactionState: If the transaction is not in the PREPARED state.
        """
        # Validate transaction
        if txid not in self._transactions:
            raise TransactionNotFound(f"Transaction {txid} not found")
        
        tx_data = self._transactions[txid]
        tx_lock = tx_data["lock"]
        
        with tx_lock:
            # Check transaction state
            if tx_data["state"] != TransactionState.PREPARED:
                raise InvalidTransactionState(
                    f"Cannot commit transaction {txid} with state {tx_data['state']}"
                )
            
            # Update transaction state
            tx_data["state"] = TransactionState.COMMITTING
            
            # Commit on all RMs
            for rm_id in tx_data["rms"]:
                with self._rm_locks[rm_id]:
                    # In a real implementation, this would send a commit message to the RM
                    print(f"RM {rm_id}: Committing transaction {txid}")
                    
                    # Release RM from this transaction
                    if rm_id in self._rm_txid_map and self._rm_txid_map[rm_id] == txid:
                        del self._rm_txid_map[rm_id]
            
            # Update transaction state
            tx_data["state"] = TransactionState.COMMITTED
            print(f"Transaction {txid}: COMMITTED")

    def rollback_transaction(self, txid):
        """
        Initiate the rollback phase of the 2PC protocol.
        
        Args:
            txid (str): Transaction ID.
        
        Raises:
            TransactionNotFound: If the transaction ID doesn't exist.
            InvalidTransactionState: If the transaction is already committed or rolled back.
        """
        # Validate transaction
        if txid not in self._transactions:
            raise TransactionNotFound(f"Transaction {txid} not found")
        
        tx_data = self._transactions[txid]
        tx_lock = tx_data["lock"]
        
        with tx_lock:
            # Check transaction state
            if tx_data["state"] in (TransactionState.COMMITTED, TransactionState.ROLLED_BACK):
                raise InvalidTransactionState(
                    f"Cannot rollback transaction {txid} with state {tx_data['state']}"
                )
            
            # Update transaction state
            tx_data["state"] = TransactionState.ROLLING_BACK
            
            # Rollback on all RMs
            for rm_id in tx_data["rms"]:
                try:
                    with self._rm_locks[rm_id]:
                        # In a real implementation, this would send a rollback message to the RM
                        print(f"RM {rm_id}: Rolling back transaction {txid}")
                        
                        # Release RM from this transaction
                        if rm_id in self._rm_txid_map and self._rm_txid_map[rm_id] == txid:
                            del self._rm_txid_map[rm_id]
                except Exception as e:
                    # Log the error but continue with other RMs
                    print(f"Error rolling back {rm_id} in transaction {txid}: {str(e)}")
            
            # Update transaction state
            tx_data["state"] = TransactionState.ROLLED_BACK
            print(f"Transaction {txid}: ROLLED BACK")