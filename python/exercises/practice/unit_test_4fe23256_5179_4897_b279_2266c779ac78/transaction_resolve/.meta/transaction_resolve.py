from collections import defaultdict

def resolve_transactions(transactions):
    """
    Resolve transaction conflicts according to the specified rules.
    
    Args:
        transactions: A list of lists, where each inner list represents a transaction
                     and contains tuples of the form (node_id, transaction_id, state).
    
    Returns:
        A dictionary mapping transaction IDs to their final states ("COMMITTED" or "ABORTED").
    """
    result = {}
    
    # Group operations by transaction ID
    tx_operations = defaultdict(list)
    for transaction in transactions:
        for node_id, tx_id, state in transaction:
            tx_operations[tx_id].append((node_id, state))
    
    # Process each transaction
    for tx_id, operations in tx_operations.items():
        # Handle the case of empty operations list (edge case)
        if not operations:
            continue
        
        # Track the final state for each node (in case of duplicates)
        node_states = {}
        for node_id, state in operations:
            node_states[node_id] = state
        
        # Apply resolution rules
        if any(state == "COMMITTED" for _, state in node_states.items()):
            # Rule 1: If any node has committed, the transaction is committed
            result[tx_id] = "COMMITTED"
        elif any(state == "ABORTED" for _, state in node_states.items()):
            # Rule 2: If any node has aborted and no node has committed, the transaction is aborted
            result[tx_id] = "ABORTED"
        else:
            # Rule 3: If all nodes are in PREPARED state, commit the transaction
            result[tx_id] = "COMMITTED"
    
    return result