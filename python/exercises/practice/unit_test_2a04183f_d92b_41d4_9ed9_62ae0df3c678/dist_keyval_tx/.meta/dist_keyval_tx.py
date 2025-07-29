import threading
import uuid
import time
import os

# Global store and transaction management variables
global_store = {}
active_transactions = {}  # Maps TID -> transaction context
key_locks = {}  # Maps key -> threading.Lock()
global_lock = threading.Lock()

LOG_FILE = "dist_keyval_tx.log"
STATE_FILE = "dist_keyval_tx_state.log"

def _log(message):
    with threading.Lock():
        with open(LOG_FILE, "a") as f:
            f.write(message + "\n")

def _get_key_lock(key):
    with global_lock:
        if key not in key_locks:
            key_locks[key] = threading.Lock()
        return key_locks[key]

# Transaction context structure:
# {
#   'tid': transaction id,
#   'snapshot': a copy of global_store at transaction start,
#   'writes': dict of key -> value updates,
#   'locks': set of keys for which locks have been acquired
# }
def begin_transaction():
    tid = str(uuid.uuid4())
    with global_lock:
        snapshot = global_store.copy()
    txn_context = {
        'tid': tid,
        'snapshot': snapshot,
        'writes': {},
        'locks': set()
    }
    active_transactions[tid] = txn_context
    return tid

def read(key, transaction_id=None):
    if transaction_id is None:
        # Non transactional read, simply read global store
        return global_store.get(key, None)
    # Transactional read: Check local writes first, then snapshot
    if transaction_id not in active_transactions:
        raise ValueError("Invalid transaction id")
    txn = active_transactions[transaction_id]
    if key in txn['writes']:
        return txn['writes'][key]
    return txn['snapshot'].get(key, None)

def write(key, value, transaction_id=None):
    if transaction_id is None:
        # Non transactional write: update global store directly with lock
        lock = _get_key_lock(key)
        with lock:
            global_store[key] = value
            _log(f"Direct_Write: key={key}, value={value}")
            # Update state file for durability
            _durable_save()
        return
    if transaction_id not in active_transactions:
        raise ValueError("Invalid transaction id")
    txn = active_transactions[transaction_id]
    # Acquire lock for key if not already held by this transaction.
    if key not in txn['locks']:
        lock = _get_key_lock(key)
        # Try to acquire the lock; block until available.
        lock.acquire()
        txn['locks'].add(key)
    txn['writes'][key] = value

def commit_transaction(transaction_id):
    if transaction_id not in active_transactions:
        raise ValueError("Invalid transaction id")
    txn = active_transactions[transaction_id]
    # Two-Phase Commit Simulation

    # Phase 1: Prepare
    prepare_success = True
    for key in txn['writes']:
        # Log prepare for each key
        _log(f"Transaction {transaction_id} Prepare for key {key}")
        # In a real system, we would check constraints or local conditions here.
        # For simulation, assume vote commit is always positive if lock held.
        # We simulate a small delay
        time.sleep(0.01)
    
    # If any prepare failed (simulate by checking condition if needed), then abort.
    if not prepare_success:
        abort_transaction(transaction_id)
        return False
    
    # Phase 2: Commit
    for key, value in txn['writes'].items():
        _log(f"Transaction {transaction_id} Commit for key {key}")
        # Update the global store with the new value.
        global_store[key] = value
        # Also update snapshot to reflect commit for any future reads (if needed)
    # Simulate durability: save state to STATE_FILE
    _durable_save()
    # Release all locks held by the transaction
    for key in txn['locks']:
        lock = _get_key_lock(key)
        # Release the lock if held (it must be held by this transaction)
        if lock.locked():
            lock.release()
    _log(f"Transaction {transaction_id} Committed")
    # Remove transaction context
    del active_transactions[transaction_id]
    return True

def abort_transaction(transaction_id):
    if transaction_id not in active_transactions:
        raise ValueError("Invalid transaction id")
    txn = active_transactions[transaction_id]
    # Log abort for each key if any pending writes exist
    for key in txn['writes']:
        _log(f"Transaction {transaction_id} Abort for key {key}")
    # Release all locks held by the transaction
    for key in txn['locks']:
        lock = _get_key_lock(key)
        if lock.locked():
            lock.release()
    _log(f"Transaction {transaction_id} Aborted")
    del active_transactions[transaction_id]
    return True

def _durable_save():
    # Write the current global store state to the state file for durability.
    with global_lock:
        with open(STATE_FILE, "w") as f:
            f.write(str(global_store))

def reload_store():
    global global_store
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            content = f.read()
            try:
                # Evaluate the stored dictionary safely (only for simulation)
                global_store = eval(content)
            except Exception:
                global_store = {}
    else:
        global_store = {}

def reset_store():
    global global_store, active_transactions, key_locks
    global_store = {}
    active_transactions = {}
    key_locks = {}
    # Clear log file and state file
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)