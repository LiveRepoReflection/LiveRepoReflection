import heapq

class Edge:
    def __init__(self, to, cap, cost, rev):
        self.to = to        # target node
        self.cap = cap      # remaining capacity
        self.cost = cost    # cost per unit
        self.rev = rev      # index of reverse edge
        self.flow = 0       # flow sent on this edge

def add_edge(graph, fr, to, cap, cost):
    forward = Edge(to, cap, cost, len(graph[to]))
    backward = Edge(fr, 0, -cost, len(graph[fr]))
    graph[fr].append(forward)
    graph[to].append(backward)

def min_cost_flow(graph, source, sink, flow_required):
    n = len(graph)
    INF = float('inf')
    h = [0] * n  # potential
    prev_v = [0] * n  # previous vertex
    prev_e = [0] * n  # previous edge index
    flow = 0
    cost = 0
    while flow < flow_required:
        dist = [INF] * n
        dist[source] = 0
        queue = []
        heapq.heappush(queue, (0, source))
        while queue:
            d, v = heapq.heappop(queue)
            if dist[v] < d:
                continue
            for i, e in enumerate(graph[v]):
                if e.cap > 0 and dist[e.to] > d + e.cost + h[v] - h[e.to]:
                    dist[e.to] = d + e.cost + h[v] - h[e.to]
                    prev_v[e.to] = v
                    prev_e[e.to] = i
                    heapq.heappush(queue, (dist[e.to], e.to))
        if dist[sink] == INF:
            # cannot flow any more
            raise Exception("Not enough supply to fulfill orders for this product")
        for v in range(n):
            h[v] += dist[v] if dist[v] < INF else 0
        d = flow_required - flow
        v = sink
        while v != source:
            d = min(d, graph[prev_v[v]][prev_e[v]].cap)
            v = prev_v[v]
        flow += d
        cost += d * h[sink]
        v = sink
        while v != source:
            e = graph[prev_v[v]][prev_e[v]]
            e.cap -= d
            e.flow += d
            graph[v][e.rev].cap += d
            graph[v][e.rev].flow -= d
            v = prev_v[v]
    return cost

def optimize_order_placement(warehouses, orders):
    # Prepare the result structure.
    result = {}
    for order in orders:
        result[order["id"]] = {}

    # Determine all products requested.
    products_set = set()
    for order in orders:
        for product in order["products"]:
            products_set.add(product)
    products = list(products_set)

    # For each product, solve a transportation problem.
    # Create mapping for orders requiring each product.
    product_orders = {}
    for product in products:
        product_orders[product] = []
        for order in orders:
            if product in order["products"]:
                product_orders[product].append(order)

    # Process each product independently.
    for product in products:
        # List supply nodes (warehouses that have the product).
        supply_nodes = []
        for wh in warehouses:
            if product in wh["capacity"]:
                # Only consider warehouses that offer the product.
                # If shipping_cost is missing for product, skip.
                if product in wh["shipping_cost"]:
                    supply_nodes.append(wh)
        if not supply_nodes and product_orders[product]:
            raise Exception(f"Product {product} is not available in any warehouse.")
        
        # Total supply:
        total_supply = sum(wh["capacity"][product] for wh in supply_nodes)
        # Total demand:
        total_demand = sum(order["products"][product] for order in product_orders[product])
        if total_supply < total_demand:
            raise Exception(f"Warehouse capacities for product {product} are insufficient to meet demand.")
        
        # Build the graph for min cost flow.
        # numbering: source = 0
        # Warehouses: 1 to W, where W = len(supply_nodes)
        # Orders: W+1 to W + O, where O = len(product_orders[product])
        # sink: W + O + 1
        W = len(supply_nodes)
        O = len(product_orders[product])
        source = 0
        sink = W + O + 1
        graph = [[] for _ in range(sink + 1)]
        # Add edges from source to each warehouse node.
        for i, wh in enumerate(supply_nodes):
            cap = wh["capacity"][product]
            add_edge(graph, source, i + 1, cap, 0)
        # Add edges from each warehouse to each order.
        # Cost is the shipping cost from warehouse for this product.
        # Capacity can be set to infinity (or a value >= total_demand) because ordering is not limited beyond supply.
        INF = float('inf')
        for i, wh in enumerate(supply_nodes):
            cost_per_unit = wh["shipping_cost"][product]
            for j, order in enumerate(product_orders[product]):
                add_edge(graph, i + 1, W + j + 1, INF, cost_per_unit)
        # Add edges from each order node to sink.
        for j, order in enumerate(product_orders[product]):
            demand = order["products"][product]
            add_edge(graph, W + j + 1, sink, demand, 0)

        # Run min cost flow.
        min_cost_flow(graph, source, sink, total_demand)

        # After flow computation, extract allocation for this product.
        # For each warehouse to order edge, if flow > 0, assign that quantity.
        for i in range(W):
            for e in graph[i + 1]:
                # Check if edge leads to an order node.
                if W + 1 <= e.to <= W + O and e.flow > 0:
                    j = e.to - (W + 1)
                    order = product_orders[product][j]
                    order_id = order["id"]
                    if product not in result[order_id]:
                        result[order_id][product] = {}
                    # Identify warehouse id.
                    warehouse_id = supply_nodes[i]["id"]
                    result[order_id][product][warehouse_id] = result[order_id][product].get(warehouse_id, 0) + e.flow
    return result