def simulate_failures(n, edges, initial_failures, threshold):
    # Build incoming edge list for each node.
    incoming = {i: [] for i in range(n)}
    for u, v, w in edges:
        incoming[v].append((u, w))
    
    # Initialize the set of failed nodes.
    failed = set(initial_failures)
    
    # Propagate failures until the state is stable.
    changed = True
    while changed:
        changed = False
        new_failures = set()
        for node in range(n):
            if node in failed:
                continue
            # If the node has no incoming edges, it cannot fail by propagation.
            if not incoming[node]:
                continue
            total_weight = sum(w for _, w in incoming[node])
            failed_weight = sum(w for u, w in incoming[node] if u in failed)
            # A node fails if the sum of weights from failed incoming nodes is
            # greater than or equal to threshold * total_weight.
            if total_weight > 0 and failed_weight >= threshold * total_weight:
                new_failures.add(node)
        if new_failures:
            failed |= new_failures
            changed = True
    return sorted(failed)


if __name__ == "__main__":
    # Example run: the example from the problem description.
    n = 4
    edges = [(0, 1, 50), (0, 2, 30), (1, 2, 20), (2, 3, 60)]
    initial_failures = {0}
    threshold = 0.6
    result = simulate_failures(n, edges, initial_failures, threshold)
    print(result)