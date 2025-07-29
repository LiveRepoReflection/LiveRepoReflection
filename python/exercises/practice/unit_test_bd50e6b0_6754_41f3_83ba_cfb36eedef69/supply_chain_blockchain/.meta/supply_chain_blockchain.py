def optimize_supply_chain(graph, T, get_demand, record_transaction):
    # Constants
    penalty_rate = 50

    # Identify nodes by type
    suppliers = []
    factories = []
    distributions = []
    for node, info in graph['nodes'].items():
        if info.get('type') == 'supplier':
            suppliers.append((node, info))
        elif info.get('type') == 'factory':
            factories.append((node, info))
        elif info.get('type') == 'distribution':
            distributions.append((node, info))
    
    # For simplicity, assume one supplier, one factory, one distribution if present.
    if suppliers:
        supplier_node, supplier_info = suppliers[0]
    else:
        supplier_node, supplier_info = None, {}
    if factories:
        factory_node, factory_info = factories[0]
    else:
        factory_node, factory_info = None, {}
    if distributions:
        distribution_node, distribution_info = distributions[0]
    else:
        distribution_node, distribution_info = None, {}
    
    supplier_capacity = supplier_info.get('capacity', 0)
    factory_capacity = factory_info.get('capacity', 0)
    distribution_capacity = distribution_info.get('capacity', 0)
    
    # Identify transportation edges and their costs and delays.
    # Assume one edge from supplier to factory and one edge from factory to distribution.
    edge_supplier_factory = None
    edge_factory_distribution = None
    for edge in graph.get('edges', []):
        src = edge.get('source')
        tgt = edge.get('target')
        if src == supplier_node and tgt == factory_node:
            edge_supplier_factory = edge
        elif src == factory_node and tgt == distribution_node:
            edge_factory_distribution = edge

    cost_supplier_factory = edge_supplier_factory.get('cost', 0) if edge_supplier_factory else 0
    delay_supplier_factory = edge_supplier_factory.get('delay', 1) if edge_supplier_factory else 1
    cost_factory_distribution = edge_factory_distribution.get('cost', 0) if edge_factory_distribution else 0
    delay_factory_distribution = edge_factory_distribution.get('delay', 1) if edge_factory_distribution else 1

    # Total simulation time includes delays: extra time for pipeline to flush.
    T_total = T + delay_supplier_factory + delay_factory_distribution

    # Initialize arrays for quantities.
    supplier_orders = [0] * T_total
    factory_input = [0] * T_total
    factory_processed = [0] * T_total
    distribution_input = [0] * T_total
    distribution_shipped = [0] * T_total

    # Simulate supplier ordering decisions.
    # The decision at time t is based on expected demand after the pipeline delays (t + total_delay)
    for t in range(T_total):
        if t + delay_supplier_factory + delay_factory_distribution < T:
            expected_demand = get_demand(t + delay_supplier_factory + delay_factory_distribution)
            order_qty = min(supplier_capacity, expected_demand)
        else:
            order_qty = 0
        supplier_orders[t] = order_qty
        # Record blockchain transaction for supplier order.
        record_transaction({
            'node': supplier_node,
            'time': t,
            'action': 'order',
            'quantity': order_qty
        })

    # Simulate factory processing.
    for t in range(T_total):
        # Factory receives supplier orders with delay_supplier_factory delay.
        if t - delay_supplier_factory >= 0:
            factory_input[t] = supplier_orders[t - delay_supplier_factory]
        else:
            factory_input[t] = 0
        processed = min(factory_input[t], factory_capacity)
        factory_processed[t] = processed
        # Record blockchain transaction for factory processing.
        record_transaction({
            'node': factory_node,
            'time': t,
            'action': 'process',
            'quantity': processed
        })

    # Simulate distribution shipping.
    penalty_cost_total = 0
    for t in range(T_total):
        # Distribution receives processed goods with delay_factory_distribution delay.
        if t - delay_factory_distribution >= 0:
            distribution_input[t] = factory_processed[t - delay_factory_distribution]
        else:
            distribution_input[t] = 0
        # Shipping only occurs during the planned time horizon [0, T)
        if t < T:
            demand = get_demand(t)
            shipped = min(distribution_input[t], demand, distribution_capacity)
            distribution_shipped[t] = shipped
            unmet = demand - shipped
            penalty = unmet * penalty_rate
            penalty_cost_total += penalty
            # Record blockchain transaction for distribution shipping.
            record_transaction({
                'node': distribution_node,
                'time': t,
                'action': 'ship',
                'quantity': shipped,
                'demand': demand,
                'penalty': penalty
            })
        else:
            distribution_shipped[t] = 0

    # Calculate transportation costs.
    transport_cost_supplier_factory = 0
    for t in range(delay_supplier_factory, T_total):
        transport_cost_supplier_factory += supplier_orders[t - delay_supplier_factory] * cost_supplier_factory

    transport_cost_factory_distribution = 0
    for t in range(delay_factory_distribution, T_total):
        transport_cost_factory_distribution += factory_processed[t - delay_factory_distribution] * cost_factory_distribution

    total_transport_cost = transport_cost_supplier_factory + transport_cost_factory_distribution
    total_cost = total_transport_cost + penalty_cost_total

    # Build schedule for each node for time periods 0..T-1.
    schedule = {}

    # Supplier schedule.
    supplier_schedule = []
    for t in range(T):
        supplier_schedule.append({'ordered': supplier_orders[t]})
    if supplier_node:
        schedule[supplier_node] = supplier_schedule

    # Factory schedule.
    factory_schedule = []
    for t in range(T):
        factory_schedule.append({'processed': factory_processed[t]})
    if factory_node:
        schedule[factory_node] = factory_schedule

    # Distribution schedule.
    distribution_schedule = []
    for t in range(T):
        distribution_schedule.append({'shipped': distribution_shipped[t]})
    if distribution_node:
        schedule[distribution_node] = distribution_schedule

    return schedule, total_cost