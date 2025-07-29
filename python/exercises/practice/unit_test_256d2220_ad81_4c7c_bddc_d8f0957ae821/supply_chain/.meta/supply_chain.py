def optimize_supply_chain(warehouses, customer_zones, transportation_costs, fixed_warehouse_costs):
    """
    Optimize the supply chain to minimize total cost consisting of transportation costs and fixed warehouse costs.
    
    Parameters:
      warehouses: List of tuples (warehouse_id, capacity)
      customer_zones: List of tuples (zone_id, demand)
      transportation_costs: Dictionary with keys (warehouse_id, zone_id) and values cost per unit shipped.
      fixed_warehouse_costs: Dictionary with keys warehouse_id and values fixed cost if the warehouse is used.
      
    Returns:
      A dictionary with keys (warehouse_id, zone_id) and values representing the number of units shipped.
      
    Raises:
      ValueError: if total warehouse capacity is insufficient to meet total demand or if a customer zone
                  cannot be serviced due to missing transportation routes.
    """
    # Check feasibility: total capacity must meet total demand.
    total_capacity = sum(cap for _, cap in warehouses)
    total_demand = sum(demand for _, demand in customer_zones)
    if total_capacity < total_demand:
        raise ValueError("Insufficient capacity to meet total demand.")
    
    # Build quick lookups
    warehouse_capacity = {w_id: cap for w_id, cap in warehouses}
    zone_demand = {z_id: demand for z_id, demand in customer_zones}
    
    # For each zone, check at least one warehouse can serve it
    zone_to_warehouses = {}
    for z_id, demand in customer_zones:
        available = [w_id for w_id, cap in warehouses if (w_id, z_id) in transportation_costs]
        if not available:
            raise ValueError(f"Feasible plan cannot be formed due to missing transportation routes for zone {z_id}.")
        zone_to_warehouses[z_id] = available
    
    # Initialize remaining capacities and demands
    remaining_capacity = warehouse_capacity.copy()
    remaining_demand = zone_demand.copy()
    
    # Track if a warehouse has been opened (used at least one shipment)
    warehouse_open = {w_id: False for w_id, _ in warehouses}
    
    # Shipping plan: dictionary mapping (warehouse_id, zone_id) -> shipment amount
    plan = {}
    
    # We'll process zones in the order of their ids (the order can be modified based on strategy)
    zones = [z_id for z_id, _ in customer_zones]
    
    # Continue until all zone demands are satisfied
    # For robustness, run a loop until no changes can be made and demands remain unsatisfied.
    progress = True
    while any(remaining_demand[z] > 0 for z in zones) and progress:
        progress = False
        for z in zones:
            if remaining_demand[z] <= 0:
                continue
            # For zone z, determine the best warehouse to ship from:
            eligible_warehouses = []
            for w in zone_to_warehouses[z]:
                if remaining_capacity[w] > 0:
                    cost = transportation_costs[(w, z)]
                    # If the warehouse is not yet open, add an estimated per-unit fixed cost component.
                    if not warehouse_open[w]:
                        # Heuristic: distribute fixed cost over full capacity.
                        cost += fixed_warehouse_costs[w] / warehouse_capacity[w]
                    eligible_warehouses.append((cost, w))
            # If no eligible warehouse is found, then it's infeasible.
            if not eligible_warehouses:
                raise ValueError(f"Feasible plan cannot be formed for zone {z}.")
            # Select warehouse with minimum effective cost.
            eligible_warehouses.sort(key=lambda x: x[0])
            best_cost, best_warehouse = eligible_warehouses[0]
            # Determine the shipment amount
            amount = min(remaining_demand[z], remaining_capacity[best_warehouse])
            # Update the plan
            key = (best_warehouse, z)
            if key in plan:
                plan[key] += amount
            else:
                plan[key] = amount
            # Mark warehouse as opened if not already
            if not warehouse_open[best_warehouse]:
                warehouse_open[best_warehouse] = True
            # Update remaining capacity and demand
            remaining_capacity[best_warehouse] -= amount
            remaining_demand[z] -= amount
            progress = True

    # After the loop, if any demand is unsatisfied, then no feasible plan exists
    for z in zones:
        if remaining_demand[z] > 0:
            raise ValueError("Feasible plan cannot be formed due to insufficient routes or capacity.")

    return plan