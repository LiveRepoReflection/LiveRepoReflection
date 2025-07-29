import threading
import time

class DistributedTxCoordinator:
    def __init__(self, timeout=5):
        self.timeout = timeout

    def run_transaction(self, transaction_id, nodes, transactions):
        # Phase 1: Prepare
        prepared_nodes = []
        for node in nodes:
            ops = transactions.get(node.node_id, [])
            try:
                success, error = self._execute_with_timeout(node.prepare, transaction_id, ops)
            except TimeoutError:
                # Timeout occurred; rollback all previously prepared nodes.
                for pnode in prepared_nodes:
                    try:
                        self._execute_with_timeout(pnode.rollback, transaction_id)
                    except TimeoutError:
                        pass
                return {
                    "status": "rolledback",
                    "failed_node": node.node_id,
                    "error": "Prepare timeout on node " + str(node.node_id)
                }
            if not success:
                # Prepare failed; rollback all previously prepared nodes.
                for pnode in prepared_nodes:
                    try:
                        self._execute_with_timeout(pnode.rollback, transaction_id)
                    except TimeoutError:
                        pass
                return {"status": "rolledback", "failed_node": node.node_id, "error": error}
            prepared_nodes.append(node)

        # Phase 2: Commit
        for node in nodes:
            try:
                success, error = self._execute_with_timeout(node.commit, transaction_id)
            except TimeoutError:
                # Timeout during commit; rollback all nodes.
                for pnode in prepared_nodes:
                    try:
                        self._execute_with_timeout(pnode.rollback, transaction_id)
                    except TimeoutError:
                        pass
                return {
                    "status": "rolledback",
                    "failed_node": node.node_id,
                    "error": "Commit timeout on node " + str(node.node_id)
                }
            if not success:
                # Commit failure; rollback all nodes.
                for pnode in prepared_nodes:
                    try:
                        self._execute_with_timeout(pnode.rollback, transaction_id)
                    except TimeoutError:
                        pass
                return {"status": "rolledback", "failed_node": node.node_id, "error": error}

        return {"status": "committed"}

    def _execute_with_timeout(self, func, *args):
        """Helper function to execute a function call with timeout."""
        result = [None]
        exception = [None]

        def target():
            try:
                result[0] = func(*args)
            except Exception as e:
                exception[0] = e

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(self.timeout)
        if thread.is_alive():
            raise TimeoutError("Function call timed out")
        if exception[0] is not None:
            raise exception[0]
        return result[0]