import heapq
from collections import defaultdict

def order_transactions(transactions):
    # Build dependency graph and in-degree count
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    timestamp_map = {}
    transaction_ids = set()
    
    # Initialize data structures
    for tx in transactions:
        tx_id = tx["transaction_id"]
        transaction_ids.add(tx_id)
        timestamp_map[tx_id] = tx["timestamp"]
        in_degree[tx_id] = 0  # Ensure all transactions are in in_degree

    for tx in transactions:
        tx_id = tx["transaction_id"]
        for dep in tx["dependencies"]:
            if dep not in transaction_ids:
                raise ValueError(f"Dependency {dep} not found in transactions")
            graph[dep].append(tx_id)
            in_degree[tx_id] += 1

    # Check for cycles
    if has_cycle(graph, transaction_ids):
        raise ValueError("Cycle detected in transaction dependencies")

    # Priority queue for ready transactions (using timestamp as priority)
    ready_heap = []
    for tx_id in transaction_ids:
        if in_degree[tx_id] == 0:
            heapq.heappush(ready_heap, (timestamp_map[tx_id], tx_id))

    result = []
    while ready_heap:
        _, tx_id = heapq.heappop(ready_heap)
        result.append(tx_id)
        
        for neighbor in graph[tx_id]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(ready_heap, (timestamp_map[neighbor], neighbor))

    if len(result) != len(transaction_ids):
        raise ValueError("Not all transactions could be ordered - possible missing dependencies")

    return result

def has_cycle(graph, transaction_ids):
    visited = set()
    recursion_stack = set()

    def dfs(node):
        if node in recursion_stack:
            return True
        if node in visited:
            return False

        visited.add(node)
        recursion_stack.add(node)

        for neighbor in graph.get(node, []):
            if dfs(neighbor):
                return True

        recursion_stack.remove(node)
        return False

    for node in transaction_ids:
        if node not in visited:
            if dfs(node):
                return True
    return False