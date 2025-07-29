import uuid
import threading
import time
import logging
from enum import Enum
from typing import Dict, List, Callable, Tuple
from dataclasses import dataclass
from threading import Lock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TransactionStatus(Enum):
    INITIATED = "initiated"
    PREPARING = "preparing"
    PREPARED = "prepared"
    COMMITTING = "committing"
    COMMITTED = "committed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"

@dataclass
class Participant:
    prepare_func: Callable[[], bool]
    commit_rollback_func: Callable[[str], bool]
    prepared: bool = False
    completed: bool = False

class Transaction:
    def __init__(self, txid: str):
        self.txid = txid
        self.participants: List[Participant] = []
        self.status = TransactionStatus.INITIATED
        self.lock = Lock()

class DistributedTransactionCoordinator:
    def __init__(self, prepare_timeout: float = 1.0):
        self.transactions: Dict[str, Transaction] = {}
        self.lock = Lock()
        self.prepare_timeout = prepare_timeout

    def begin_transaction(self) -> str:
        """Start a new transaction and return its ID."""
        txid = str(uuid.uuid4())
        with self.lock:
            self.transactions[txid] = Transaction(txid)
            logger.info(f"Started new transaction: {txid}")
        return txid

    def register_participant(
        self, 
        txid: str, 
        prepare_func: Callable[[], bool],
        commit_rollback_func: Callable[[str], bool]
    ) -> None:
        """Register a participant for the given transaction."""
        if txid not in self.transactions:
            raise ValueError(f"Transaction {txid} does not exist")

        transaction = self.transactions[txid]
        with transaction.lock:
            if transaction.status != TransactionStatus.INITIATED:
                raise ValueError(f"Cannot register participant: transaction {txid} is already in progress")
            
            participant = Participant(prepare_func, commit_rollback_func)
            transaction.participants.append(participant)
            logger.info(f"Registered new participant for transaction {txid}")

    def get_participants(self, txid: str) -> List[Participant]:
        """Get all participants for a given transaction."""
        return self.transactions[txid].participants if txid in self.transactions else []

    def _prepare_participant(
        self, 
        participant: Participant, 
        results: List[bool], 
        index: int,
        timeout: float
    ) -> None:
        """Execute prepare phase for a single participant."""
        start_time = time.time()
        try:
            success = participant.prepare_func()
            if time.time() - start_time > timeout:
                results[index] = False
            else:
                results[index] = success
                if success:
                    participant.prepared = True
        except Exception as e:
            logger.error(f"Prepare phase failed with error: {str(e)}")
            results[index] = False

    def _prepare_phase(self, transaction: Transaction) -> bool:
        """Execute prepare phase for all participants."""
        with transaction.lock:
            transaction.status = TransactionStatus.PREPARING
            logger.info(f"Starting prepare phase for transaction {transaction.txid}")

        results = [False] * len(transaction.participants)
        threads = []

        # Start prepare phase for all participants
        for i, participant in enumerate(transaction.participants):
            thread = threading.Thread(
                target=self._prepare_participant,
                args=(participant, results, i, self.prepare_timeout)
            )
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete or timeout
        for thread in threads:
            thread.join(self.prepare_timeout)

        success = all(results)
        
        with transaction.lock:
            transaction.status = TransactionStatus.PREPARED if success else TransactionStatus.ROLLING_BACK
            logger.info(f"Prepare phase {'succeeded' if success else 'failed'} for transaction {transaction.txid}")
        
        return success

    def _commit_phase(self, transaction: Transaction) -> bool:
        """Execute commit phase for all participants."""
        with transaction.lock:
            transaction.status = TransactionStatus.COMMITTING
            logger.info(f"Starting commit phase for transaction {transaction.txid}")

        success = True
        for participant in transaction.participants:
            if participant.prepared and not participant.completed:
                try:
                    if not participant.commit_rollback_func("commit"):
                        success = False
                    participant.completed = True
                except Exception as e:
                    logger.error(f"Commit phase failed with error: {str(e)}")
                    success = False

        with transaction.lock:
            transaction.status = TransactionStatus.COMMITTED if success else TransactionStatus.ROLLING_BACK
            logger.info(f"Commit phase {'succeeded' if success else 'failed'} for transaction {transaction.txid}")

        return success

    def _rollback_phase(self, transaction: Transaction) -> None:
        """Execute rollback phase for all participants."""
        with transaction.lock:
            transaction.status = TransactionStatus.ROLLING_BACK
            logger.info(f"Starting rollback phase for transaction {transaction.txid}")

        for participant in transaction.participants:
            if not participant.completed:
                try:
                    participant.commit_rollback_func("rollback")
                    participant.completed = True
                except Exception as e:
                    logger.error(f"Rollback failed with error: {str(e)}")

        with transaction.lock:
            transaction.status = TransactionStatus.ROLLED_BACK
            logger.info(f"Rollback phase completed for transaction {transaction.txid}")

    def commit_transaction(self, txid: str) -> str:
        """
        Attempt to commit a transaction.
        Returns "committed" if successful, "rolled_back" otherwise.
        """
        if txid not in self.transactions:
            raise ValueError(f"Transaction {txid} does not exist")

        transaction = self.transactions[txid]
        
        # Check if transaction is already completed
        with transaction.lock:
            if transaction.status in [TransactionStatus.COMMITTED, TransactionStatus.ROLLED_BACK]:
                return transaction.status.value

        # Execute prepare phase
        if self._prepare_phase(transaction):
            # If prepare successful, execute commit phase
            if self._commit_phase(transaction):
                return "committed"
            else:
                self._rollback_phase(transaction)
                return "rolled_back"
        else:
            # If prepare failed, execute rollback phase
            self._rollback_phase(transaction)
            return "rolled_back"