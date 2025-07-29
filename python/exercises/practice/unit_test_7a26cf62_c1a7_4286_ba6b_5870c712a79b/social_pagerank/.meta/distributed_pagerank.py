def distributed_pagerank(K, nodes, N, iterations):
    d = 0.85
    # Initialize PageRank: Using a list index corresponds to user id
    pr = [1.0 / N for _ in range(N)]

    for _ in range(iterations):
        # Prepare contributions and dangling mass
        contributions = [0.0 for _ in range(N)]
        dangling_mass = 0.0

        # Simulate each node's computation and message passing
        for node in nodes:
            local_users = node.get('users', [])
            local_edges = node.get('edges', {})
            for user in local_users:
                pr_value = pr[user]
                # Check if user has outgoing edges: If not present in local_edges or empty list, treat as dangling.
                if user in local_edges and local_edges[user]:
                    out_links = local_edges[user]
                    contribution = pr_value / len(out_links)
                    for target in out_links:
                        # Accumulate contribution for target user
                        contributions[target] += contribution
                else:
                    # Dangling node contributes its PageRank uniformly to all nodes
                    dangling_mass += pr_value

        # Distribute dangling mass evenly
        dangling_distribution = dangling_mass / N

        # Compute new PageRank for each user
        new_pr = [0.0 for _ in range(N)]
        for i in range(N):
            new_pr[i] = (1 - d) / N + d * (contributions[i] + dangling_distribution)
        pr = new_pr

    # Return the final PageRank scores as a dictionary mapping user id to score
    return {i: pr[i] for i in range(N)}