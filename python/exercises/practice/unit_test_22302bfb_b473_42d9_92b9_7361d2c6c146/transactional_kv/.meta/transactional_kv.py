from bisect import bisect_right

global_version = 0
global_store = {}  # key: list of (version, value) tuples in ascending order
transactions = {}  # txid: {"snapshot": int, "local": dict}
next_tx_id = 1

def begin_transaction():
    global next_tx_id, global_version
    txid = next_tx_id
    next_tx_id += 1
    transactions[txid] = {"snapshot": global_version, "local": {}}
    return txid

def read(txid, key):
    if txid not in transactions:
        raise ValueError("Transaction ID does not exist.")
    tx = transactions[txid]
    # Check local writes first
    if key in tx["local"]:
        return tx["local"][key]
    # Now check the global store using snapshot isolation
    if key not in global_store:
        return None
    versions = global_store[key]
    # Find the rightmost insertion point for tx snapshot
    idx = bisect_right(versions, (tx["snapshot"], chr(255)))
    if idx == 0:
        return None
    return versions[idx - 1][1]

def write(txid, key, value):
    if txid not in transactions:
        raise ValueError("Transaction ID does not exist.")
    transactions[txid]["local"][key] = value

def commit_transaction(txid):
    global global_version
    if txid not in transactions:
        raise ValueError("Transaction ID does not exist.")
    tx = transactions[txid]
    snapshot = tx["snapshot"]
    local_writes = tx["local"]
    # Conflict detection: For each key in local writes, make sure no commit happened after the tx snapshot.
    for key in local_writes:
        if key in global_store and global_store[key]:
            last_version = global_store[key][-1][0]
            if last_version > snapshot:
                # Conflict: remove transaction and return False
                del transactions[txid]
                return False
    # No conflicts: commit all writes with new commit version number
    global_version += 1
    new_commit_version = global_version
    for key, value in local_writes.items():
        if key not in global_store:
            global_store[key] = []
        global_store[key].append((new_commit_version, value))
    del transactions[txid]
    return True

def rollback_transaction(txid):
    if txid not in transactions:
        raise ValueError("Transaction ID does not exist.")
    del transactions[txid]