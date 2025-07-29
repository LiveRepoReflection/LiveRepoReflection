import heapq
import math

def compute_shortest_time(graph, source, target):
    """
    Compute the shortest travel time from source to target using Dijkstra's algorithm.
    If target is unreachable, returns math.inf.
    """
    if source == target:
        return 0
    dist = {node: math.inf for node in graph}
    dist[source] = 0
    heap = [(0, source)]
    while heap:
        cur_time, cur_node = heapq.heappop(heap)
        if cur_node == target:
            return cur_time
        if cur_time > dist[cur_node]:
            continue
        for neighbor, weight in graph[cur_node]:
            new_time = cur_time + weight
            if new_time < dist[neighbor]:
                dist[neighbor] = new_time
                heapq.heappush(heap, (new_time, neighbor))
    return math.inf

def dispatch_fleet(edges, requests, num_avs, depot, T):
    """
    Compute the maximum total reward the AV fleet can earn within simulation time T.
    
    Parameters:
    edges: List of tuples (u, v, w)
    requests: List of tuples (pickup, dropoff, request_time, reward, max_wait)
    num_avs: Number of autonomous vehicles
    depot: Starting intersection for all vehicles
    T: Total simulation time in seconds
    
    Returns:
    Integer: Maximum total reward earned.
    """
    # Build graph as adjacency list. Ensure all nodes appear.
    graph = {}
    for u, v, w in edges:
        if u not in graph:
            graph[u] = []
        if v not in graph:
            graph[v] = []
        graph[u].append((v, w))
    # It's possible some nodes exist only as destinations.
    # Ensure all nodes are in the graph.
    for u, v, w in edges:
        if u not in graph:
            graph[u] = []
        if v not in graph:
            graph[v] = []
    
    # Sort requests by request time
    sorted_requests = sorted(requests, key=lambda r: r[2])
    
    # Initialize vehicles as list of (available_time, location)
    vehicles = [(0, depot) for _ in range(num_avs)]
    
    total_reward = 0
    
    # Process each ride request in order of request time
    for ride in sorted_requests:
        pickup, dropoff, req_time, reward, max_wait = ride
        best_vehicle_idx = None
        best_finish_time = math.inf
        
        # Evaluate each vehicle for possibility to serve this ride
        for idx, (avail_time, location) in enumerate(vehicles):
            # Compute travel time from current location to pickup
            time_to_pickup = compute_shortest_time(graph, location, pickup)
            if time_to_pickup == math.inf:
                continue  # Cannot reach pickup
            
            arrival_time = avail_time + time_to_pickup
            # Vehicle can only start ride at max(arrival_time, request time)
            start_time = req_time if arrival_time < req_time else arrival_time
            # Check if pickup is reached within allowed waiting time
            if start_time > req_time + max_wait:
                continue  # This vehicle cannot get there in time
            
            # Compute travel time from pickup to dropoff
            ride_time = compute_shortest_time(graph, pickup, dropoff)
            if ride_time == math.inf:
                continue  # Ride is not achievable
            
            finish_time = start_time + ride_time
            
            # Ride must complete within simulation time T.
            if finish_time > T:
                continue
            
            # Choose the best vehicle that finishes earliest
            if finish_time < best_finish_time:
                best_finish_time = finish_time
                best_vehicle_idx = idx
        
        # If a vehicle is found for the ride, assign the ride.
        if best_vehicle_idx is not None:
            total_reward += reward
            vehicles[best_vehicle_idx] = (best_finish_time, dropoff)
    
    return total_reward