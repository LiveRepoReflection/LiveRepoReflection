def allocate_resources(timestamp, grid_price, solar_generation, wind_generation, demands, battery_state, battery_capacity, max_charge_rate, max_grid_power):
    # Validate inputs
    if grid_price < 0:
        raise ValueError("grid_price cannot be negative")
    if solar_generation < 0 or wind_generation < 0:
        raise ValueError("renewable generation cannot be negative")
    if battery_state < 0 or battery_state > battery_capacity:
        raise ValueError("battery_state out of bounds")
    if max_charge_rate < 0 or max_grid_power < 0:
        raise ValueError("charge rate and grid power limits must be non-negative")
    for consumer, demand in demands.items():
        if demand < 0:
            raise ValueError("consumer demand cannot be negative")
    
    total_demand = sum(demands.values())
    total_renewable = solar_generation + wind_generation
    consumer_power = {}

    if total_demand == 0:
        # No consumer demand: allocate surplus renewable generation to charging the battery.
        surplus = total_renewable
        charge_possible = battery_capacity - battery_state
        battery_charge = min(surplus, max_charge_rate, charge_possible)
        grid_power = 0
        battery_charge_rate = battery_charge
        for consumer in demands:
            consumer_power[consumer] = 0
    elif total_renewable >= total_demand:
        # Sufficient renewable energy to satisfy all demand.
        for consumer, d in demands.items():
            consumer_power[consumer] = d
        surplus = total_renewable - total_demand
        charge_possible = battery_capacity - battery_state
        battery_charge = min(surplus, max_charge_rate, charge_possible)
        grid_power = 0
        battery_charge_rate = battery_charge
    else:
        # Renewable energy is insufficient.
        deficit = total_demand - total_renewable
        # Battery discharge: battery discharging is limited by max_charge_rate and available battery energy.
        battery_possible = min(max_charge_rate, battery_state)
        battery_used = min(deficit, battery_possible)
        deficit_after_battery = deficit - battery_used
        grid_used = min(deficit_after_battery, max_grid_power)
        # Distribute renewable, battery, and grid supplies proportionally to each consumer's demand.
        for consumer, d in demands.items():
            # Renewable allocation is proportional to each consumer's share of total demand.
            r_alloc = d * (total_renewable / total_demand)
            remaining = d - r_alloc
            # Allocate battery discharge proportionally.
            if deficit > 0:
                b_alloc = remaining * (battery_used / deficit)
            else:
                b_alloc = 0
            g_alloc = remaining - b_alloc
            consumer_power[consumer] = r_alloc + b_alloc + g_alloc
        battery_charge_rate = -battery_used
        grid_power = grid_used

    return {
        "grid_power": grid_power,
        "battery_charge_rate": battery_charge_rate,
        "consumer_power": consumer_power
    }