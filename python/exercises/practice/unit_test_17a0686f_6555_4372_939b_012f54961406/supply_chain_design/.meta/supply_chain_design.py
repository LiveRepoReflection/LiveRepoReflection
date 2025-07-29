def optimize_supply_chain(factories, warehouses, customer_demand, transportation_costs):
    # Check total demand versus production capacity
    total_demand = sum(c["demand"] for c in customer_demand)
    total_production_capacity = sum(f["production_capacity"] for f in factories)
    if total_production_capacity < total_demand:
        return {
            "selected_factories": [],
            "selected_warehouses": [],
            "flow": {},
            "total_cost": float('inf')
        }

    flow = {}
    selected_factories = set()
    selected_warehouses = set()
    total_cost = 0.0

    # If no warehouses are provided, assign factories directly to customers.
    if len(warehouses) == 0:
        # Maintain remaining capacity per factory.
        factories_rem = {f["location_id"]: f["production_capacity"] for f in factories}
        factories_info = {f["location_id"]: f for f in factories}

        for cust in customer_demand:
            cust_id = cust["location_id"]
            remaining_demand = cust["demand"]
            while remaining_demand > 0:
                best_factory = None
                best_cost = float('inf')
                # Find the factory that offers the cheapest combined production and transportation cost.
                for f in factories:
                    fid = f["location_id"]
                    if factories_rem[fid] > 0:
                        trans_cost = transportation_costs.get(fid, {}).get(cust_id, float('inf'))
                        current_cost = f["production_cost_per_unit"] + trans_cost
                        if current_cost < best_cost:
                            best_cost = current_cost
                            best_factory = f
                if best_factory is None:
                    return {
                        "selected_factories": [],
                        "selected_warehouses": [],
                        "flow": {},
                        "total_cost": float('inf')
                    }
                fid = best_factory["location_id"]
                available = factories_rem[fid]
                allocate = min(available, remaining_demand)
                factories_rem[fid] -= allocate
                remaining_demand -= allocate
                flow[(fid, cust_id)] = flow.get((fid, cust_id), 0) + allocate
                total_cost += allocate * (best_factory["production_cost_per_unit"] +
                                          transportation_costs.get(fid, {}).get(cust_id, float('inf')))
                selected_factories.add(fid)
        # Add fixed costs of factories used.
        for fid in selected_factories:
            total_cost += factories_info[fid]["fixed_cost"]

        return {
            "selected_factories": sorted(list(selected_factories)),
            "selected_warehouses": [],
            "flow": flow,
            "total_cost": total_cost
        }

    else:
        # When warehouses exist, we route production through warehouses.
        # Step 1: Assign customer demands to warehouses.
        # Maintain warehouse remaining storage capacity.
        wh_rem = {w["location_id"]: w["storage_capacity"] for w in warehouses}
        warehouses_info = {w["location_id"]: w for w in warehouses}
        wh_to_customer_flow = {}  # key: (warehouse, customer)

        for cust in customer_demand:
            cust_id = cust["location_id"]
            demand_remaining = cust["demand"]
            # For each warehouse, calculate effective cost: transportation cost from warehouse
            # to customer plus storage cost per unit.
            warehouse_options = []
            for w in warehouses:
                w_id = w["location_id"]
                trans_cost = transportation_costs.get(w_id, {}).get(cust_id, float('inf'))
                effective_cost = trans_cost + w["storage_cost_per_unit"]
                warehouse_options.append((effective_cost, w))
            # Sort warehouses by effective cost (cheapest first)
            warehouse_options.sort(key=lambda x: x[0])
            # Allocate customer demand across warehouses in order of increasing effective cost.
            for cost_val, w in warehouse_options:
                w_id = w["location_id"]
                if demand_remaining <= 0:
                    break
                if wh_rem[w_id] > 0:
                    allocate = min(wh_rem[w_id], demand_remaining)
                    wh_rem[w_id] -= allocate
                    demand_remaining -= allocate
                    wh_to_customer_flow[(w_id, cust_id)] = wh_to_customer_flow.get((w_id, cust_id), 0) + allocate
                    total_cost += allocate * (transportation_costs.get(w_id, {}).get(cust_id, float('inf')) +
                                               w["storage_cost_per_unit"])
                    selected_warehouses.add(w_id)
            if demand_remaining > 0:
                # Not enough warehouse storage capacity to meet customer demand.
                return {
                    "selected_factories": [],
                    "selected_warehouses": [],
                    "flow": {},
                    "total_cost": float('inf')
                }
        # Add fixed costs of warehouses that are used.
        for w_id in selected_warehouses:
            total_cost += warehouses_info[w_id]["fixed_cost"]

        # Step 2: Supply each warehouse from factories.
        # Compute total demand for each warehouse.
        warehouse_demand = {}
        for (w_id, cust_id), units in wh_to_customer_flow.items():
            warehouse_demand[w_id] = warehouse_demand.get(w_id, 0) + units

        factories_rem = {f["location_id"]: f["production_capacity"] for f in factories}
        factories_info = {f["location_id"]: f for f in factories}
        factory_to_wh_flow = {}  # key: (factory, warehouse)

        for w_id, demand in warehouse_demand.items():
            demand_remaining = demand
            while demand_remaining > 0:
                best_factory = None
                best_cost = float('inf')
                for f in factories:
                    fid = f["location_id"]
                    if factories_rem[fid] > 0:
                        trans_cost = transportation_costs.get(fid, {}).get(w_id, float('inf'))
                        current_cost = f["production_cost_per_unit"] + trans_cost
                        if current_cost < best_cost:
                            best_cost = current_cost
                            best_factory = f
                if best_factory is None:
                    return {
                        "selected_factories": [],
                        "selected_warehouses": [],
                        "flow": {},
                        "total_cost": float('inf')
                    }
                fid = best_factory["location_id"]
                available = factories_rem[fid]
                allocate = min(available, demand_remaining)
                factories_rem[fid] -= allocate
                demand_remaining -= allocate
                factory_to_wh_flow[(fid, w_id)] = factory_to_wh_flow.get((fid, w_id), 0) + allocate
                total_cost += allocate * (best_factory["production_cost_per_unit"] +
                                          transportation_costs.get(fid, {}).get(w_id, float('inf')))
                selected_factories.add(fid)
        # Add fixed costs of factories used.
        for fid in selected_factories:
            total_cost += factories_info[fid]["fixed_cost"]

        # Combine flows from factories to warehouses and from warehouses to customers.
        combined_flow = {}
        for key, value in factory_to_wh_flow.items():
            combined_flow[key] = value
        for key, value in wh_to_customer_flow.items():
            combined_flow[key] = value

        return {
            "selected_factories": sorted(list(selected_factories)),
            "selected_warehouses": sorted(list(selected_warehouses)),
            "flow": combined_flow,
            "total_cost": total_cost
        }


if __name__ == '__main__':
    # This block can be used for simple manual testing.
    factories = [{
        "location_id": "F1",
        "production_capacity": 100,
        "production_cost_per_unit": 1.0,
        "fixed_cost": 50.0
    }]
    warehouses = [{
        "location_id": "W1",
        "storage_capacity": 100,
        "storage_cost_per_unit": 0.5,
        "fixed_cost": 30.0
    }]
    customer_demand = [{
        "location_id": "C1",
        "demand": 50
    }]
    transportation_costs = {
        "F1": {"W1": 0.5, "C1": 2.0},
        "W1": {"C1": 0.5},
        "C1": {}
    }
    result = optimize_supply_chain(factories, warehouses, customer_demand, transportation_costs)
    print(result)