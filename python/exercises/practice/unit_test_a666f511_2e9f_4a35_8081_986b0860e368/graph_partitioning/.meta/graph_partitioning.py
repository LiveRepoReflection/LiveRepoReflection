import random

def partition_graph(n, edges, k):
    # Build the graph as an adjacency list.
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
        
    # Compute the degree of each node and total edge count m.
    degrees = [len(neighbors) for neighbors in graph]
    m = sum(degrees) // 2  # each edge counted twice

    if m == 0:
        # If there are no edges, assign communities in a round-robin manner.
        return [i % k for i in range(n)]
    
    # Initialize community assignments randomly.
    communities = [random.randint(0, k - 1) for _ in range(n)]
    
    # Compute the total degree for each community.
    comm_degree = [0] * k
    for i in range(n):
        comm_degree[communities[i]] += degrees[i]
        
    # Set the maximum number of iterations for local optimization.
    max_iter = 50

    for _ in range(max_iter):
        improved = False
        # Process nodes in a random order to avoid bias.
        order = list(range(n))
        random.shuffle(order)
        for i in order:
            current_comm = communities[i]
            best_comm = current_comm
            best_gain = 0  # Only move if there is positive gain

            # Count neighbors of i in each community.
            neighbor_counts = [0] * k
            for neighbor in graph[i]:
                neighbor_counts[communities[neighbor]] += 1

            # Remove node i from its current community temporarily.
            comm_degree[current_comm] -= degrees[i]

            # Evaluate potential gain for moving node i to each candidate community.
            for candidate in range(k):
                if candidate == current_comm:
                    continue
                # Approximate change in modularity:
                # Gain = (number of edges from i to nodes in candidate) - expected edges
                gain = neighbor_counts[candidate] - (degrees[i] * comm_degree[candidate]) / (2 * m)
                if gain > best_gain:
                    best_gain = gain
                    best_comm = candidate

            if best_comm != current_comm:
                # Move node i to the new community.
                communities[i] = best_comm
                comm_degree[best_comm] += degrees[i]
                improved = True
            else:
                # Revert the temporary removal.
                comm_degree[current_comm] += degrees[i]

        if not improved:
            # Terminate early if no improvement is possible.
            break

    return communities