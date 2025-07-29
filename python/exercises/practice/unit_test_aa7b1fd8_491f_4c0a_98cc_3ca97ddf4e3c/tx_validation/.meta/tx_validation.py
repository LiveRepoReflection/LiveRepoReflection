def validate_transactions(transactions):
    # Step 1: Check consistency for each transaction.
    # For every transaction_id, all entries must have same (operation, data)
    txn_consistency = {}
    for txn_id, node_id, op, data in transactions:
        # If this transaction id is seen first time, store the (op, data)
        if txn_id not in txn_consistency:
            txn_consistency[txn_id] = (op, data)
        else:
            # If already exists, then ensure consistency.
            if txn_consistency[txn_id] != (op, data):
                return False

    # Step 2: Check for conflicts across transactions on same (node, data)
    # Group transactions by (node, data) and record operations by distinct transaction id.
    node_data_map = {}
    for txn_id, node_id, op, data in transactions:
        key = (node_id, data)
        if key not in node_data_map:
            node_data_map[key] = {txn_id: op}
        else:
            # Only add if transaction id is not already accounted.
            if txn_id not in node_data_map[key]:
                node_data_map[key][txn_id] = op

    # For each (node, data), if more than one distinct transaction is present, 
    # all operations must be READ for there to be no conflict.
    for transactions_on_node in node_data_map.values():
        if len(transactions_on_node) > 1:
            # If any op is not "READ", then conflict exists.
            for op in transactions_on_node.values():
                if op != "READ":
                    return False

    return True