import heapq

def find_routes(locations, edges, transfer_costs, od_pairs):
    # Build a dictionary for location mode support
    location_support = {}
    for loc in locations:
        # Each location dict contains keys: name, truck, train, ship
        supported = set()
        if loc.get("truck", False):
            supported.add("truck")
        if loc.get("train", False):
            supported.add("train")
        if loc.get("ship", False):
            supported.add("ship")
        location_support[loc["name"]] = supported

    # Build graph: mapping from source to list of edges.
    graph = {}
    for loc in location_support:
        graph[loc] = []
    # Only include edge if both source and destination support the mode.
    for edge in edges:
        src = edge["source"]
        dst = edge["destination"]
        mode = edge["mode"]
        if src in location_support and dst in location_support:
            if mode in location_support[src] and mode in location_support[dst]:
                graph[src].append({
                    "source": src,
                    "destination": dst,
                    "mode": mode,
                    "cost": edge["cost"],
                    "time": edge["time"],
                    "capacity": edge["capacity"]
                })

    results = []
    # Process each origin-destination pair
    for od in od_pairs:
        origin = od["origin"]
        destination = od["destination"]
        quantity = od["quantity"]
        time_window = od["time_window"]  # [start, end]
        best_route = None

        # Dijkstra with state: (total_cost, total_time, current_node, last_mode, path_nodes, path_edges)
        # Start with last_mode = None (no mode used yet)
        heap = [(0, 0, origin, None, [origin], [])]
        # visited dictionary for (node, last_mode) -> (total_cost, total_time)
        visited = {}
        while heap:
            total_cost, total_time, node, last_mode, path_nodes, path_edges = heapq.heappop(heap)
            state = (node, last_mode)
            if state in visited:
                prev_cost, prev_time = visited[state]
                if total_cost > prev_cost or (total_cost == prev_cost and total_time >= prev_time):
                    continue
            visited[state] = (total_cost, total_time)

            if node == destination:
                # Found a route, since heapq pops smallest cost/time route first.
                best_route = {
                    "nodes": path_nodes,
                    "edges": path_edges,
                    "total_cost": total_cost,
                    "total_time": total_time,
                    "time_window_met": total_time <= time_window[1]
                }
                break

            # Expand neighbors
            for edge in graph.get(node, []):
                next_node = edge["destination"]
                # Check mode compatibility already handled in graph construction.
                # Calculate transfer cost (if any)
                if last_mode is None or last_mode == edge["mode"]:
                    trans_cost = 0
                else:
                    trans_cost = transfer_costs.get(last_mode, {}).get(edge["mode"], 0)
                # Capacity penalty: if quantity exceeds capacity, add penalty per unit over capacity
                penalty = max(0, quantity - edge["capacity"])
                # New cost and time include base cost/time plus penalties and any transfer cost
                new_cost = total_cost + trans_cost + edge["cost"] + penalty
                new_time = total_time + edge["time"] + penalty
                new_state = (next_node, edge["mode"])
                new_path_nodes = path_nodes + [next_node]
                new_path_edges = path_edges + [edge]
                # Push to the heap
                heapq.heappush(heap, (new_cost, new_time, next_node, edge["mode"], new_path_nodes, new_path_edges))

        if best_route is None:
            # No route found, return route with all values as None and time_window_met as False.
            results.append({
                "nodes": None,
                "edges": None,
                "total_cost": None,
                "total_time": None,
                "time_window_met": False
            })
        else:
            results.append(best_route)
    return results