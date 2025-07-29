from collections import deque

def orchestrate_transaction(graph, operations, compensations):
    if not graph:
        return True

    # Build in-degree and adjacency list
    in_degree = {node: 0 for node in graph}
    adj_list = {node: [] for node in graph}

    for node in graph:
        for neighbor in graph[node]:
            adj_list[neighbor].append(node)
            in_degree[node] += 1

    # Initialize queue with nodes having 0 in-degree
    queue = deque([node for node in in_degree if in_degree[node] == 0])
    executed_order = []
    executed = set()
    failed = False

    # Topological sort with execution
    while queue:
        node = queue.popleft()

        # Execute the operation
        if not operations[node]():
            failed = True
            break

        executed.add(node)
        executed_order.append(node)

        # Update in-degree of neighbors
        for neighbor in adj_list[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if not failed:
        return True

    # Compensation phase
    for node in reversed(executed_order):
        compensations[node]()

    return False