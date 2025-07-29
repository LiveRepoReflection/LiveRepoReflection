def select_data_centers(locations, regions, budget, latency_threshold):
    # Convert regions list to a dictionary for easy lookup of demand.
    region_demand = {region_id: demand for region_id, demand in regions}
    # Sort locations by build_cost to aid branch and bound
    sorted_locations = sorted(locations, key=lambda x: x[1])
    
    best_solution = []
    best_cost = float("inf")
    
    # initial latencies: for each region, set to inf (unreachable)
    initial_latencies = {r: float("inf") for r in region_demand}
    
    def search(i, selected, current_cost, current_latencies):
        nonlocal best_solution, best_cost
        # Prune if cost already exceeds budget or current branch is no better than best found.
        if current_cost > budget or current_cost >= best_cost:
            return
        # If we've considered all locations, evaluate this subset.
        if i == len(sorted_locations):
            total_demand = 0
            weighted_latency = 0
            for r, demand in region_demand.items():
                # If a region is unreachable, skip candidate.
                if current_latencies[r] == float("inf"):
                    return
                total_demand += demand
                weighted_latency += demand * current_latencies[r]
            # Calculate the weighted average latency.
            if total_demand == 0:
                return
            average_latency = weighted_latency / total_demand
            # Check if latency constraint is satisfied.
            if average_latency <= latency_threshold:
                if current_cost < best_cost:
                    best_cost = current_cost
                    best_solution = selected.copy()
            return

        # Option 1: Do not take the current location.
        search(i + 1, selected, current_cost, current_latencies)
        
        # Option 2: Take the current location.
        loc_id, cost, latency_profiles = sorted_locations[i]
        new_cost = current_cost + cost
        if new_cost > budget:
            return
        # Update the current latencies with the latency profiles offered by the new location.
        new_latencies = current_latencies.copy()
        for r in region_demand:
            if r in latency_profiles:
                new_latencies[r] = min(new_latencies[r], latency_profiles[r])
        selected.append(loc_id)
        search(i + 1, selected, new_cost, new_latencies)
        selected.pop()
    
    search(0, [], 0, initial_latencies)
    return best_solution