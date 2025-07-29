import threading
import uuid
import time
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

class TransactionManager:
    def __init__(self):
        self._services = []
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=20)
        self._commit_retry_limit = 3
        self._rollback_retry_limit = 3
        self._timeout = 5  # seconds

    def begin_transaction(self):
        return str(uuid.uuid4())

    def enlist_service(self, service):
        with self._lock:
            self._services.append(service)

    def commit_transaction(self, transaction_id):
        # Make a snapshot of the current enlisted services
        with self._lock:
            services = list(self._services)

        logging.info("Starting transaction %s prepare phase", transaction_id)
        # Prepare phase
        for service in services:
            try:
                result = self._call_with_timeout(service.prepare, transaction_id)
                if not result:
                    logging.error("Service %r failed in prepare phase for transaction %s", service, transaction_id)
                    self.rollback_transaction(transaction_id)
                    return False
            except Exception as e:
                logging.error("Exception during prepare phase for transaction %s in service %r: %s", transaction_id, service, e)
                self.rollback_transaction(transaction_id)
                return False

        logging.info("Transaction %s prepare phase successful. Proceeding to commit phase.", transaction_id)
        # Commit phase
        commit_successful = True
        for service in services:
            committed = False
            attempts = 0
            while attempts < self._commit_retry_limit and not committed:
                try:
                    result = self._call_with_timeout(service.commit, transaction_id)
                    if result:
                        committed = True
                        logging.info("Service %r committed transaction %s successfully.", service, transaction_id)
                    else:
                        attempts += 1
                        logging.error("Service %r failed commit attempt %d for transaction %s", service, attempts, transaction_id)
                        time.sleep(1)
                except Exception as e:
                    attempts += 1
                    logging.error("Exception during commit attempt %d for transaction %s in service %r: %s", attempts, transaction_id, service, e)
                    time.sleep(1)
            if not committed:
                logging.error("Service %r exceeded commit retries for transaction %s", service, transaction_id)
                commit_successful = False
        if commit_successful:
            logging.info("Transaction %s committed successfully.", transaction_id)
        else:
            logging.error("Transaction %s failed to fully commit.", transaction_id)
        return commit_successful

    def rollback_transaction(self, transaction_id):
        # Make a snapshot of the current enlisted services
        with self._lock:
            services = list(self._services)
        logging.info("Starting rollback for transaction %s", transaction_id)
        for service in services:
            rolled_back = False
            attempts = 0
            while attempts < self._rollback_retry_limit and not rolled_back:
                try:
                    result = self._call_with_timeout(service.rollback, transaction_id)
                    if result:
                        rolled_back = True
                        logging.info("Service %r rolled back transaction %s successfully.", service, transaction_id)
                    else:
                        attempts += 1
                        logging.error("Service %r failed rollback attempt %d for transaction %s", service, attempts, transaction_id)
                        time.sleep(1)
                except Exception as e:
                    attempts += 1
                    logging.error("Exception during rollback attempt %d for transaction %s in service %r: %s", attempts, transaction_id, service, e)
                    time.sleep(1)
            if not rolled_back:
                logging.error("Service %r exceeded rollback retries for transaction %s", service, transaction_id)
        logging.info("Rollback process completed for transaction %s", transaction_id)
        return True

    def _call_with_timeout(self, func, transaction_id):
        future = self._executor.submit(func, transaction_id)
        try:
            result = future.result(timeout=self._timeout)
            return result
        except TimeoutError:
            future.cancel()
            logging.error("Timeout during service call %r for transaction %s", func, transaction_id)
            raise TimeoutError("Service call timed out")
        except Exception as e:
            raise e