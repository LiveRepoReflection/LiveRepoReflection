def allocate(n, k, demands, capacities, edges):
    # Initialize allocation array, where allocation[i] will store the cluster assigned to node i.
    allocation = [-1] * n
    # Create a copy of capacities to track remaining capacity for each cluster.
    remaining_capacity = capacities[:]

    # Simple Greedy Approach:
    # Sort nodes in descending order based on their computational demand.
    nodes_sorted = sorted(range(n), key=lambda i: demands[i], reverse=True)

    for node in nodes_sorted:
        assigned = False
        # For each node, try to assign it to the cluster with the largest remaining capacity that can accommodate it.
        clusters_sorted = sorted(range(k), key=lambda j: remaining_capacity[j], reverse=True)
        for cluster in clusters_sorted:
            if remaining_capacity[cluster] >= demands[node]:
                allocation[node] = cluster
                remaining_capacity[cluster] -= demands[node]
                assigned = True
                break
        # In case no cluster can accommodate the node (should not happen in valid test cases),
        # assign to the cluster with the most remaining capacity (this is a fallback).
        if not assigned:
            allocation[node] = clusters_sorted[0]
            remaining_capacity[clusters_sorted[0]] -= demands[node]
            
    return allocation