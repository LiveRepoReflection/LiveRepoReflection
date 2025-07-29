import heapq
from collections import defaultdict

def find_optimal_route(N, links, critical_nodes, start, end, penalty_factor):
    """
    Find the optimal route from start to end node in a network with critical nodes.
    
    Args:
        N (int): Number of nodes in the network
        links (list): List of tuples (u, v, bandwidth) representing bidirectional links
        critical_nodes (set): Set of node IDs that are considered critical
        start (int): Starting node ID
        end (int): Destination node ID
        penalty_factor (float): Penalty multiplier for traffic through critical nodes
    
    Returns:
        list: Optimal route from start to end as a list of node IDs, or empty list if no route exists
    """
    # Build the adjacency list representation of the graph
    graph = defaultdict(list)
    for u, v, bandwidth in links:
        graph[u].append((v, bandwidth))
        graph[v].append((u, bandwidth))  # Bidirectional links
    
    # Initialize distances with infinity for all nodes
    distances = {node: float('infinity') for node in range(N)}
    distances[start] = 0
    
    # Initialize previous node dictionary for path reconstruction
    previous = {node: None for node in range(N)}
    
    # Priority queue for Dijkstra's algorithm
    # (total_cost, node_id, path_length)
    priority_queue = [(0, start, 0)]
    
    while priority_queue:
        current_cost, current_node, path_length = heapq.heappop(priority_queue)
        
        # If we reached the destination, we're done
        if current_node == end:
            break
        
        # If we've found a better path to this node already, skip
        if current_cost > distances[current_node]:
            continue
        
        # Explore neighbors
        for neighbor, bandwidth in graph[current_node]:
            # Calculate new path length
            new_path_length = path_length + 1
            
            # Calculate penalty if neighbor is a critical node
            penalty = penalty_factor if neighbor in critical_nodes else 0
            
            # Calculate total cost (path length + penalties)
            # We give preference to higher bandwidth in case of ties
            # by subtracting a small factor based on bandwidth
            bandwidth_factor = 0.0001 * bandwidth
            new_cost = new_path_length + penalty - bandwidth_factor
            
            if new_cost < distances[neighbor]:
                distances[neighbor] = new_cost
                previous[neighbor] = current_node
                heapq.heappush(priority_queue, (new_cost, neighbor, new_path_length))
    
    # Reconstruct path from start to end
    if distances[end] == float('infinity'):
        return []  # No path exists
    
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous[current]
    
    # Reverse path to get from start to end
    return path[::-1]