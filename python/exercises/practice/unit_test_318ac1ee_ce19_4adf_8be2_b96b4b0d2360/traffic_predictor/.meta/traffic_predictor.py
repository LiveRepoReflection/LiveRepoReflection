def predict_traffic_flow(N, edges, current_traffic, historical_data, events, time_slices):
    # Build a mapping for current traffic for quick lookup.
    current_traffic_dict = {}
    for u, v, volume in current_traffic:
        current_traffic_dict[(u, v)] = volume

    # Build a mapping for edges capacity lookup.
    capacity_dict = {}
    for u, v, capacity in edges:
        capacity_dict[(u, v)] = capacity

    # Prepare baseline for each road segment using current traffic if available, otherwise average historical data.
    baseline_dict = {}
    for u, v, capacity in edges:
        if (u, v) in current_traffic_dict:
            baseline_dict[(u, v)] = current_traffic_dict[(u, v)]
        else:
            # Use average from historical data, rounded down to integer.
            hist = historical_data.get((u, v), [])
            if hist:
                baseline_dict[(u, v)] = int(sum(hist) / len(hist))
            else:
                baseline_dict[(u, v)] = 0

    # Initialize result dictionary.
    result = {}
    
    # For each time slice, compute predicted value for each edge.
    for t in time_slices:
        for u, v, capacity in edges:
            baseline = baseline_dict[(u, v)]
            # Compute cumulative impact factor from events affecting this road's origin node.
            total_factor = 0.0
            for start_time, end_time, impact_node, impact_factor in events:
                if impact_node == u and start_time <= t < end_time:
                    total_factor += impact_factor
            # Calculate prediction.
            prediction = int(baseline * (1 + total_factor))
            if prediction < 0:
                prediction = 0
            if prediction > capacity:
                prediction = capacity
            result[(u, v, t)] = prediction

    return result