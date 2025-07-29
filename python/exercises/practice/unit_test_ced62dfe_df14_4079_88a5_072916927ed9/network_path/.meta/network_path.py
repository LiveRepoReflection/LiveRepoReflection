import heapq
import math

def optimal_route(num_routers, edges, source, destination, time_windows, congestion_levels, unique_times):
    """
    For each time window (snapshot), compute the maximum achievable minimum available capacity
    along a path from source to destination.
    Return a list of integers representing this capacity for each time window.
    If no valid path exists in a time window, return -1 for that window.
    """
    results = []
    # Assume that each time window corresponds to the congestion snapshot at the same index in congestion_levels.
    for snapshot in congestion_levels:
        # Build the graph for the current congestion snapshot.
        # Graph is dict: node -> list of (neighbor, available_capacity)
        graph = {i: [] for i in range(num_routers)}
        for idx, (u, v, capacity) in enumerate(edges):
            # Calculate available capacity for the edge at the current time.
            available = capacity * (1 - snapshot[idx])
            # Only add the edge if there is some capacity available.
            # However, an edge with 0 available might be validly considered impassable.
            graph[u].append((v, available))
        
        # Use a modified Dijkstra algorithm to maximize the bottleneck (minimum capacity along the path).
        max_bandwidth = [0] * num_routers
        max_bandwidth[source] = math.inf
        # Priority queue stores pairs (-bandwidth, node) to simulate a max-heap.
        heap = [(-max_bandwidth[source], source)]
        
        while heap:
            current_bandwidth, node = heapq.heappop(heap)
            current_bandwidth = -current_bandwidth
            # Early exit if we reached the destination.
            if node == destination:
                break
            # If we already have a better bandwidth to this node, continue.
            if current_bandwidth < max_bandwidth[node]:
                continue
            # Explore neighbors.
            for neighbor, available in graph[node]:
                # Calculate the new bandwidth as the minimum of current path's bandwidth and the available capacity of the edge.
                new_bandwidth = min(current_bandwidth, available)
                if new_bandwidth > max_bandwidth[neighbor]:
                    max_bandwidth[neighbor] = new_bandwidth
                    heapq.heappush(heap, (-new_bandwidth, neighbor))
        
        # If destination is unreachable, max_bandwidth[destination] remains 0 or -infinity
        if max_bandwidth[destination] == 0 or max_bandwidth[destination] == -math.inf:
            results.append(-1)
        else:
            # If the result is infinite (source equals destination which shouldn't happen) or a real number, 
            # we return it as an integer since capacities are given as integers.
            # In our problem, bandwidths are computed from integer capacities.
            results.append(int(max_bandwidth[destination]))
            
    return results

if __name__ == "__main__":
    # Example run (this block can be removed when running unit tests)
    num_routers = 3
    edges = [
        (0, 1, 100),
        (1, 2, 200)
    ]
    source = 0
    destination = 2
    time_windows = [(5, 6)]
    unique_times = [5]
    congestion_levels = [
        [0.0, 0.5]
    ]
    
    print(optimal_route(num_routers, edges, source, destination, time_windows, congestion_levels, unique_times))