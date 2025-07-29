import threading

transaction_lock = threading.Lock()
data_lock = threading.Lock()

timestamp = 0

def generate_timestamp():
    """
    Returns a globally increasing integer timestamp.
    In a real distributed system, this would involve coordination across multiple nodes.
    """
    global timestamp
    with transaction_lock:
        timestamp += 1
        return timestamp


def execute_transactions(transactions, initial_data):
    """
    Executes a list of transactions with conflict resolution.

    Args:
        transactions: A list of transactions, each a tuple (transaction_id, operations).
        initial_data: A dictionary representing the initial state of the database.

    Returns:
        A tuple (committed_data, transaction_results).
    """
    global timestamp
    timestamp = 0  # Reset timestamp for testing

    # Create a mutable copy of the initial data for us to work with
    committed_data = initial_data.copy()
    transaction_results = {}
    
    # For lock management
    read_locks = {}  # Key: data key, Value: set of transaction IDs holding a read lock
    write_locks = {}  # Key: data key, Value: transaction ID holding the write lock, or None if no write lock
    
    # For tracking operation results per transaction
    transaction_operations = {}
    
    # For tracking aborted transactions
    aborted_transactions = set()

    # Timestamps for each transaction
    transaction_timestamps = {}
    
    # Helper functions for lock management
    def can_acquire_read_lock(txn_id, key):
        # Check if there's a write lock held by someone else
        if key in write_locks and write_locks[key] is not None and write_locks[key] != txn_id:
            return False
        return True
    
    def can_acquire_write_lock(txn_id, key):
        # Check if there are any read locks held by someone else
        if key in read_locks and any(reader != txn_id for reader in read_locks[key]):
            return False
        # Check if there's a write lock held by someone else
        if key in write_locks and write_locks[key] is not None and write_locks[key] != txn_id:
            return False
        return True
    
    def acquire_read_lock(txn_id, key):
        if can_acquire_read_lock(txn_id, key):
            if key not in read_locks:
                read_locks[key] = set()
            read_locks[key].add(txn_id)
            return True
        return False
    
    def acquire_write_lock(txn_id, key):
        if can_acquire_write_lock(txn_id, key):
            write_locks[key] = txn_id
            return True
        return False
    
    def release_locks(txn_id):
        # Release all read locks
        for key in list(read_locks.keys()):
            if txn_id in read_locks[key]:
                read_locks[key].remove(txn_id)
                if not read_locks[key]:  # Remove the key if the set is empty
                    del read_locks[key]
        
        # Release all write locks
        for key in list(write_locks.keys()):
            if write_locks[key] == txn_id:
                write_locks[key] = None
    
    # Assign timestamps to transactions
    for txn_id, ops in transactions:
        ts = generate_timestamp()
        transaction_timestamps[txn_id] = ts
        transaction_operations[txn_id] = []
    
    # Process transactions in timestamp order
    sorted_transactions = sorted(transactions, key=lambda t: transaction_timestamps[t[0]])
    
    for txn_id, operations in sorted_transactions:
        aborted = False
        current_transaction_results = []
        
        # Sort operations by key to prevent deadlocks
        sorted_operations = sorted(operations, key=lambda op: op[1])
        
        # Execute each operation
        for op_type, key, value in sorted_operations:
            if op_type == 'READ':
                if not acquire_read_lock(txn_id, key):
                    aborted = True
                    break
                
                # Perform the read operation
                if key not in committed_data:
                    current_transaction_results.append("KEY_NOT_FOUND")
                else:
                    current_transaction_results.append(committed_data[key])
                
            elif op_type == 'WRITE':
                if not acquire_write_lock(txn_id, key):
                    aborted = True
                    break
                
                # Perform the write operation - just record it for now
                if key not in committed_data:
                    committed_data[key] = value
                else:
                    committed_data[key] = value
                current_transaction_results.append("OK")
        
        if aborted:
            # Transaction aborted - record it and roll back any changes
            aborted_transactions.add(txn_id)
            transaction_results[txn_id] = 'ABORTED'
            # In a real system, we'd need to roll back all changes made by this transaction
            # For this exercise, we'll rebuild the committed_data from the beginning
        else:
            # Transaction committed - record its results
            transaction_results[txn_id] = current_transaction_results
        
        # Always release locks
        release_locks(txn_id)
    
    # Rebuild the committed data from initial data and successful transactions
    final_data = initial_data.copy()
    
    # Re-execute all successful transactions in timestamp order to get the final state
    for txn_id, operations in sorted_transactions:
        if txn_id not in aborted_transactions:
            for op_type, key, value in operations:
                if op_type == 'WRITE':
                    final_data[key] = value
    
    return final_data, transaction_results


if __name__ == "__main__":
    # Simple test
    transactions = [
        ("T1", [("WRITE", "A", "10"), ("READ", "A", None)]),
        ("T2", [("WRITE", "A", "20"), ("READ", "A", None)]),
    ]
    initial_data = {"A": "0"}
    
    committed_data, transaction_results = execute_transactions(transactions, initial_data)
    print(f"Committed data: {committed_data}")
    print(f"Transaction results: {transaction_results}")