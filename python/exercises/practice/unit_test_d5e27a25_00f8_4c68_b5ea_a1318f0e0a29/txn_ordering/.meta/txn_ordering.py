from collections import defaultdict, deque

def order_transactions(operations):
    # If operations is empty, return empty list
    if not operations:
        return []
        
    # Gather all unique transactions from the operations
    all_txns = set()
    for tx, _, _, _ in operations:
        all_txns.add(tx)
        
    # Build a dependency graph: for each (node, data_item), add edge from earlier transaction to later transaction
    # if there is a conflict (i.e., at least one of the operations is a WRITE).
    graph = defaultdict(set)
    indegree = {txn: 0 for txn in all_txns}
    
    # Group operations by (node, data_item) with indices preserving the order from the input
    groups = defaultdict(list)
    for index, (tx, node, data_item, op_type) in enumerate(operations):
        groups[(node, data_item)].append((index, tx, op_type))
    
    # For each group, add dependencies based on operation order
    for key, op_list in groups.items():
        # Sort the list by the original index (should already be sorted)
        op_list.sort(key=lambda x: x[0])
        n = len(op_list)
        for i in range(n - 1):
            index_i, tx_i, op_i = op_list[i]
            for j in range(i + 1, n):
                index_j, tx_j, op_j = op_list[j]
                # Skip if the same transaction (no dependency on itself)
                if tx_i == tx_j:
                    continue
                # If either operation is a WRITE, it's a conflict
                if op_i == "WRITE" or op_j == "WRITE":
                    # Add edge from tx_i to tx_j if not already present
                    if tx_j not in graph[tx_i]:
                        graph[tx_i].add(tx_j)
                        indegree[tx_j] += 1
                    # Once a dependency is added between these two in one group, we can move on to next operation
                    # because the relative order among these transactions is already fixed by the first conflict.
                    break
    
    # Topological sort using Kahn's algorithm
    # Initialize a queue with transactions that have zero incoming dependencies
    queue = deque()
    for txn, deg in indegree.items():
        if deg == 0:
            queue.append(txn)
            
    sorted_txns = []
    while queue:
        current = queue.popleft()
        sorted_txns.append(current)
        for neighbor in graph[current]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
    
    # If not all transactions are sorted, a cycle exists and no valid order is possible.
    if len(sorted_txns) != len(all_txns):
        return []
    
    return sorted_txns