import threading

class TransactionCoordinator:
    def __init__(self):
        self._lock = threading.Lock()
        self._transactions = {}  # txid -> {"participants": [participant, ...], "status": str}
        self._tx_counter = 0

    def begin_transaction(self):
        with self._lock:
            self._tx_counter += 1
            txid = self._tx_counter
            self._transactions[txid] = {"participants": [], "status": "PENDING"}
            return txid

    def register_participant(self, txid, participant):
        with self._lock:
            if txid in self._transactions:
                # Register only if transaction is still pending
                if self._transactions[txid]["status"] == "PENDING":
                    self._transactions[txid]["participants"].append(participant)
            else:
                raise ValueError("Transaction ID does not exist")

    def commit_transaction(self, txid):
        with self._lock:
            if txid not in self._transactions:
                raise ValueError("Transaction ID does not exist")
            txn = self._transactions[txid]
            # Idempotency: if transaction previously committed/aborted, try to reapply the logic
            if txn["status"] == "COMMITTED":
                return True
            if txn["status"] == "ABORTED":
                # Allow re-calling rollback to ensure idempotency
                self._call_rollback(txid)
                return False

            participants = list(txn["participants"])
        # Release lock during external participant calls

        # Phase 1: Prepare
        for participant in participants:
            try:
                prep_result = participant.prepare()
            except Exception:
                prep_result = False
            if not prep_result:
                self.rollback_transaction(txid)
                return False

        # Phase 2: Commit
        for participant in participants:
            try:
                commit_result = participant.commit()
            except Exception:
                commit_result = False
            if not commit_result:
                self.rollback_transaction(txid)
                return False

        with self._lock:
            txn["status"] = "COMMITTED"
        return True

    def rollback_transaction(self, txid):
        # Rollback regardless of current status (idempotent rollback)
        with self._lock:
            if txid not in self._transactions:
                raise ValueError("Transaction ID does not exist")
            txn = self._transactions[txid]
            participants = list(txn["participants"])
        # Call rollback on all participants regardless of current state.
        for participant in participants:
            try:
                participant.rollback()
            except Exception:
                pass
        with self._lock:
            txn["status"] = "ABORTED"
        return True

    def get_transaction_status(self, txid):
        with self._lock:
            if txid not in self._transactions:
                raise ValueError("Transaction ID does not exist")
            return self._transactions[txid]["status"]