import threading
import uuid
import time
import concurrent.futures

def get_bank_service(account_id):
    raise NotImplementedError("get_bank_service should be implemented externally.")

class TransactionCoordinator:
    def __init__(self):
        self._lock = threading.Lock()
        self.current_transaction_id = None
        self._operations = {}  # Mapping: bank_service instance -> list of operations
        self._status = "pending"

    def begin_transaction(self):
        with self._lock:
            self.current_transaction_id = str(uuid.uuid4())
            self._operations = {}
            self._status = "pending"

    def transfer(self, from_account, to_account, amount):
        with self._lock:
            svc_from = get_bank_service(from_account)
            svc_to = get_bank_service(to_account)
            if svc_from not in self._operations:
                self._operations[svc_from] = []
            if svc_to not in self._operations:
                self._operations[svc_to] = []
            self._operations[svc_from].append((from_account, amount, "withdraw"))
            self._operations[svc_to].append((to_account, amount, "deposit"))

    def end_transaction(self):
        transaction_id = self.current_transaction_id
        if transaction_id is None:
            return "no active transaction"

        prepare_success = True
        prepare_results = {}

        # Prepare Phase: Execute prepare in parallel with timeout.
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_service = {
                executor.submit(self._prepare_service, svc, transaction_id, ops): svc
                for svc, ops in self._operations.items()
            }
            try:
                for future in concurrent.futures.as_completed(future_to_service, timeout=1.5):
                    svc = future_to_service[future]
                    try:
                        result = future.result(timeout=0)
                        prepare_results[svc] = result
                        if not result:
                            prepare_success = False
                    except Exception:
                        prepare_results[svc] = False
                        prepare_success = False
            except concurrent.futures.TimeoutError:
                prepare_success = False

        # Commit or Rollback Phase based on prepare results.
        if prepare_success and len(prepare_results) == len(self._operations):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for svc in self._operations.keys():
                    futures.append(executor.submit(svc.commit, transaction_id))
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception:
                        pass
            with self._lock:
                self._status = "committed"
        else:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for svc in self._operations.keys():
                    futures.append(executor.submit(svc.rollback, transaction_id))
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception:
                        pass
            with self._lock:
                self._status = "aborted"

        return self._status

    def _prepare_service(self, svc, transaction_id, operations):
        start_time = time.time()
        result = svc.prepare(transaction_id, operations)
        elapsed = time.time() - start_time
        if elapsed > 1:
            return False
        return result

    def get_transaction_status(self, transaction_id):
        with self._lock:
            if self.current_transaction_id == transaction_id:
                return self._status
            return "unknown"