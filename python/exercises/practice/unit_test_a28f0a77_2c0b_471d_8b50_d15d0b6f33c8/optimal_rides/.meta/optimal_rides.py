import heapq
import math

def dijkstra(graph, start, end):
    if start == end:
        return [start], 0

    dist = {node: math.inf for node in graph}
    prev = {node: None for node in graph}
    dist[start] = 0
    heap = [(0, start)]
    
    while heap:
        current_dist, current = heapq.heappop(heap)
        if current == end:
            break
        if current_dist > dist[current]:
            continue
        for neighbor, weight in graph.get(current, []):
            new_dist = current_dist + weight
            if new_dist < dist.get(neighbor, math.inf):
                dist[neighbor] = new_dist
                prev[neighbor] = current
                heapq.heappush(heap, (new_dist, neighbor))
                
    if dist[end] == math.inf:
        return None, None

    # Reconstruct path
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    
    return path, dist[end]

def plan_rides(graph, requests):
    # Compute shortest path for each request individually.
    results = {}
    direct_paths = {}
    for req in requests:
        req_id = req["id"]
        start = req["start"]
        end = req["end"]
        # For same start=end, return trivial path
        if start == end:
            direct_paths[req_id] = ([start], 0)
            results[req_id] = {
                "shared": False,
                "travel_time": 0,
                "route": [start],
                "riders": []
            }
        else:
            path, cost = dijkstra(graph, start, end)
            if path is None:
                direct_paths[req_id] = (None, None)
                results[req_id] = {
                    "shared": False,
                    "travel_time": None,
                    "route": None,
                    "riders": []
                }
            else:
                direct_paths[req_id] = (path, cost)
                results[req_id] = {
                    "shared": False,
                    "travel_time": cost,
                    "route": path,
                    "riders": []
                }
                
    # Group ride requests that are eligible for sharing.
    # For this simple implementation, only group requests with identical start and end.
    groups = {}
    for req in requests:
        req_id = req["id"]
        start = req["start"]
        end = req["end"]
        key = (start, end)
        # Only group if the ride is reachable
        if direct_paths[req_id][0] is not None:
            groups.setdefault(key, []).append(req_id)
    
    # For each group with more than one ride, assign shared ride attributes.
    for group in groups.values():
        if len(group) > 1:
            # For ride sharing, assume they all share the same direct route.
            # Validate that each request's detour factor allows for the direct route travel time.
            valid_group = []
            for req_id in group:
                # Get the individual shortest travel time from direct path.
                _, cost = direct_paths[req_id]
                req = next(r for r in requests if r["id"] == req_id)
                # The maximum allowed travel time is detour factor * direct travel time.
                max_allowed = req["detour"] * cost if cost is not None else math.inf
                # In a shared ride with same start and end as direct ride,
                # the travel time remains the same.
                if cost <= max_allowed:
                    valid_group.append(req_id)
            if len(valid_group) > 1:
                # Mark these rides as shared.
                for req_id in valid_group:
                    rider_list = [other for other in valid_group if other != req_id]
                    results[req_id]["shared"] = True
                    results[req_id]["riders"] = rider_list
    return results