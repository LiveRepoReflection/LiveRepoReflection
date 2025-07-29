import uuid
import threading
import time
import logging
import concurrent.futures
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('transaction_coordinator')

# Custom exceptions
class TransactionError(Exception):
    """Base class for transaction-related exceptions."""
    pass

class TransactionNotFound(TransactionError):
    """Raised when attempting to work with a non-existent transaction."""
    pass

class ParticipantFailedToCommit(TransactionError):
    """Raised when a participant fails during commit."""
    pass

class ParticipantFailedToRollback(TransactionError):
    """Raised when a participant fails during rollback."""
    pass

class MaxParticipantsExceeded(TransactionError):
    """Raised when trying to add more participants than allowed."""
    pass

class MaxTransactionsExceeded(TransactionError):
    """Raised when trying to create more concurrent transactions than allowed."""
    pass

class TransactionTimeout(TransactionError):
    """Raised when a transaction operation times out."""
    pass


class Participant(ABC):
    """Abstract base class for transaction participants."""
    
    @abstractmethod
    def commit(self, transaction_id: uuid.UUID) -> bool:
        """
        Commit changes for the given transaction.
        
        Args:
            transaction_id: The unique identifier for the transaction.
            
        Returns:
            bool: True if commit was successful.
            
        Raises:
            Exception: If commit fails.
        """
        pass
    
    @abstractmethod
    def rollback(self, transaction_id: uuid.UUID) -> bool:
        """
        Rollback changes for the given transaction.
        
        Args:
            transaction_id: The unique identifier for the transaction.
            
        Returns:
            bool: True if rollback was successful.
            
        Raises:
            Exception: If rollback fails.
        """
        pass


class TransactionCoordinator:
    """
    Coordinates distributed transactions across multiple participants.
    Implements a simplified two-phase commit protocol.
    """
    
    def __init__(self, max_participants: int = 10, max_concurrent_transactions: int = 100, commit_timeout: int = 30):
        """
        Initialize the transaction coordinator.
        
        Args:
            max_participants: Maximum number of participants allowed per transaction.
            max_concurrent_transactions: Maximum number of concurrent transactions allowed.
            commit_timeout: Timeout in seconds for commit operations.
        """
        self._transactions: Dict[uuid.UUID, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self.max_participants = max_participants
        self.max_concurrent_transactions = max_concurrent_transactions
        self.commit_timeout = commit_timeout
    
    def begin_transaction(self) -> uuid.UUID:
        """
        Start a new transaction.
        
        Returns:
            uuid.UUID: A unique transaction identifier.
            
        Raises:
            MaxTransactionsExceeded: If maximum number of concurrent transactions is reached.
        """
        with self._lock:
            if len(self._transactions) >= self.max_concurrent_transactions:
                logger.error(f"Max concurrent transactions limit reached: {self.max_concurrent_transactions}")
                raise MaxTransactionsExceeded(f"Maximum number of concurrent transactions ({self.max_concurrent_transactions}) exceeded")
            
            transaction_id = uuid.uuid4()
            self._transactions[transaction_id] = {
                'participants': [],
                'state': 'active',
                'created_at': time.time()
            }
            
            logger.info(f"Started transaction: {transaction_id}")
            return transaction_id
    
    def enlist_participant(self, transaction_id: uuid.UUID, participant: Participant) -> bool:
        """
        Add a participant to a transaction.
        
        Args:
            transaction_id: The transaction identifier.
            participant: The participant to add.
            
        Returns:
            bool: True if the participant was added successfully.
            
        Raises:
            TransactionNotFound: If the transaction doesn't exist.
            MaxParticipantsExceeded: If maximum participants per transaction is reached.
        """
        with self._lock:
            if transaction_id not in self._transactions:
                logger.error(f"Transaction not found: {transaction_id}")
                raise TransactionNotFound(f"Transaction {transaction_id} not found")
            
            transaction = self._transactions[transaction_id]
            
            if transaction['state'] != 'active':
                logger.error(f"Cannot enlist participant in {transaction['state']} transaction {transaction_id}")
                raise TransactionError(f"Cannot enlist participant in {transaction['state']} transaction")
            
            if len(transaction['participants']) >= self.max_participants:
                logger.error(f"Max participants limit reached for transaction {transaction_id}")
                raise MaxParticipantsExceeded(f"Maximum number of participants ({self.max_participants}) exceeded")
            
            transaction['participants'].append(participant)
            logger.info(f"Enlisted participant in transaction {transaction_id}")
            return True
    
    def commit_transaction(self, transaction_id: uuid.UUID) -> bool:
        """
        Commit a transaction by committing all participants.
        If any participant fails to commit, all participants are rolled back.
        
        Args:
            transaction_id: The transaction identifier.
            
        Returns:
            bool: True if all participants committed successfully.
            
        Raises:
            TransactionNotFound: If the transaction doesn't exist.
            ParticipantFailedToCommit: If any participant fails to commit.
        """
        with self._lock:
            if transaction_id not in self._transactions:
                logger.error(f"Transaction not found for commit: {transaction_id}")
                raise TransactionNotFound(f"Transaction {transaction_id} not found")
            
            transaction = self._transactions[transaction_id]
            
            if transaction['state'] != 'active':
                logger.error(f"Cannot commit {transaction['state']} transaction {transaction_id}")
                raise TransactionError(f"Cannot commit {transaction['state']} transaction")
            
            participants = transaction['participants']
            
            if not participants:
                logger.warning(f"Committing empty transaction {transaction_id}")
                del self._transactions[transaction_id]
                return True
            
            # Mark transaction as preparing to commit
            transaction['state'] = 'preparing'
            logger.info(f"Preparing to commit transaction {transaction_id} with {len(participants)} participants")
            
            # Phase 1: Prepare by doing nothing (simplified 2PC)
            # In a real 2PC, we would ask participants to prepare first
            
            # Phase 2: Commit
            committed_participants = []
            has_error = False
            error_message = ""
            
            # Use a ThreadPoolExecutor to implement timeout for each participant
            with concurrent.futures.ThreadPoolExecutor() as executor:
                try:
                    for participant in participants:
                        try:
                            # Submit the commit task with a timeout
                            future = executor.submit(participant.commit, transaction_id)
                            # Wait for the result with timeout
                            future.result(timeout=self.commit_timeout)
                            committed_participants.append(participant)
                        except concurrent.futures.TimeoutError:
                            has_error = True
                            error_message = f"Participant commit timed out after {self.commit_timeout} seconds"
                            logger.error(f"{error_message} for transaction {transaction_id}")
                            break
                        except Exception as e:
                            has_error = True
                            error_message = f"Participant commit failed: {str(e)}"
                            logger.error(f"{error_message} for transaction {transaction_id}")
                            break
                except Exception as e:
                    has_error = True
                    error_message = f"Unexpected error during commit: {str(e)}"
                    logger.error(f"{error_message} for transaction {transaction_id}")
            
            if has_error:
                # If any participant failed to commit, rollback all committed participants
                logger.info(f"Commit failed, rolling back transaction {transaction_id}")
                transaction['state'] = 'rolling_back'
                
                rollback_errors = []
                for participant in participants:
                    try:
                        participant.rollback(transaction_id)
                    except Exception as e:
                        rollback_errors.append(str(e))
                        logger.error(f"Rollback failed for participant during abort: {str(e)}")
                
                # Remove the transaction
                del self._transactions[transaction_id]
                
                if rollback_errors:
                    raise ParticipantFailedToRollback(f"Some participants failed to rollback after commit failure: {', '.join(rollback_errors)}")
                
                raise ParticipantFailedToCommit(error_message)
            
            # All participants committed successfully
            logger.info(f"Successfully committed transaction {transaction_id}")
            transaction['state'] = 'committed'
            
            # Clean up the transaction
            del self._transactions[transaction_id]
            return True
    
    def rollback_transaction(self, transaction_id: uuid.UUID) -> bool:
        """
        Rollback a transaction by rolling back all participants.
        
        Args:
            transaction_id: The transaction identifier.
            
        Returns:
            bool: True if all participants rolled back successfully.
            
        Raises:
            TransactionNotFound: If the transaction doesn't exist.
            ParticipantFailedToRollback: If any participant fails to rollback.
        """
        with self._lock:
            if transaction_id not in self._transactions:
                logger.error(f"Transaction not found for rollback: {transaction_id}")
                raise TransactionNotFound(f"Transaction {transaction_id} not found")
            
            transaction = self._transactions[transaction_id]
            participants = transaction['participants']
            
            if not participants:
                logger.warning(f"Rolling back empty transaction {transaction_id}")
                del self._transactions[transaction_id]
                return True
            
            # Mark transaction as rolling back
            transaction['state'] = 'rolling_back'
            logger.info(f"Rolling back transaction {transaction_id} with {len(participants)} participants")
            
            rollback_errors = []
            
            for participant in participants:
                try:
                    participant.rollback(transaction_id)
                except Exception as e:
                    rollback_errors.append(str(e))
                    logger.error(f"Rollback failed for participant: {str(e)}")
            
            # Clean up the transaction
            del self._transactions[transaction_id]
            
            if rollback_errors:
                raise ParticipantFailedToRollback(f"Some participants failed to rollback: {', '.join(rollback_errors)}")
            
            logger.info(f"Successfully rolled back transaction {transaction_id}")
            return True