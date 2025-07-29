def assign_orders(warehouses, orders, product_dependencies):
    # Build a dependency lookup dictionary: product -> required warehouse
    dep_lookup = {}
    for prod, wh_id in product_dependencies:
        dep_lookup[prod] = wh_id

    # Initialize remaining capacities for each warehouse
    remaining_capacity = {wh_id: info["capacity"] for wh_id, info in warehouses.items()}

    # Initialize assignment dictionary: warehouse_id -> list of order_ids
    assignments = {wh_id: [] for wh_id in warehouses}

    # Pre-process orders: compute total volume and check for dependency requirements
    processed_orders = []
    for order in orders:
        total_volume = sum(order["volumes"])
        required_warehouse = None
        # Check dependency constraints: If any product requires a specific warehouse,
        # then all such dependencies must agree. If not, mark order as invalid (skip assignment).
        for prod in order["products"]:
            if prod in dep_lookup:
                if required_warehouse is None:
                    required_warehouse = dep_lookup[prod]
                elif required_warehouse != dep_lookup[prod]:
                    # Inconsistent dependency: skip order (do not assign)
                    required_warehouse = -1
                    break
        if required_warehouse == -1:
            continue
        processed_orders.append({
            "order_id": order["order_id"],
            "total_volume": total_volume,
            "preferred_warehouses": order["preferred_warehouses"],
            "required_warehouse": required_warehouse
        })

    # Separate orders with dependencies and without dependencies
    orders_with_dep = [order for order in processed_orders if order["required_warehouse"] is not None]
    orders_without_dep = [order for order in processed_orders if order["required_warehouse"] is None]

    # Process orders with dependency constraints first
    for order in orders_with_dep:
        req_wh = order["required_warehouse"]
        vol = order["total_volume"]
        # Check if the required warehouse exists and has sufficient capacity
        if req_wh in remaining_capacity and remaining_capacity[req_wh] >= vol:
            assignments[req_wh].append(order["order_id"])
            remaining_capacity[req_wh] -= vol
        # Else order cannot be assigned, so skip it

    # Process orders without dependency constraints.
    # Sort orders without dependency by descending volume to pack larger orders first.
    orders_without_dep.sort(key=lambda x: x["total_volume"], reverse=True)

    for order in orders_without_dep:
        vol = order["total_volume"]
        assigned = False
        # First, try to use a warehouse that is already used among the preferred list
        for wh in order["preferred_warehouses"]:
            if wh in remaining_capacity and remaining_capacity[wh] >= vol and assignments[wh]:
                assignments[wh].append(order["order_id"])
                remaining_capacity[wh] -= vol
                assigned = True
                break
        # If not assigned, try any warehouse in the preferred list that has enough capacity
        if not assigned:
            for wh in order["preferred_warehouses"]:
                if wh in remaining_capacity and remaining_capacity[wh] >= vol:
                    assignments[wh].append(order["order_id"])
                    remaining_capacity[wh] -= vol
                    assigned = True
                    break
        # If not assignable in preferred warehouses, try any warehouse that can fit the order.
        if not assigned:
            for wh in remaining_capacity:
                if remaining_capacity[wh] >= vol:
                    assignments[wh].append(order["order_id"])
                    remaining_capacity[wh] -= vol
                    assigned = True
                    break
        # If not assigned, order is skipped.

    # Remove warehouses with no assignments from the result
    final_assignments = {wh: orders for wh, orders in assignments.items() if orders}
    return final_assignments