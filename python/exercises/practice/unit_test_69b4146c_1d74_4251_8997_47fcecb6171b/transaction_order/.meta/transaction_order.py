from collections import defaultdict, deque
import heapq

def order_transactions(N, transactions, dependencies):
    """
    Determine a global, consistent order for executing transactions given dependencies and conflicts.
    
    Parameters:
    - N: int, number of nodes.
    - transactions: list of tuples (transaction_id, participating_nodes, operations)
    - dependencies: list of tuples (A, B), meaning transaction A depends on B (B must come before A)
    
    Returns:
    - A list of transaction_id in a valid execution order, or an empty list if no valid order exists.
    """
    # Build a set of all transaction ids and mapping for quick lookup
    tx_ids = set()
    for tx in transactions:
        tx_ids.add(tx[0])
    
    # Build the dependency graph: edge from X -> Y means X must come before Y
    graph = defaultdict(set)
    indegree = {tx_id: 0 for tx_id in tx_ids}
    
    # Add dependency edges: for each (A, B), B should come before A, so edge from B -> A.
    for a, b in dependencies:
        # Only consider valid transaction ids
        if a in tx_ids and b in tx_ids:
            # Avoid adding duplicate edge
            if a not in graph[b]:
                graph[b].add(a)
                indegree[a] += 1

    # Add conflict resolution edges.
    # Two transactions conflict if they share at least one node and have at least one common operation.
    # For each node, for each operation, order transactions (by transaction_id ascending) that include that op.
    # This ensures a consistent ordering among conflicting transactions.
    node_op_to_txs = defaultdict(list)
    for transaction_id, participating_nodes, operations in transactions:
        for node in participating_nodes:
            for op in operations:
                node_op_to_txs[(node, op)].append(transaction_id)
    
    # For each (node, op) key, sort the transactions and add edge from earlier to later.
    for key, tx_list in node_op_to_txs.items():
        if len(tx_list) > 1:
            # Remove duplicates if any and sort
            unique_txs = sorted(set(tx_list))
            for i in range(len(unique_txs) - 1):
                u = unique_txs[i]
                v = unique_txs[i+1]
                # Avoid adding edge if already present via dependency
                if v not in graph[u]:
                    graph[u].add(v)
                    indegree[v] += 1

    # Topological sort using a heap to enforce deterministic tie-breaking (lowest transaction id first)
    min_heap = []
    for tx in indegree:
        if indegree[tx] == 0:
            heapq.heappush(min_heap, tx)
    
    order = []
    while min_heap:
        current = heapq.heappop(min_heap)
        order.append(current)
        for neighbor in sorted(graph[current]):  # sort for deterministic order
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(min_heap, neighbor)
    
    # If not all transactions are processed, there is a cycle
    if len(order) != len(tx_ids):
        return []
    
    return order