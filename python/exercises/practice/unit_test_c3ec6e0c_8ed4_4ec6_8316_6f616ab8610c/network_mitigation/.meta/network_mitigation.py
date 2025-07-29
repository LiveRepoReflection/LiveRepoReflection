def mitigate_congestion(N, edges, capacity):
    """
    Mitigates network congestion by reducing bandwidth on edges while:
    1. Minimizing total reduction amount
    2. Prioritizing higher bandwidth edges
    3. Ensuring total bandwidth ≤ capacity
    """
    # Calculate current total bandwidth
    total_bandwidth = sum(w for _, _, w in edges)
    
    # If already within capacity, return empty list
    if total_bandwidth <= capacity:
        return []
    
    # Calculate required reduction
    required_reduction = total_bandwidth - capacity
    
    # Sort edges by bandwidth descending (prioritize higher bandwidth edges)
    sorted_edges = sorted(edges, key=lambda x: -x[2])
    
    reductions = []
    remaining_reduction = required_reduction
    
    for u, v, w in sorted_edges:
        if remaining_reduction <= 0:
            break
        
        # Calculate possible reduction for this edge
        possible_reduction = min(w, remaining_reduction)
        reductions.append((u, v, possible_reduction))
        remaining_reduction -= possible_reduction
    
    return reductions