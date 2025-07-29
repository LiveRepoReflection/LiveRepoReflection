def optimize_transactions(N, M, P, C, Adj, T):
    """
    Optimize the ordering of services within each transaction to minimize the worst-case latency.
    
    Args:
        N: Number of services (1 <= N <= 25)
        M: Number of transactions (1 <= M <= 100)
        P: List of prepare costs for each service
        C: List of commit costs for each service
        Adj: N x N adjacency matrix representing network topology
        T: List of M transactions, each being a list of service indices
    
    Returns:
        List of M lists, each representing the optimized ordering of services for a transaction
    """
    # First, compute shortest paths between all pairs of nodes
    # We'll use the Floyd-Warshall algorithm
    shortest_paths = compute_shortest_paths(Adj, N)
    
    # For each transaction, optimize the ordering of services
    optimized_transactions = []
    
    for transaction in T:
        # If transaction has 0 or 1 services, no optimization needed
        if len(transaction) <= 1:
            optimized_transactions.append(transaction[:])
            continue
        
        # Optimize this transaction
        optimized_order = optimize_transaction_order(transaction, P, C, shortest_paths)
        optimized_transactions.append(optimized_order)
    
    return optimized_transactions

def compute_shortest_paths(Adj, N):
    """
    Compute shortest paths between all pairs of nodes using Floyd-Warshall algorithm.
    """
    # Initialize shortest paths with adjacency matrix
    dist = [row[:] for row in Adj]
    
    # Set diagonal to 0 (distance from node to itself)
    for i in range(N):
        dist[i][i] = 0
    
    # Set unreachable nodes to infinity
    for i in range(N):
        for j in range(N):
            if i != j and dist[i][j] == 0:
                dist[i][j] = float('inf')
    
    # Floyd-Warshall algorithm
    for k in range(N):
        for i in range(N):
            for j in range(N):
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    
    return dist

def optimize_transaction_order(transaction, P, C, shortest_paths):
    """
    Optimize the ordering of services for a single transaction.
    
    The strategy is to:
    1. Sort services by communication cost + prepare cost (to minimize latency in failure case)
    2. Then consider the impact on successful commit case
    """
    # Score each service based on its impact on latency
    service_scores = []
    
    for service_idx in transaction:
        # Communication cost from DTC (node 0) to this service
        comm_cost = shortest_paths[0][service_idx]
        
        # Prepare and commit costs for this service
        prepare_cost = P[service_idx]
        commit_cost = C[service_idx]
        
        # Score for failure case: communication cost + prepare cost
        # We want services with high failure impact to be checked first
        failure_impact = comm_cost + prepare_cost
        
        # Score for success case: communication cost + commit cost
        success_impact = comm_cost + commit_cost
        
        # Combined score (prioritize failure impact more)
        # We use a weighted combination to prioritize services with high failure impact
        combined_score = failure_impact * 2 + success_impact
        
        service_scores.append((combined_score, service_idx))
    
    # Sort services by their scores in descending order
    # Higher scores (higher impact) should be checked first to minimize worst-case latency
    service_scores.sort(reverse=True)
    
    # Extract the optimized order
    optimized_order = [score_service[1] for score_service in service_scores]
    
    return optimized_order

def calculate_transaction_latency(transaction_order, P, C, shortest_paths, fail_index=None):
    """
    Calculate the latency for a transaction with a specific service ordering.
    
    Args:
        transaction_order: List of service indices in the order they'll be processed
        P: List of prepare costs
        C: List of commit costs
        shortest_paths: Matrix of shortest paths between all pairs of nodes
        fail_index: Index in transaction_order where preparation fails (None for success case)
    
    Returns:
        The latency for this transaction
    """
    # DTC is co-located with service 0
    dtc_node = 0
    
    # Calculate max communication cost for prepare messages
    max_prepare_comm = max(shortest_paths[dtc_node][service] for service in transaction_order)
    
    # If a failure occurs during prepare phase
    if fail_index is not None:
        failing_service = transaction_order[fail_index]
        # Latency = comm cost + prepare cost of the failing service
        return max_prepare_comm + P[failing_service]
    
    # Success case (all services prepare successfully)
    # Max prepare cost across all services in the transaction
    max_prepare_cost = max(P[service] for service in transaction_order)
    
    # Max communication cost for commit messages
    max_commit_comm = max(shortest_paths[dtc_node][service] for service in transaction_order)
    
    # Max commit cost across all services
    max_commit_cost = max(C[service] for service in transaction_order)
    
    # Total latency for success case
    return max_prepare_comm + max_prepare_cost + max_commit_comm + max_commit_cost