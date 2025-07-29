def schedule_transactions(transaction_logs):
    # Gather all operations grouped by key (node, data)
    # Each operation is represented as a tuple: (timestamp, transaction_id, operation)
    key_ops = {}
    all_tids = set()
    for trans in transaction_logs:
        if not trans:
            continue
        for op in trans:
            tid, nid, di, op_type, ts = op
            all_tids.add(tid)
            key = (nid, di)
            if key not in key_ops:
                key_ops[key] = []
            key_ops[key].append((ts, tid, op_type))
    # Set to record transactions that must be aborted
    aborted = set()
    # Process each key independently
    for key, ops in key_ops.items():
        # Sort operations by timestamp
        ops.sort(key=lambda x: x[0])
        encountered_write = False
        winner_tid = None
        for ts, tid, op_type in ops:
            if not encountered_write:
                if op_type == 'W':
                    encountered_write = True
                    winner_tid = tid
                # If op is read and no write has been encountered, no conflict.
            else:
                # If a write has already been encountered, any subsequent operation from
                # a different transaction will cause that transaction to be aborted.
                if tid != winner_tid:
                    aborted.add(tid)
    # The committed transactions are those that were never aborted.
    committed = [tid for tid in all_tids if tid not in aborted]
    # To determine a serializable order, we order transactions by the order of their first appearance
    # in the transaction_logs. We'll build an order map from transaction log order.
    order_map = {}
    for trans in transaction_logs:
        if not trans:
            continue
        tid = trans[0][0]
        if tid not in order_map:
            order_map[tid] = len(order_map)
    # For any transaction that did not appear (edge case) assign a high order value.
    committed.sort(key=lambda tid: order_map.get(tid, float('inf')))
    return committed

if __name__ == "__main__":
    # Sample execution for debugging purposes.
    transaction_logs = [
        [(1, 1, 'A', 'W', 1), (1, 2, 'B', 'R', 3), (1, 1, 'C', 'R', 5)],
        [(2, 1, 'A', 'R', 2), (2, 2, 'C', 'W', 4), (2, 1, 'D', 'W', 6)],
        [(3, 2, 'B', 'W', 7), (3, 1, 'C', 'W', 8)],
    ]
    result = schedule_transactions(transaction_logs)
    print(result)