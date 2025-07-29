import heapq
from collections import defaultdict

def dijkstra(graph, start, end):
    # Standard Dijkstra's algorithm to find the shortest path from start to end
    queue = [(0, start)]
    distances = {start: 0}
    while queue:
        curr_dist, node = heapq.heappop(queue)
        if node == end:
            return curr_dist
        if curr_dist > distances.get(node, float('inf')):
            continue
        for neighbor, weight in graph[node]:
            distance = curr_dist + weight
            if distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = distance
                heapq.heappush(queue, (distance, neighbor))
    return float('inf')

def build_graph(nodes, edges):
    graph = defaultdict(list)
    # Although nodes list contains coordinates, we only use node_id for graph construction.
    for node_id, _, _ in nodes:
        graph[node_id] = []
    for u, v, weight in edges:
        graph[u].append((v, weight))
        graph[v].append((u, weight))
    return graph

def simulate_order(current_location, current_time, order, graph):
    # order: (order_id, source_node, destination_node, start_time, end_time, priority)
    order_id, src, dest, start_time, end_time, priority = order
    # Compute travel time from current location to order's source
    t1 = 0
    if current_location != src:
        t1 = dijkstra(graph, current_location, src)
    arrival_at_source = current_time + t1
    # Wait if arriving earlier than the start_time
    wait_time = 0
    if arrival_at_source < start_time:
        wait_time = start_time - arrival_at_source
    start_service = arrival_at_source + wait_time
    # Compute travel time from source to destination
    t2 = dijkstra(graph, src, dest)
    finish_time = start_service + t2
    lateness = max(0, finish_time - end_time)
    total_travel = t1 + wait_time + t2
    return finish_time, lateness, total_travel

def optimal_route_plan(nodes, edges, orders):
    """
    Given the city graph (nodes, edges) and delivery orders, returns an ordered list of delivery order IDs
    representing the optimized delivery route that minimizes overall lateness while prioritizing higher priority orders.
    """
    # Build graph representation from nodes and edges.
    graph = build_graph(nodes, edges)
    if not orders:
        return []
    
    remaining_orders = orders.copy()
    route = []
    # Select the first order as the one with the highest priority.
    first_order = max(remaining_orders, key=lambda o: o[5])
    remaining_orders.remove(first_order)
    order_id, src, dest, start_time, end_time, priority = first_order
    # Assume starting at the source of the first order; travel time from src to src is 0.
    initial_start = max(0, start_time)
    t_delivery = dijkstra(graph, src, dest)
    current_time = initial_start + t_delivery
    current_location = dest
    route.append(order_id)
    
    # Greedily select the next order based on a cost tuple: (lateness, total_travel, -priority)
    while remaining_orders:
        best_order = None
        best_cost = None
        best_finish = None
        for order in remaining_orders:
            finish_time, lateness, total_travel = simulate_order(current_location, current_time, order, graph)
            # The cost tuple prioritizes lower lateness, then lower total travel, then higher priority.
            cost = (lateness, total_travel, -order[5])
            if best_cost is None or cost < best_cost:
                best_cost = cost
                best_order = order
                best_finish = finish_time
        # Update current state with chosen order
        route.append(best_order[0])
        remaining_orders.remove(best_order)
        finish_time, _, _ = simulate_order(current_location, current_time, best_order, graph)
        current_time = finish_time
        current_location = best_order[2]  # destination of the selected order
    return route