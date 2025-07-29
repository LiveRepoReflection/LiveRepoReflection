def optimize_supply_network(factories, demand_centers, transportation_costs):
    # Build dictionaries for easy lookup
    fac_dict = {}
    for fac in factories:
        fac_dict[fac["factory_id"]] = {
            "capacity": fac["capacity"],
            "operating_cost": fac["operating_cost"],
            "original_capacity": fac["capacity"],
            "operational": False,
        }

    demand_dict = {}
    for dc in demand_centers:
        demand_dict[dc["demand_center_id"]] = dc["demand"]

    # Check if overall capacity (even if not all routes are available) is enough to meet the total demand.
    total_capacity = sum(fac["capacity"] for fac in fac_dict.values())
    total_demand = sum(demand_dict.values())
    if total_capacity < total_demand:
        return None

    # For each demand center, check if there is at least one factory that can ship to it.
    demand_reachable = {dc: False for dc in demand_dict}
    for (fac_id, dc_id) in transportation_costs:
        if fac_id in fac_dict and dc_id in demand_dict:
            demand_reachable[dc_id] = True
    for dc_id, reachable in demand_reachable.items():
        if not reachable:
            return None

    # Initialize shipments result dictionary.
    shipments = {}
    for fac_id in fac_dict:
        shipments[fac_id] = {dc["demand_center_id"]: 0 for dc in demand_centers}

    # Greedy iterative assignment.
    # While any demand remains, choose a shipment with the smallest effective cost.
    # Effective cost is defined as transportation cost plus a penalty if the factory is not operational.
    # The penalty is computed as (operating_cost / original_capacity) so that larger factories spread out the fixed cost.
    progress = True
    while any(qty > 0 for qty in demand_dict.values()) and progress:
        best_eff_cost = None
        best_pair = None
        # Iterate over every (factory, demand center) pair that has a defined transportation route,
        # and where the factory has capacity and the demand center still needs product.
        for fac_id, fac_info in fac_dict.items():
            if fac_info["capacity"] <= 0:
                continue
            for dc_id, rem_demand in demand_dict.items():
                if rem_demand <= 0:
                    continue
                if (fac_id, dc_id) not in transportation_costs:
                    continue
                t_cost = transportation_costs[(fac_id, dc_id)]
                penalty = 0.0
                if not fac_info["operational"]:
                    # Spread the fixed cost over the factory's original capacity:
                    penalty = fac_info["operating_cost"] / fac_info["original_capacity"]
                eff_cost = t_cost + penalty
                if best_eff_cost is None or eff_cost < best_eff_cost:
                    best_eff_cost = eff_cost
                    best_pair = (fac_id, dc_id, t_cost)
        # If no eligible pair found, break the loop (infeasible)
        if best_pair is None:
            progress = False
            break

        fac_id, dc_id, t_cost = best_pair
        fac_info = fac_dict[fac_id]
        # Determine how many units can be assigned
        qty_to_assign = min(fac_info["capacity"], demand_dict[dc_id])
        # Assign shipment
        shipments[fac_id][dc_id] += qty_to_assign
        # Update remaining capacity and demand
        fac_info["capacity"] -= qty_to_assign
        demand_dict[dc_id] -= qty_to_assign
        # Mark the factory as operational if not already
        if not fac_info["operational"]:
            fac_info["operational"] = True

    # Check if all demands have been satisfied
    if any(rem > 0 for rem in demand_dict.values()):
        return None

    # Build the final result dictionary
    result = {"factories": {}}
    for fac in factories:
        fac_id = fac["factory_id"]
        fac_info = fac_dict[fac_id]
        result["factories"][fac_id] = {
            "operational": fac_info["operational"],
            "shipments": shipments[fac_id]
        }
    return result


if __name__ == "__main__":
    # Example usage (the provided test cases will invoke optimize_supply_network directly)
    factories = [
        {"factory_id": "F1", "capacity": 100, "operating_cost": 500},
        {"factory_id": "F2", "capacity": 50, "operating_cost": 300},
    ]
    demand_centers = [
        {"demand_center_id": "D1", "demand": 70},
        {"demand_center_id": "D2", "demand": 80},
    ]
    transportation_costs = {
        ("F1", "D1"): 5,
        ("F1", "D2"): 7,
        ("F2", "D1"): 8,
        ("F2", "D2"): 4,
    }
    result = optimize_supply_network(factories, demand_centers, transportation_costs)
    print(result)