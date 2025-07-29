def min_total_cost(N, dependencies, bandwidth, cost, data_replication):
    total_cost = 0
    # Process each dependency request
    for req_dc, orig_dc, data_id, size in dependencies:
        # Determine candidate suppliers: replication providers plus the originally intended data center.
        candidates = set(data_replication.get(data_id, set()))
        candidates.add(orig_dc)
        
        # If the requiring data center already has the data, no transfer cost.
        best_cost_factor = float('inf')
        if req_dc in candidates:
            best_cost_factor = 0
        else:
            for supplier in candidates:
                # Verify that there is a valid connection: bandwidth must be positive and cost must be finite.
                if bandwidth[supplier][req_dc] > 0 and cost[supplier][req_dc] < best_cost_factor:
                    best_cost_factor = cost[supplier][req_dc]
        # If no candidate supplier can deliver the data, return infinite cost.
        if best_cost_factor == float('inf'):
            return float('inf')
        total_cost += best_cost_factor * size
    return total_cost