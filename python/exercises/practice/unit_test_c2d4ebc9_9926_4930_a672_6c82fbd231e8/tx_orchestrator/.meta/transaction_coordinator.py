import threading
import concurrent.futures
import time
from typing import List, Callable

class TransactionCoordinator:
    def __init__(self):
        self.lock = threading.Lock()
        self.active_transactions = {}

    def execute_transaction(self, services: List[object], tx_id: str, timeout: int) -> bool:
        with self.lock:
            if tx_id in self.active_transactions:
                raise ValueError(f"Transaction {tx_id} already exists")
            self.active_transactions[tx_id] = {'status': 'pending', 'services': services}

        try:
            # Phase 1: Prepare
            prepared = self._prepare_phase(services, tx_id, timeout)
            if not prepared:
                self._rollback_phase(services, tx_id, timeout)
                return False

            # Phase 2: Commit
            committed = self._commit_phase(services, tx_id, timeout)
            if not committed:
                self._rollback_phase(services, tx_id, timeout)
                return False

            return True
        finally:
            with self.lock:
                self.active_transactions.pop(tx_id, None)

    def _prepare_phase(self, services: List[object], tx_id: str, timeout: int) -> bool:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for service in services:
                futures.append(executor.submit(self._call_service_operation, 
                                             service.prepare, tx_id, timeout))

            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception:
                    results.append(False)

            return all(results)

    def _commit_phase(self, services: List[object], tx_id: str, timeout: int) -> bool:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for service in services:
                futures.append(executor.submit(self._call_service_operation, 
                                             service.commit, tx_id, timeout))

            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                    results.append(True)
                except Exception:
                    results.append(False)

            return all(results)

    def _rollback_phase(self, services: List[object], tx_id: str, timeout: int) -> bool:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for service in services:
                futures.append(executor.submit(self._call_service_operation, 
                                             service.rollback, tx_id, timeout))

            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                    results.append(True)
                except Exception:
                    results.append(False)

            return all(results)

    def _call_service_operation(self, operation: Callable, tx_id: str, timeout: int):
        start_time = time.time()
        try:
            future = concurrent.futures.Future()
            
            def worker():
                try:
                    result = operation(tx_id)
                    future.set_result(result)
                except Exception as e:
                    future.set_exception(e)
            
            thread = threading.Thread(target=worker)
            thread.start()
            thread.join(timeout=timeout)
            
            if thread.is_alive():
                raise TimeoutError(f"Operation timed out after {timeout} seconds")
            
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Operation timed out after {timeout} seconds")
                
            return future.result()
        except Exception as e:
            raise e