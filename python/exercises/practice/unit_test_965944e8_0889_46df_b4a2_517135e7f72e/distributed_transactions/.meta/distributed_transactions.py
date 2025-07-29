import threading
import time
import concurrent.futures
import math
from abc import ABC, abstractmethod

class Node(ABC):
    def __init__(self, node_id: int, failure_rate: float = 0.0):
        self.node_id = node_id
        self.failure_rate = failure_rate

    @abstractmethod
    def prepare(self, transaction_id: int) -> bool:
        pass

    @abstractmethod
    def commit(self, transaction_id: int) -> None:
        pass

    @abstractmethod
    def rollback(self, transaction_id: int) -> None:
        pass

class TransactionCoordinator:
    def __init__(self, retry_count: int = 3):
        self.retry_count = retry_count
        self.nodes = []
        self.tx_id_lock = threading.Lock()
        self.current_tx_id = 0

    def register_node(self, node: Node) -> None:
        self.nodes.append(node)

    def begin_transaction(self) -> int:
        with self.tx_id_lock:
            self.current_tx_id += 1
            tx_id = self.current_tx_id
        return tx_id

    def _execute_with_retry(self, func, node, transaction_id: int):
        attempt = 0
        delay = 1
        while attempt < self.retry_count:
            try:
                func(node, transaction_id)
                return True
            except Exception:
                attempt += 1
                if attempt < self.retry_count:
                    time.sleep(delay)
                    delay *= 2
        return False

    def end_transaction(self, transaction_id: int) -> bool:
        # Phase 1: Prepare Phase - execute concurrently.
        prepare_results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_node = {executor.submit(self._prepare_wrapper, node, transaction_id): node for node in self.nodes}
            for future in concurrent.futures.as_completed(future_to_node):
                node = future_to_node[future]
                try:
                    result = future.result()
                    prepare_results[node] = result
                except Exception:
                    prepare_results[node] = False

        # If any node votes False, rollback.
        if not all(prepare_results.values()):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(self._rollback_with_retry, node, transaction_id) for node in self.nodes]
                for future in concurrent.futures.as_completed(futures):
                    future.result()  # Wait for rollback to finish.
            return False

        # All prepared successfully, now commit phase.
        commit_results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_node = {executor.submit(self._commit_with_retry, node, transaction_id): node for node in self.nodes}
            for future in concurrent.futures.as_completed(future_to_node):
                node = future_to_node[future]
                try:
                    result = future.result()
                    commit_results[node] = result
                except Exception:
                    commit_results[node] = False

        # If any commit operation ultimately fails, perform rollback.
        if not all(commit_results.values()):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(self._rollback_with_retry, node, transaction_id) for node in self.nodes]
                for future in concurrent.futures.as_completed(futures):
                    future.result()  # Wait for rollback to finish.
            return False

        return True

    def _prepare_wrapper(self, node: Node, transaction_id: int) -> bool:
        # No retry logic needed for prepare, as immediate false means vote no.
        try:
            return node.prepare(transaction_id)
        except Exception:
            return False

    def _commit_with_retry(self, node: Node, transaction_id: int) -> bool:
        def commit_call(n, tx_id):
            n.commit(tx_id)
        return self._execute_with_retry(commit_call, node, transaction_id)

    def _rollback_with_retry(self, node: Node, transaction_id: int) -> bool:
        def rollback_call(n, tx_id):
            n.rollback(tx_id)
        return self._execute_with_retry(rollback_call, node, transaction_id)

    def get_node_count(self) -> int:
        return len(self.nodes)