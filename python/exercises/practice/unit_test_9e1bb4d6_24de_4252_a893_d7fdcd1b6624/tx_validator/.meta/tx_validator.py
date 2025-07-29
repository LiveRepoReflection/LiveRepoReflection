def validate_global_transaction(transactions, global_transaction_ids):
    # If global_transaction_ids is empty, it's not a valid global transaction
    if not global_transaction_ids:
        return False

    # Build a mapping from transaction_id to transaction record
    txn_map = {}
    for t in transactions:
        txn_map[t["transaction_id"]] = t

    # A set to collect all required transaction ids (global transactions + transitive dependencies)
    required_ids = set()

    # visited helps us avoid reprocessing transactions; in_progress for cycle detection.
    visited = {}
    
    def dfs(tid, in_progress):
        # Check if the transaction exists
        if tid not in txn_map:
            return False
        
        # Cycle detection: if tid is in in_progress, a cycle exists
        if tid in in_progress:
            return False
        
        # If already visited, skip further DFS; it's already valid.
        if tid in visited:
            return True
        
        # Mark current transaction as in progress for cycle detection.
        in_progress.add(tid)
        current_tx = txn_map[tid]
        
        # Process each dependency
        for dep_tid in current_tx.get("dependencies", []):
            # A transaction cannot depend on itself.
            if dep_tid == tid:
                return False
            # Timestamp consistency: dependency's timestamp must be <= current transaction's timestamp.
            if dep_tid in txn_map and txn_map[dep_tid]["timestamp"] > current_tx["timestamp"]:
                return False
            if not dfs(dep_tid, in_progress):
                return False
        
        # Finished processing current transaction; remove it from in_progress
        in_progress.remove(tid)
        visited[tid] = True
        required_ids.add(tid)
        return True

    # Start DFS from each transaction in global_transaction_ids
    for tid in global_transaction_ids:
        if not dfs(tid, set()):
            return False

    # Account Balance Consistency:
    # For each account, sort its transactions (from the required set) in chronological order and ensure balance stays non-negative.
    account_transactions = {}
    for tid in required_ids:
        t = txn_map[tid]
        account = t["account_id"]
        if account not in account_transactions:
            account_transactions[account] = []
        account_transactions[account].append(t)
    
    for account, tx_list in account_transactions.items():
        # Sort transactions by timestamp and then by transaction_id to stabilize ordering for same timestamps.
        tx_list.sort(key=lambda x: (x["timestamp"], x["transaction_id"]))
        balance = 0
        for t in tx_list:
            balance += t["amount"]
            if balance < 0:
                return False

    return True