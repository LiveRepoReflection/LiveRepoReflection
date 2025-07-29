def coordinate_transaction(nodes, transaction):
    """
    Coordinates a distributed transaction using two-phase commit protocol.
    
    Args:
        nodes: List of node dictionaries with can_commit, commit, and rollback functions
        transaction: Dictionary containing transaction_id, operations, and expected_reads
        
    Returns:
        bool: True if transaction committed successfully, False if rolled back
    """
    transaction_id = transaction["transaction_id"]
    operations = transaction["operations"]
    expected_reads = transaction.get("expected_reads", {})
    
    # Phase 1: Prepare - Collect votes from all nodes
    prepare_results = {}
    node_operations = {}
    
    # Group operations by node
    for op in operations:
        node_id = op[0]
        if node_id not in node_operations:
            node_operations[node_id] = []
        node_operations[node_id].append(op)
    
    # Check all nodes are valid
    node_ids = {node["node_id"] for node in nodes}
    for node_id in node_operations.keys():
        if node_id not in node_ids:
            raise ValueError(f"Node {node_id} not found in cluster")
    
    # Execute reads and verify expected values
    temp_data = {}
    for op in operations:
        node_id, op_type, key, value = op
        if op_type == "read":
            # Check if this read has an expected value
            if (node_id, key) in expected_reads:
                # In a real system, we would read from the node
                # For this simulation, we'll use the value from the operation
                # or from previous writes in this transaction
                found_value = None
                # Check if we wrote this key earlier in the transaction
                for prev_op in operations:
                    if (prev_op[0] == node_id and prev_op[1] == "write" and 
                        prev_op[2] == key and prev_op[3] is not None):
                        found_value = prev_op[3]
                        break
                
                if found_value is None:
                    # If not written in this transaction, use node's data
                    for node in nodes:
                        if node["node_id"] == node_id:
                            found_value = node["data"].get(key, None)
                            break
                
                if found_value != expected_reads[(node_id, key)]:
                    raise ValueError(f"Read verification failed for node {node_id} key {key}. "
                                   f"Expected {expected_reads[(node_id, key)]}, got {found_value}")
    
    # Ask each node to prepare
    for node in nodes:
        node_id = node["node_id"]
        if node_id in node_operations:
            ops = node_operations[node_id]
            try:
                prepare_results[node_id] = node["can_commit"](transaction_id, ops)
            except Exception as e:
                prepare_results[node_id] = False
    
    # Phase 2: Commit or Rollback based on prepare results
    all_prepared = all(prepare_results.values())
    
    if all_prepared:
        # Commit phase
        for node in nodes:
            node_id = node["node_id"]
            if node_id in node_operations:
                ops = node_operations[node_id]
                node["commit"](transaction_id, ops)
        return True
    else:
        # Rollback phase
        for node in nodes:
            node_id = node["node_id"]
            if node_id in node_operations:
                ops = node_operations[node_id]
                node["rollback"](transaction_id, ops)
        return False