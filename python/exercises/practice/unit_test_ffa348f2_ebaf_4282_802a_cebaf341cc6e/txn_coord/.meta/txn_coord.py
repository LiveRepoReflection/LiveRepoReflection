import threading
import uuid
import time
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
from typing import Dict, List, Any, Callable, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TransactionCoordinator:
    def __init__(self, timeout: int = 5, max_retries: int = 3):
        self._transactions: Dict[str, List[Tuple[Callable, Any]]] = {}
        self._completed_transactions: Dict[str, bool] = {}
        self._lock = threading.Lock()
        self._timeout = timeout
        self._max_retries = max_retries

    def begin_transaction(self) -> str:
        """Creates a new transaction and returns its unique ID."""
        transaction_id = str(uuid.uuid4())
        with self._lock:
            self._transactions[transaction_id] = []
        logger.info(f"Beginning transaction {transaction_id}")
        return transaction_id

    def enlist_service(self, transaction_id: str, service: Callable, data: Any) -> None:
        """Enlists a service in the transaction."""
        if transaction_id not in self._transactions:
            raise ValueError(f"Invalid transaction ID: {transaction_id}")
            
        with self._lock:
            self._transactions[transaction_id].append((service, data))
        logger.info(f"Enlisted service in transaction {transaction_id}")

    def _execute_prepare_phase(self, transaction_id: str) -> bool:
        """Executes the prepare phase for all enlisted services."""
        services = self._transactions.get(transaction_id, [])
        if not services:
            return True

        with ThreadPoolExecutor() as executor:
            prepare_futures = []
            for service, data in services:
                future = executor.submit(
                    self._execute_with_timeout,
                    service, "prepare", transaction_id, data
                )
                prepare_futures.append(future)

            try:
                # Wait for all prepare operations to complete
                results = []
                for future in as_completed(prepare_futures, timeout=self._timeout):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Prepare phase failed for transaction {transaction_id}: {str(e)}")
                        return False

                return all(results)
            except TimeoutError:
                logger.error(f"Prepare phase timed out for transaction {transaction_id}")
                return False

    def _execute_commit_phase(self, transaction_id: str) -> bool:
        """Executes the commit phase for all enlisted services."""
        services = self._transactions.get(transaction_id, [])
        if not services:
            return True

        with ThreadPoolExecutor() as executor:
            commit_futures = []
            for service, _ in services:
                future = executor.submit(
                    self._execute_with_retry,
                    service, "commit", transaction_id
                )
                commit_futures.append(future)

            try:
                # Wait for all commit operations to complete
                results = []
                for future in as_completed(commit_futures, timeout=self._timeout):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Commit phase failed for transaction {transaction_id}: {str(e)}")
                        return False

                return all(results)
            except TimeoutError:
                logger.error(f"Commit phase timed out for transaction {transaction_id}")
                return False

    def _execute_with_timeout(self, service: Callable, action: str, 
                            transaction_id: str, data: Any = None) -> bool:
        """Executes a service operation with timeout."""
        try:
            return service(action, transaction_id, data)
        except Exception as e:
            logger.error(f"Service {action} operation failed: {str(e)}")
            raise

    def _execute_with_retry(self, service: Callable, action: str, 
                          transaction_id: str, data: Any = None) -> bool:
        """Executes a service operation with retry logic."""
        for attempt in range(self._max_retries):
            try:
                return service(action, transaction_id, data)
            except Exception as e:
                if attempt == self._max_retries - 1:
                    logger.error(f"Service {action} operation failed after {self._max_retries} attempts")
                    raise
                logger.warning(f"Retrying {action} operation after failure: {str(e)}")
                time.sleep(0.1 * (attempt + 1))  # Exponential backoff
        return False

    def commit_transaction(self, transaction_id: str) -> bool:
        """Executes the two-phase commit protocol."""
        if transaction_id not in self._transactions:
            raise ValueError(f"Invalid transaction ID: {transaction_id}")

        # Check if transaction was already completed
        with self._lock:
            if transaction_id in self._completed_transactions:
                return self._completed_transactions[transaction_id]

        logger.info(f"Starting commit for transaction {transaction_id}")

        # Execute prepare phase
        prepare_success = self._execute_prepare_phase(transaction_id)
        if not prepare_success:
            logger.info(f"Prepare phase failed for transaction {transaction_id}")
            with self._lock:
                self._completed_transactions[transaction_id] = False
            return False

        # Execute commit phase
        commit_success = self._execute_commit_phase(transaction_id)
        
        with self._lock:
            self._completed_transactions[transaction_id] = commit_success
            if commit_success:
                logger.info(f"Successfully committed transaction {transaction_id}")
            else:
                logger.error(f"Failed to commit transaction {transaction_id}")

        return commit_success