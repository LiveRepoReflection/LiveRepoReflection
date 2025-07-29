def allocate(resources, consumers, time_steps):
    total_cost = 0.0
    allocations = []  # List of allocations per time step, each a list for each resource.

    # Initialize battery state for each battery resource using its index.
    battery_states = {}
    for i, resource in enumerate(resources):
        if resource["type"] == "battery":
            battery_states[i] = resource.get("initial_charge", 0)

    # Process each time step.
    for t in range(time_steps):
        # Compute total demand from all consumers for the current time step.
        demand_t = sum(consumer[t] for consumer in consumers)
        remaining = demand_t
        alloc_t = [0.0 for _ in resources]

        # First, use renewable resources (solar and wind) which have zero cost.
        for i, resource in enumerate(resources):
            if resource["type"] in ("solar", "wind"):
                production = resource["capacity"] * resource["availability"][t]
                supply = min(production, remaining)
                alloc_t[i] = supply
                remaining -= supply

        # Second, use battery resources if demand is still unmet.
        # Battery discharge incurs a degradation cost.
        for i, resource in enumerate(resources):
            if resource["type"] == "battery":
                current_charge = battery_states.get(i, 0)
                available = min(current_charge, resource["discharge_rate"])
                supply = min(available, remaining)
                alloc_t[i] = supply
                battery_states[i] = current_charge - supply
                remaining -= supply
                total_cost += supply * resource["degradation_cost"]

        # Third, use grid resources to cover any remaining demand.
        for i, resource in enumerate(resources):
            if resource["type"] == "grid":
                # Grid capacity is assumed to be sufficient (even infinite).
                supply = min(remaining, resource["capacity"])
                alloc_t[i] = supply
                total_cost += supply * resource["cost"][t]
                remaining -= supply

        # Check if the demand has been fully met.
        if abs(remaining) > 1e-6:
            raise ValueError("Not enough supply to meet demand at time step {}".format(t))
        allocations.append(alloc_t)

    return {"allocations": allocations, "total_cost": total_cost}


if __name__ == "__main__":
    # Sample run (this block can be used for quick manual testing)
    resources = [
        {
            "type": "solar",
            "capacity": 10,
            "availability": [0.5, 0.8]
        },
        {
            "type": "battery",
            "capacity": 5,
            "initial_charge": 2,
            "charge_rate": 2,
            "discharge_rate": 2,
            "degradation_cost": 0.1
        },
        {
            "type": "grid",
            "capacity": float("inf"),
            "cost": [0.2, 0.3]
        }
    ]
    consumers = [
        [7, 7]
    ]
    time_steps = 2
    result = allocate(resources, consumers, time_steps)
    print(result)