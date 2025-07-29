from collections import defaultdict, deque


def validate_transactions(transactions):
    """
    Validates a batch of transactions according to the specified rules:
    1. No Double-Spending: No input account is used more than once across all transactions
    2. Sufficient Funds: Each transaction has sufficient funds (assuming initial balance of 0)
    3. DAG Consistency: Transactions form a Directed Acyclic Graph without cycles

    Args:
        transactions (list): List of transaction dictionaries with keys 'transaction_id', 'inputs', 'outputs'

    Returns:
        bool: True if the batch of transactions is valid, False otherwise
    """
    if not transactions:
        return True

    # Create mapping from transaction_id to transaction
    txn_map = {txn["transaction_id"]: txn for txn in transactions}
    
    # Create mapping from account to transactions that use it as input
    account_to_input_txns = defaultdict(set)
    
    # Create mapping from account to transactions that use it as output
    account_to_output_txns = defaultdict(set)
    
    # Build the dependencies
    for txn in transactions:
        txn_id = txn["transaction_id"]
        for input_account in txn["inputs"]:
            account_to_input_txns[input_account].add(txn_id)
        
        for output_account in txn["outputs"]:
            account_to_output_txns[output_account].add(txn_id)
    
    # Check for double-spending
    for account, txn_ids in account_to_input_txns.items():
        if len(txn_ids) > 1:
            return False
    
    # Build the transaction dependency graph
    # If transaction B uses an output account from transaction A as input,
    # then transaction B depends on transaction A
    graph = defaultdict(set)
    in_degree = defaultdict(int)
    
    for txn in transactions:
        txn_id = txn["transaction_id"]
        for input_account in txn["inputs"]:
            # For each input account, find transactions that output to it
            for dependency_txn_id in account_to_output_txns[input_account]:
                if dependency_txn_id != txn_id:  # Avoid self-loops
                    graph[dependency_txn_id].add(txn_id)
                    in_degree[txn_id] += 1
    
    # Check for cycles using topological sort
    queue = deque()
    
    # Add all nodes with in-degree 0 to the queue
    for txn_id in txn_map:
        if in_degree[txn_id] == 0:
            queue.append(txn_id)
    
    visited_count = 0
    
    # Maintain account balances to check for sufficient funds
    account_balances = defaultdict(int)
    
    # Process the queue
    while queue:
        current_txn_id = queue.popleft()
        visited_count += 1
        
        # Update account balances
        current_txn = txn_map[current_txn_id]
        
        # Check if there are sufficient funds in input accounts
        for input_account in current_txn["inputs"]:
            if account_balances[input_account] < 0:
                return False
        
        # Deduct from input accounts
        for input_account in current_txn["inputs"]:
            account_balances[input_account] -= 1
        
        # Add to output accounts
        for output_account in current_txn["outputs"]:
            account_balances[output_account] += 1
        
        # Process neighbors
        for neighbor in graph[current_txn_id]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # If we didn't visit all nodes, there's a cycle
    if visited_count != len(txn_map):
        return False
    
    return True