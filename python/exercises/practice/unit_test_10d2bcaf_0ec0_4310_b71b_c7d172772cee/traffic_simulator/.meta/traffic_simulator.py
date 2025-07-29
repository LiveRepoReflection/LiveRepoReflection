import heapq
import math
from collections import defaultdict

def simulate_traffic_flow(graph, vehicles, congestion_factor, T):
    # Cache for routes computed using Dijkstra for (source, destination)
    route_cache = {}
    # State: vehicle_id -> (departure_time, route)
    vehicle_state = {}
    
    # Precompute the shortest path route for each vehicle using Dijkstra
    for vid, (src, dest, dep_time) in enumerate(vehicles):
        # If source equals destination, route is empty and travel time is 0.
        if src == dest:
            vehicle_state[vid] = (dep_time, [])
            continue
        key = (src, dest)
        if key not in route_cache:
            route = dijkstra_route(graph, src, dest)
            route_cache[key] = route
        vehicle_state[vid] = (dep_time, route_cache[key])
    
    # PriorityQueue event: (event_time, vehicle_id, current_node, route_index)
    # route_index is the index in the route list for the next edge to traverse.
    events = []
    for vid, (src, dest, dep_time) in enumerate(vehicles):
        dep, route = vehicle_state[vid]
        # If route is None, there is no available path.
        if route is None:
            continue
        # If route is empty (src == dest), we record travel time = 0 later
        if len(route) == 0:
            heapq.heappush(events, (dep, vid, src, 0))
        else:
            heapq.heappush(events, (dep, vid, src, 0))
    
    # Record completed travel times, keyed by vehicle id
    completed_travel_times = {}
    
    # Process simulation events
    while events:
        # Pop one event from the heap.
        event_time, vid, current_node, route_index = heapq.heappop(events)
        # If event time is beyond simulation period, skip processing.
        if event_time > T:
            continue
        
        # Determine the next edge for the vehicle if route remains.
        departure_time, route = vehicle_state[vid]
        # If route_index equals length of route, it means vehicle has arrived at destination.
        if route_index == len(route):
            # Already at destination; record travel time if not recorded.
            if vid not in completed_travel_times:
                completed_travel_times[vid] = event_time - departure_time
            continue
        
        # The next edge: from current_node to next_node, with given capacity and length.
        next_edge = route[route_index]  # next_edge is a tuple: (next_node, capacity, length)
        next_node, capacity, length = next_edge
        
        # Now, group all events that start the same edge at the same time.
        edge_group = [(event_time, vid, current_node, route_index)]
        # Look ahead in heap while top event has same event_time, current_node, and same next_node.
        temp = []
        while events:
            t, v, curr, idx = heapq.heappop(events)
            if math.isclose(t, event_time) and curr == current_node:
                # Check if this vehicle is taking the same edge
                dep_t, r = vehicle_state[v]
                if idx < len(r) and r[idx][0] == next_node:
                    edge_group.append((t, v, curr, idx))
                    continue
            temp.append((t, v, curr, idx))
        # Push back all other events that do not belong to this group.
        for item in temp:
            heapq.heappush(events, item)
            
        # Determine if congestion occurs for this edge group.
        group_size = len(edge_group)
        if group_size > capacity:
            travel_time = length * congestion_factor
        else:
            travel_time = length
        
        # For each vehicle in the group, schedule its arrival event.
        for t, v, curr, idx in edge_group:
            arrival_time = t + travel_time
            dep_t, r = vehicle_state[v]
            # If arrival time exceeds simulation period, do not schedule further.
            if arrival_time > T:
                continue
            # If next_node is the destination for this vehicle (i.e., this edge was the last in its route)
            if idx == len(r) - 1:
                # Vehicle will arrive at destination.
                completed_travel_times[v] = arrival_time - dep_t
            else:
                # Schedule next event: vehicle v is now at next_node and will depart for the next edge.
                heapq.heappush(events, (arrival_time, v, next_node, idx + 1))
    
    # Compute the average travel time over vehicles that reached destination within T.
    if not completed_travel_times:
        return 0
    total_time = sum(completed_travel_times.values())
    avg_time = total_time / len(completed_travel_times)
    return avg_time

def dijkstra_route(graph, start, end):
    # Standard Dijkstra algorithm over the graph with travel time = length for each edge.
    # The graph structure: graph[u] is list of tuples (v, capacity, length).
    # Return the route as a list of edges: each edge is (v, capacity, length).
    heap = [(0, start)]
    dist = {start: 0}
    prev = {start: None}  # To reconstruct path: key: node, value: (prev_node, edge_info)
    
    while heap:
        cur_dist, u = heapq.heappop(heap)
        if u == end:
            break
        if cur_dist > dist.get(u, float('inf')):
            continue
        for edge in graph.get(u, []):
            v, capacity, length = edge
            new_dist = cur_dist + length
            if new_dist < dist.get(v, float('inf')):
                dist[v] = new_dist
                prev[v] = (u, edge)
                heapq.heappush(heap, (new_dist, v))
    
    if end not in dist:
        return None  # No route available
    
    # Reconstruct route from start to end.
    route = []
    node = end
    while node != start:
        pred, edge = prev[node]
        route.append(edge)
        node = pred
    route.reverse()
    return route