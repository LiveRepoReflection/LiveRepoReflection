import heapq
from collections import defaultdict

def find_optimal_path(N, node_capacities, connections, source, destination, data_size, latency_budget):
    """
    Find the optimal path from source to destination within a latency budget.
    
    Args:
        N (int): The number of nodes in the network.
        node_capacities (list): A list of length N representing the processing capacity of each node.
        connections (list): A list of tuples (node1, node2, latency) representing bidirectional connections.
        source (int): The index of the source node.
        destination (int): The index of the destination node.
        data_size (int): The size of the data to be routed.
        latency_budget (int): The maximum allowed latency for the path.
        
    Returns:
        list: A list of integers representing the optimal path, or an empty list if no valid path exists.
    """
    # Handle the case when source and destination are the same
    if source == destination:
        return [source]
    
    # Build the adjacency list representation of the graph
    graph = defaultdict(list)
    for node1, node2, latency in connections:
        graph[node1].append((node2, latency))
        graph[node2].append((node1, latency))
    
    # Initialize data structures for Dijkstra's algorithm with multiple criteria
    # We'll use a min-heap priority queue to keep track of (total_cost, latency, hops, path)
    pq = [(0, 0, 1, [source])]
    # Keep track of visited states to avoid cycles and repeated work
    # We track a state as (node, latency) to allow revisiting nodes with better latencies
    visited = set()
    
    while pq:
        total_cost, current_latency, hops, path = heapq.heappop(pq)
        current_node = path[-1]
        
        # If we've reached the destination, return the path
        if current_node == destination:
            return path
        
        # Skip if we've already processed this state with a better or equal cost
        state = (current_node, current_latency)
        if state in visited:
            continue
        visited.add(state)
        
        # Explore neighbors
        for neighbor, latency in graph[current_node]:
            # Skip if we've already visited this node in the current path (avoid cycles)
            if neighbor in path:
                continue
            
            new_latency = current_latency + latency
            
            # Skip if the latency exceeds the budget
            if new_latency > latency_budget:
                continue
            
            # Calculate the processing cost for this neighbor
            processing_cost = data_size / node_capacities[neighbor]
            
            # Calculate the total cost for reaching the neighbor
            new_total_cost = total_cost + latency + processing_cost
            
            # Create the new path
            new_path = path + [neighbor]
            
            # Add to priority queue with the new cost, latency, and increased hop count
            heapq.heappush(pq, (new_total_cost, new_latency, hops + 1, new_path))
    
    # If we've exhausted all possibilities and haven't found a path, return empty list
    return []