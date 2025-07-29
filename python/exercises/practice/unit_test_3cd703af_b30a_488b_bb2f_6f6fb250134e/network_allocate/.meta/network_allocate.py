import heapq
import math
from collections import defaultdict

def find_optimal_path(capacities, costs, allocations, source, destination, bandwidth):
    """
    Finds the optimal path for routing bandwidth in a network.
    
    Args:
        capacities: Dict of (source, destination) tuples to capacity values
        costs: Dict of (source, destination) tuples to cost values
        allocations: Dict of (source, destination) tuples to current bandwidth allocations
        source: Source router index
        destination: Destination router index
        bandwidth: Required bandwidth for the new service
        
    Returns:
        Tuple of (path, total_cost) if a feasible path exists, None otherwise
        path is a list of router indices including source and destination
        total_cost is the total cost of routing the bandwidth
    """
    # Handle edge case: source equals destination
    if source == destination:
        return ([source], 0.0)
    
    # Build adjacency list representation of the network
    network = defaultdict(list)
    for (u, v), cap in capacities.items():
        # Get the current allocation for this link
        current_allocation = allocations.get((u, v), 0.0)
        # Calculate remaining capacity
        remaining_capacity = cap - current_allocation
        
        # Only add edge if there's enough remaining capacity
        if remaining_capacity >= bandwidth:
            # Add edge u -> v with cost
            cost = costs.get((u, v), float('inf'))
            network[u].append((v, cost, remaining_capacity))
            # Add the reverse edge (graph is undirected)
            network[v].append((u, cost, remaining_capacity))
    
    # Check if source and destination are in the network
    if source not in network or destination not in network:
        return None
    
    # Use Dijkstra's algorithm to find shortest path
    # Priority queue entry: (total_cost_so_far, current_node, path_so_far)
    priority_queue = [(0, source, [source])]
    visited = set()
    
    while priority_queue:
        cost_so_far, current, path = heapq.heappop(priority_queue)
        
        # If already visited this node through a cheaper path, skip
        if current in visited:
            continue
        
        # Mark as visited
        visited.add(current)
        
        # If reached destination, return the path and total cost
        if current == destination:
            return (path, cost_so_far * bandwidth)
        
        # Explore neighbors
        for neighbor, edge_cost, remaining_capacity in network[current]:
            if neighbor not in visited and remaining_capacity >= bandwidth:
                # Calculate new cost and path
                new_cost = cost_so_far + edge_cost
                new_path = path + [neighbor]
                
                # Add to priority queue
                heapq.heappush(priority_queue, (new_cost, neighbor, new_path))
    
    # If we get here, there is no feasible path
    return None