import threading

# Global lock for transaction id and commit version updates.
global_lock = threading.Lock()
txid_counter = 0
commit_version = 0

# Number of nodes in the distributed system.
NODES_COUNT = 3

# Global dictionary to keep track of active transactions.
transactions = {}

def get_node(key):
    return nodes[hash(key) % len(nodes)]

class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        # Data format: key -> (value, version)
        self.data = {}
        self.lock = threading.Lock()

    def prepare(self, write_set, snapshot):
        """
        Check for conflicts for the keys in write_set based on the snapshot.
        For each key that belongs to this node, compare its current version
        with the version recorded in the snapshot.
        """
        with self.lock:
            for key, new_val in write_set.items():
                expected_version = snapshot.get(key, (None, 0))[1] if key in snapshot else 0
                current_version = self.data.get(key, (None, 0))[1] if key in self.data else 0
                if current_version != expected_version:
                    return False
            return True

    def commit(self, write_set, new_version):
        """
        Apply all writes in write_set and update the version.
        """
        with self.lock:
            for key, new_val in write_set.items():
                self.data[key] = (new_val, new_version)

class Transaction:
    def __init__(self, txid, snapshot):
        self.txid = txid
        # Snapshot is a dictionary mapping node_id to a copy of that node's data.
        self.snapshot = snapshot
        # Write set stores keys and their new values.
        self.write_set = {}

def begin_transaction():
    """
    Initiates a new transaction by capturing snapshots from all nodes.
    Returns a unique transaction id.
    """
    global txid_counter
    with global_lock:
        txid_counter += 1
        txid = txid_counter
    # Capture snapshot for each node.
    snap = {}
    for node in nodes:
        # Create a shallow copy of the node's data to capture the version for each key.
        with node.lock:
            snap[node.node_id] = node.data.copy()
    transactions[txid] = Transaction(txid, snap)
    return txid

def read(txid, key):
    """
    Reads the value for a key within the context of the provided transaction.
    It first checks the transaction's write set, then falls back to the snapshot.
    """
    if txid not in transactions:
        raise Exception("Invalid Transaction ID")
    txn = transactions[txid]
    # If the key was already written in this transaction, return the local version.
    if key in txn.write_set:
        return txn.write_set[key]
    # Determine the responsible node and fetch from the transaction's snapshot.
    node = get_node(key)
    node_snapshot = txn.snapshot[node.node_id]
    return node_snapshot.get(key, (None, 0))[0]

def write(txid, key, value):
    """
    Writes a new value for the key within the context of the provided transaction.
    """
    if txid not in transactions:
        raise Exception("Invalid Transaction ID")
    txn = transactions[txid]
    txn.write_set[key] = value

def commit_transaction(txid):
    """
    Attempts to commit the transaction using a two-phase commit protocol.
    If any node detects a conflict, the transaction is aborted.
    Returns True if commit is successful, False otherwise.
    """
    global commit_version
    if txid not in transactions:
        raise Exception("Invalid Transaction ID")
    txn = transactions[txid]

    # Partition the write set by node.
    node_writes = {}
    for key, value in txn.write_set.items():
        node = get_node(key)
        if node.node_id not in node_writes:
            node_writes[node.node_id] = {}
        node_writes[node.node_id][key] = value

    # Phase 1: Prepare phase. Ask each node to prepare.
    for node in nodes:
        if node.node_id in node_writes:
            snapshot = txn.snapshot[node.node_id]
            if not node.prepare(node_writes[node.node_id], snapshot):
                abort_transaction(txid)
                return False

    # Phase 2: Commit phase.
    with global_lock:
        commit_version += 1
        new_version = commit_version

    for node in nodes:
        if node.node_id in node_writes:
            node.commit(node_writes[node.node_id], new_version)
    # Remove the transaction as it is committed.
    transactions.pop(txid, None)
    return True

def abort_transaction(txid):
    """
    Aborts the transaction by discarding its local state.
    """
    if txid in transactions:
        transactions.pop(txid, None)

# Initialize the distributed nodes.
nodes = [Node(node_id) for node_id in range(NODES_COUNT)]