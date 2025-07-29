import threading
import uuid

# Global data structures for the distributed transactional store.
_valid_nodes = {"node1", "node2"}
_connected_nodes = []
_next_node_index = 0
_connected_lock = threading.Lock()

# Global map of transaction_id -> transaction object
_transactions = {}
_transactions_lock = threading.Lock()

# Global committed key store: key -> {"value": str, "owner": str, "version_vector": dict}
_committed_store = {}
_committed_lock = threading.Lock()


class Transaction:
    def __init__(self, tx_id, owner_node):
        self.tx_id = tx_id
        self.owner_node = owner_node
        # staged changes: key -> value
        self.staged = {}


def connect(node_id: str) -> bool:
    global _connected_nodes
    if node_id not in _valid_nodes:
        return False
    with _connected_lock:
        if node_id not in _connected_nodes:
            _connected_nodes.append(node_id)
    return True


def begin_transaction() -> str:
    global _next_node_index
    with _transactions_lock, _connected_lock:
        if not _connected_nodes:
            # No connected nodes means we cannot start a transaction.
            # For simplicity, generate a transaction with a default node "node1" if available.
            owner_node = "node1"
            if owner_node not in _valid_nodes:
                raise Exception("No valid node available for transaction")
        else:
            # Round robin assignment to connected nodes.
            owner_node = _connected_nodes[_next_node_index % len(_connected_nodes)]
            _next_node_index += 1
        tx_id = str(uuid.uuid4())
        _transactions[tx_id] = Transaction(tx_id, owner_node)
    return tx_id


def put(transaction_id: str, key: str, value: str) -> bool:
    with _transactions_lock:
        tx = _transactions.get(transaction_id)
        if tx is None:
            return False
        tx.staged[key] = value
    return True


def commit_transaction(transaction_id: str) -> bool:
    global _committed_store
    with _transactions_lock:
        tx = _transactions.get(transaction_id)
        if tx is None:
            return False
        # Remove the transaction from the global transactions now.
        del _transactions[transaction_id]
    # For each key in the transaction, commit the change.
    with _committed_lock:
        for key, new_value in tx.staged.items():
            if key not in _committed_store:
                # First commit for the key.
                _committed_store[key] = {
                    "value": new_value,
                    "owner": tx.owner_node,
                    "version_vector": {tx.owner_node: 1}
                }
            else:
                current_entry = _committed_store[key]
                current_owner = current_entry["owner"]
                # Last-write-wins: use lexicographic order of node id.
                if tx.owner_node > current_owner:
                    # Update the value, owner, and version vector.
                    version_vector = current_entry["version_vector"].copy()
                    version_vector[tx.owner_node] = version_vector.get(tx.owner_node, 0) + 1
                    _committed_store[key] = {
                        "value": new_value,
                        "owner": tx.owner_node,
                        "version_vector": version_vector
                    }
                else:
                    # Even if the new transaction's node is not the winner,
                    # update the version vector to reflect the attempted commit.
                    version_vector = current_entry["version_vector"].copy()
                    version_vector[tx.owner_node] = version_vector.get(tx.owner_node, 0) + 1
                    # Do not change the committed value and owner.
                    _committed_store[key]["version_vector"] = version_vector
    return True


def abort_transaction(transaction_id: str) -> None:
    with _transactions_lock:
        if transaction_id in _transactions:
            del _transactions[transaction_id]


def get(key: str) -> str:
    with _committed_lock:
        entry = _committed_store.get(key)
        if entry:
            return entry["value"]
        return None