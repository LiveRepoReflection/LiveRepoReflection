import threading

# Global lock for thread-safety
_global_lock = threading.RLock()

# Global timestamp counter
_global_timestamp = 0

def get_timestamp():
    global _global_timestamp
    with _global_lock:
        _global_timestamp += 1
        return _global_timestamp

# Global history: maps key -> list of (commit_ts, value) sorted by commit_ts ascending.
_global_history = {}

# Global mapping for the latest commit timestamp for each key.
_global_latest_ts = {}

# Transactions storage: maps transaction_id to its data.
# Each transaction is a dict with keys: 'start_ts', 'read_set' (set), 'write_set' (dict), 'active' (bool)
_transactions = {}

def begin_transaction():
    txn_id = get_timestamp()
    with _global_lock:
        _transactions[txn_id] = {
            'start_ts': txn_id,
            'read_set': set(),
            'write_set': {},
            'active': True
        }
    return txn_id

def _get_version_for_key(key, snapshot_ts):
    """
    Returns the value of the key from the global history that is visible to
    a transaction with snapshot timestamp snapshot_ts. If no version exists,
    return None.
    """
    versions = _global_history.get(key, [])
    result = None
    # Since versions are sorted in ascending commit_ts order, iterate to find the latest version <= snapshot_ts.
    for commit_ts, value in versions:
        if commit_ts <= snapshot_ts:
            result = value
        else:
            break
    return result

def read(transaction_id, key):
    with _global_lock:
        txn = _transactions.get(transaction_id)
        if txn is None or not txn['active']:
            return None
        # Check if the key has been written in the buffered writes of this transaction.
        if key in txn['write_set']:
            # Add to read_set as well.
            txn['read_set'].add(key)
            return txn['write_set'][key]
        # Otherwise, get the visible version from global history.
        value = _get_version_for_key(key, txn['start_ts'])
        txn['read_set'].add(key)
        return value

def write(transaction_id, key, value):
    with _global_lock:
        txn = _transactions.get(transaction_id)
        if txn is None or not txn['active']:
            return
        txn['write_set'][key] = value

def commit_transaction(transaction_id):
    with _global_lock:
        txn = _transactions.get(transaction_id)
        if txn is None or not txn['active']:
            return False
        
        # Conflict detection: For each key in the transaction's write_set,
        # if it has been updated (committed) after the transaction started (snapshot)
        # then abort. This check covers both write-write and read-write conflicts.
        start_ts = txn['start_ts']
        for key in txn['write_set']:
            latest_ts = _global_latest_ts.get(key, 0)
            if latest_ts > start_ts:
                # Conflict detected
                txn['active'] = False
                # Discard the transaction.
                _transactions.pop(transaction_id, None)
                return False

        # No conflict detected, assign a commit timestamp.
        commit_ts = get_timestamp()
        # Apply the buffered writes.
        for key, value in txn['write_set'].items():
            # Append the new version to the history of the key.
            if key not in _global_history:
                _global_history[key] = []
            _global_history[key].append((commit_ts, value))
            # Update the latest committed timestamp for this key.
            _global_latest_ts[key] = commit_ts

        # Mark the transaction as committed.
        txn['active'] = False
        _transactions.pop(transaction_id, None)
        return True

def abort_transaction(transaction_id):
    with _global_lock:
        txn = _transactions.get(transaction_id)
        if txn is None or not txn['active']:
            return
        txn['active'] = False
        _transactions.pop(transaction_id, None)