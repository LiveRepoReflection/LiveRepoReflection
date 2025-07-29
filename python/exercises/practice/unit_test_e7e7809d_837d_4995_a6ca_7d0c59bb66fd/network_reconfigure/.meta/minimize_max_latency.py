def minimize_max_latency(num_servers, edges, critical_edges):
    # If there are no servers, reconfiguration cannot be possible.
    if num_servers <= 0:
        return -1

    # Build a dictionary mapping an unordered pair (u, v) of servers to the minimum latency among edges in the original network.
    # For consistency, represent each pair as a tuple in sorted order.
    edge_latency = {}
    for u, v, w in edges:
        pair = tuple(sorted((u, v)))
        if pair in edge_latency:
            if w < edge_latency[pair]:
                edge_latency[pair] = w
        else:
            edge_latency[pair] = w

    # Process the critical edges and extract the lower bound latency for each required connection.
    # Use a set to avoid duplicate processing.
    critical_bounds = []
    seen = set()
    for u, v in critical_edges:
        pair = tuple(sorted((u, v)))
        if pair in seen:
            continue
        seen.add(pair)
        # If there exists at least one connection in original edges for this pair, we must use at least its minimum latency.
        # Otherwise, we can add a new edge with latency 0.
        if pair in edge_latency:
            critical_bounds.append(edge_latency[pair])
        else:
            critical_bounds.append(0)

    # We can always add additional edges with 0 latency to connect the network.
    # The reconfigured network must include all critical edges with their lower bound latencies; hence
    # the maximum latency in the reconfiguration is determined by the highest lower bound among the critical edges.
    if not critical_bounds:
        # If there are no critical edges, we can construct a connected network with 0 latency edges.
        return 0
    else:
        return max(critical_bounds)
    

if __name__ == '__main__':
    # For simple ad-hoc testing if necessary.
    # This code block is for local debugging and will not be used by the unit tests.
    num_servers = 3
    edges = [(0, 1, 5), (1, 2, 3), (0, 2, 10)]
    critical_edges = [(0, 1), (1, 2)]
    result = minimize_max_latency(num_servers, edges, critical_edges)
    print("Minimum maximum latency:", result)