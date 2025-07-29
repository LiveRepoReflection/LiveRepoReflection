import heapq
from collections import defaultdict

def build_dependency_graph(transactions):
    graph = {}
    for tx in transactions:
        tx_id = tx["id"]
        graph[tx_id] = []
    for tx in transactions:
        tx_id = tx["id"]
        for dep in tx["dependencies"]:
            # Append current transaction as dependent of dep
            if dep in graph:
                graph[dep].append(tx_id)
    return graph

def order_transactions(transactions):
    # Create a mapping from transaction id to transaction object.
    tx_map = {tx["id"]: tx for tx in transactions}
    # Compute indegree for each transaction.
    indegree = {tx["id"]: 0 for tx in transactions}
    for tx in transactions:
        for dep in tx["dependencies"]:
            if dep in indegree:
                indegree[tx["id"]] += 1

    # Build dependency graph.
    graph = build_dependency_graph(transactions)

    # Priority queue for transaction ids with indegree 0.
    # Priority: (number of distinct nodes used, transaction id alphabetical order)
    heap = []
    for tx in transactions:
        if indegree[tx["id"]] == 0:
            distinct_nodes = len({op["node"] for op in tx["operations"]})
            heapq.heappush(heap, (distinct_nodes, tx["id"]))

    order = []
    while heap:
        _, curr = heapq.heappop(heap)
        order.append(curr)
        # For each transaction that depends on current transaction.
        for dependent in graph[curr]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                dep_tx = tx_map[dependent]
                distinct_nodes = len({op["node"] for op in dep_tx["operations"]})
                heapq.heappush(heap, (distinct_nodes, dependent))
    # Check if all transactions are processed (i.e., no cycle).
    if len(order) != len(transactions):
        raise ValueError("Cycle detected in transaction dependencies")
    return order

def commit_protocol(transactions, vote_function):
    # Determine order of execution for transactions.
    order = order_transactions(transactions)
    tx_map = {tx["id"]: tx for tx in transactions}
    # Dictionary to keep the final status of each transaction.
    result = {}

    for tx_id in order:
        tx = tx_map[tx_id]
        # If any dependency is aborted, then abort this transaction.
        abort_due_to_dependency = False
        for dep in tx["dependencies"]:
            if dep in result and result[dep] == "aborted":
                abort_due_to_dependency = True
                break
        if abort_due_to_dependency:
            result[tx_id] = "aborted"
        else:
            # Simulate the voting process. If vote_function returns True, commit; otherwise abort.
            if vote_function(tx):
                result[tx_id] = "committed"
            else:
                result[tx_id] = "aborted"
    return result