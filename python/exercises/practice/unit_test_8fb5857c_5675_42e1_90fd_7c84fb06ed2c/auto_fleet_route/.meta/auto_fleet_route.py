import heapq
import math

def route_vehicles(city_graph, vehicles):
    # Initialize usage for each edge in the city graph.
    # usage is a dict with key (u, edge_index) and value count.
    usage = {}
    for u in city_graph:
        for idx in range(len(city_graph[u])):
            usage[(u, idx)] = 0

    # These lists hold the computed route (list of intersections)
    # and the chosen edges (list of tuples (u, edge_index)) for each vehicle.
    routes = []
    chosen_edges_list = []

    # Process each vehicle sequentially.
    for start, dest in vehicles:
        if start == dest:
            routes.append([start])
            chosen_edges_list.append([])
            continue

        # Dijkstra's algorithm to find shortest path given current congestion.
        dist = {node: math.inf for node in city_graph}
        prev = {}  # will store (prev_node, edge index used)
        dist[start] = 0
        heap = [(0, start)]
        
        while heap:
            current_cost, u = heapq.heappop(heap)
            if current_cost > dist[u]:
                continue
            # Early stopping if we reached destination.
            if u == dest:
                break
            for idx, edge in enumerate(city_graph.get(u, [])):
                v, base, congest = edge
                # If we add a vehicle on this edge, the cost is computed with usage+1.
                current_usage = usage[(u, idx)]
                edge_cost = base * congest(current_usage + 1)
                new_cost = dist[u] + edge_cost
                # If we don't have node v in dist, default is math.inf.
                if new_cost < dist.get(v, math.inf):
                    dist[v] = new_cost
                    prev[v] = (u, idx)
                    heapq.heappush(heap, (new_cost, v))
        
        # Check if destination was reached.
        if dist.get(dest, math.inf) == math.inf:
            routes.append([])
            chosen_edges_list.append([])
        else:
            # Reconstruct the path and record edge usage.
            path = []
            chosen_edges = []
            cur = dest
            while cur != start:
                if cur not in prev:
                    break
                u, edge_idx = prev[cur]
                chosen_edges.append((u, edge_idx))
                cur = u
            chosen_edges.reverse()
            path.append(start)
            for (u, idx) in chosen_edges:
                # Increase the usage for this edge.
                usage[(u, idx)] += 1
                next_node = city_graph[u][idx][0]
                path.append(next_node)
            routes.append(path)
            chosen_edges_list.append(chosen_edges)

    # After assigning routes for all vehicles, compute the final travel time for each vehicle.
    final_travel_times = []
    for chosen_edges in chosen_edges_list:
        if not chosen_edges:
            final_travel_times.append(math.inf)
        else:
            total_time = 0
            for (u, idx) in chosen_edges:
                v, base, congest = city_graph[u][idx]
                count = usage[(u, idx)]
                total_time += base * congest(count)
            final_travel_times.append(total_time)

    # The maximum travel time among all vehicles.
    max_travel_time = max(final_travel_times) if final_travel_times else 0

    return routes, max_travel_time