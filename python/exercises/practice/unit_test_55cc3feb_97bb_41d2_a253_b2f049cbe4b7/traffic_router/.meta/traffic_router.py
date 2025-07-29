import heapq
from collections import defaultdict, deque
import copy

def find_k_shortest_paths(graph, requests, updates):
    """
    Find the k shortest paths for each request, considering road updates.
    
    Args:
        graph: Dictionary representing the road network as an adjacency list.
        requests: List of (source, destination, k) tuples.
        updates: List of (source, dest, new_capacity, new_travel_time) tuples.
    
    Returns:
        List of lists of paths, where each inner list contains k shortest paths.
    """
    # Create a copy of the graph to avoid modifying the original
    working_graph = copy.deepcopy(graph)
    
    # Apply all updates to the graph
    for src, dest, capacity, travel_time in updates:
        # Check if edge already exists
        edge_exists = False
        for i, (neighbor, _, _) in enumerate(working_graph.get(src, [])):
            if neighbor == dest:
                # If capacity is 0, remove the edge
                if capacity == 0:
                    working_graph[src].pop(i)
                else:
                    # Update the existing edge
                    working_graph[src][i] = (dest, capacity, travel_time)
                edge_exists = True
                break
        
        # If edge doesn't exist and capacity > 0, add it
        if not edge_exists and capacity > 0:
            if src not in working_graph:
                working_graph[src] = []
            working_graph[src].append((dest, capacity, travel_time))
    
    # Process each request
    results = []
    for src, dest, k in requests:
        paths = find_k_shortest_paths_for_request(working_graph, src, dest, k)
        results.append(paths)
    
    return results

def find_k_shortest_paths_for_request(graph, source, target, k):
    """
    Find the k shortest paths from source to target in the graph.
    
    Args:
        graph: Dictionary representing the road network.
        source: Source node ID.
        target: Target node ID.
        k: Number of shortest paths to find.
    
    Returns:
        List of paths, where each path is a list of node IDs.
    """
    if source not in graph or target not in graph:
        return []
    
    # Use Yen's algorithm to find k shortest paths
    shortest_paths = yen_k_shortest_paths(graph, source, target, k)
    
    return shortest_paths

def dijkstra(graph, source, target=None):
    """
    Run Dijkstra's algorithm to find shortest paths from source.
    
    Args:
        graph: Dictionary representing the road network.
        source: Source node ID.
        target: Optional target node ID. If provided, algorithm stops when target is reached.
    
    Returns:
        Tuple of (distances, predecessors) dictionaries.
    """
    # Initialize distances with infinity for all nodes
    distances = {node: float('infinity') for node in graph}
    distances[source] = 0
    
    # Initialize predecessors
    predecessors = {node: None for node in graph}
    
    # Priority queue for nodes to visit
    priority_queue = [(0, source)]  # (distance, node)
    
    # Set of visited nodes
    visited = set()
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        # Skip if we've already processed this node with a shorter path
        if current_node in visited:
            continue
        
        # If we've reached the target, we can stop
        if target is not None and current_node == target:
            break
        
        visited.add(current_node)
        
        # Process neighbors
        for neighbor, capacity, travel_time in graph.get(current_node, []):
            # Skip edges with 0 capacity
            if capacity == 0:
                continue
                
            distance = current_distance + travel_time
            
            # If we found a shorter path, update distance and predecessor
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))
    
    return distances, predecessors

def construct_path(predecessors, target):
    """
    Construct a path from source to target using predecessors.
    
    Args:
        predecessors: Dictionary of predecessors from Dijkstra's algorithm.
        target: Target node ID.
    
    Returns:
        List of node IDs representing the path, or empty list if no path exists.
    """
    if predecessors[target] is None:
        return []
    
    path = [target]
    current = target
    
    while predecessors[current] is not None:
        current = predecessors[current]
        path.append(current)
    
    # Reverse the path to get source -> target order
    return path[::-1]

def get_path_travel_time(graph, path):
    """
    Calculate the total travel time of a path.
    
    Args:
        graph: Dictionary representing the road network.
        path: List of node IDs representing a path.
    
    Returns:
        Total travel time of the path.
    """
    total_time = 0
    for i in range(len(path) - 1):
        src, dest = path[i], path[i + 1]
        # Find the edge from src to dest
        for neighbor, _, travel_time in graph.get(src, []):
            if neighbor == dest:
                total_time += travel_time
                break
    
    return total_time

def yen_k_shortest_paths(graph, source, target, k):
    """
    Implementation of Yen's algorithm for finding k shortest paths.
    
    Args:
        graph: Dictionary representing the road network.
        source: Source node ID.
        target: Target node ID.
        k: Number of shortest paths to find.
    
    Returns:
        List of paths, where each path is a list of node IDs.
    """
    # Find the shortest path using Dijkstra's algorithm
    _, predecessors = dijkstra(graph, source, target)
    shortest_path = construct_path(predecessors, target)
    
    # If no path exists, return empty list
    if not shortest_path:
        return []
    
    # Initialize the list of k shortest paths with the first shortest path
    k_shortest_paths = [shortest_path]
    
    # Initialize a list of potential k-shortest paths
    potential_paths = []
    
    # Iterate until we have k paths or no more paths can be found
    for i in range(1, k):
        # For each node in the previous shortest path except the last one
        prev_path = k_shortest_paths[i-1]
        
        for j in range(len(prev_path) - 1):
            # The spur node is the node where we deviate from the previous path
            spur_node = prev_path[j]
            
            # The root path is the path from source to the spur node
            root_path = prev_path[:j+1]
            
            # Store edges to remove temporarily
            edges_to_remove = []
            
            # Remove edges that are part of the previous shortest paths with the same root path
            for path in k_shortest_paths:
                if len(path) > j and path[:j+1] == root_path:
                    # The edge to remove is from the spur node to the next node in the path
                    if j + 1 < len(path):
                        u, v = path[j], path[j+1]
                        # Find the edge details
                        for idx, (neighbor, capacity, travel_time) in enumerate(graph.get(u, [])):
                            if neighbor == v:
                                edges_to_remove.append((u, idx, (v, capacity, travel_time)))
                                break
            
            # Remove the edges from the graph
            for u, idx, edge_details in edges_to_remove:
                graph[u].pop(idx)
                
            # Find the shortest path from the spur node to the target
            try:
                _, spur_predecessors = dijkstra(graph, spur_node, target)
                spur_path = construct_path(spur_predecessors, target)
                
                if spur_path:
                    # Complete path is root_path + spur_path[1:]
                    # We exclude the first node of spur_path as it's already in root_path
                    total_path = root_path + spur_path[1:]
                    
                    # Calculate the travel time for this path
                    travel_time = get_path_travel_time(graph, total_path)
                    
                    # Add the path to the potential paths if it's not already there
                    if total_path not in [p for _, p in potential_paths]:
                        heapq.heappush(potential_paths, (travel_time, total_path))
            except Exception:
                # Handle any errors (e.g., disconnected graph)
                pass
            
            # Restore the edges we removed
            for u, _, edge_details in edges_to_remove:
                graph[u].append(edge_details)
        
        # If there are no potential paths left, break
        if not potential_paths:
            break
        
        # Add the next shortest path to the list
        _, next_path = heapq.heappop(potential_paths)
        k_shortest_paths.append(next_path)
    
    return k_shortest_paths