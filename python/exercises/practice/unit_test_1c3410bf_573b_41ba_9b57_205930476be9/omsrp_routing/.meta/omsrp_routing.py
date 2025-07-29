import heapq
from collections import defaultdict

def find_best_paths(graph, sources, destination, k, max_path_length, min_node_diversity, min_edge_diversity):
    """
    Find the k best paths from any of the source nodes to the destination node.
    
    Args:
        graph: A dictionary representing an undirected graph with edge costs
        sources: A list of source node IDs
        destination: The destination node ID
        k: The number of best paths to find
        max_path_length: The maximum number of edges a path can contain
        min_node_diversity: Minimum number of distinct nodes required across all k paths
        min_edge_diversity: Minimum number of distinct edges required across all k paths
        
    Returns:
        A list of the k best paths sorted by path cost
    """
    # Validate inputs
    for source in sources:
        if source not in graph:
            continue
    
    if destination not in graph:
        return []
    
    # Early check for source being destination
    if destination in sources:
        return [[destination]]
    
    # Use modified Yen's algorithm to find k-shortest loopless paths
    candidate_paths = []
    final_paths = []
    
    # Use a priority queue for candidate paths (cost, path)
    pq = []
    
    # Initialize with Dijkstra's for each source to find the shortest path
    for source in sources:
        if source in graph:
            shortest_path = dijkstra(graph, source, destination, max_path_length)
            if shortest_path:
                cost = calculate_path_cost(graph, shortest_path)
                heapq.heappush(pq, (cost, shortest_path))
    
    # Track used paths to avoid duplicates
    used_paths = set()
    
    # Find up to k paths
    while pq and len(final_paths) < k:
        cost, current_path = heapq.heappop(pq)
        
        # Convert path to tuple for hashable comparison
        path_tuple = tuple(current_path)
        if path_tuple in used_paths:
            continue
            
        used_paths.add(path_tuple)
        final_paths.append(current_path)
        
        # For each node in the current path (except the last)
        for i in range(len(current_path) - 1):
            # The root path is the path up to the deviation node
            root_path = current_path[:i]
            
            # The deviation node is where we'll explore alternatives
            deviation_node = current_path[i]
            
            # Create a modified graph excluding edges from the current path
            # to force finding alternative paths
            modified_graph = graph.copy()
            
            # Remove edges that would create cycles with the root path
            for j in range(len(root_path)):
                if j+1 < len(root_path) and root_path[j+1] in modified_graph.get(root_path[j], {}):
                    # Create a deep copy if needed
                    if isinstance(modified_graph[root_path[j]], dict):
                        modified_graph[root_path[j]] = modified_graph[root_path[j]].copy()
                    
                    # Remove the edge to prevent reusing this subpath
                    del modified_graph[root_path[j]][root_path[j+1]]
                    
                    # Remove the reverse edge as well (for undirected graph)
                    if root_path[j] in modified_graph.get(root_path[j+1], {}):
                        if isinstance(modified_graph[root_path[j+1]], dict):
                            modified_graph[root_path[j+1]] = modified_graph[root_path[j+1]].copy()
                        del modified_graph[root_path[j+1]][root_path[j]]
            
            # Also remove the current link at the deviation point to force a different path
            if i+1 < len(current_path) and current_path[i+1] in modified_graph.get(deviation_node, {}):
                if isinstance(modified_graph[deviation_node], dict):
                    modified_graph[deviation_node] = modified_graph[deviation_node].copy()
                del modified_graph[deviation_node][current_path[i+1]]
                
                # Remove the reverse edge
                if deviation_node in modified_graph.get(current_path[i+1], {}):
                    if isinstance(modified_graph[current_path[i+1]], dict):
                        modified_graph[current_path[i+1]] = modified_graph[current_path[i+1]].copy()
                    del modified_graph[current_path[i+1]][deviation_node]
            
            # Find a new shortest path from the deviation node to the destination
            alternate_suffix = dijkstra(modified_graph, deviation_node, destination, 
                                       max_path_length - i if max_path_length is not None else None)
            
            if alternate_suffix:
                # Ensure the alternate suffix doesn't contain nodes from the root path (avoid cycles)
                root_set = set(root_path)
                if len([n for n in alternate_suffix if n in root_set]) == 0:  # No overlap
                    new_path = root_path + alternate_suffix
                    
                    # Check if the new path meets the max length constraint
                    if len(new_path) - 1 <= max_path_length:
                        path_cost = calculate_path_cost(graph, new_path)
                        # Check if this path is already in the queue or final paths
                        if tuple(new_path) not in used_paths:
                            heapq.heappush(pq, (path_cost, new_path))
    
    # If we have fewer than k paths, return what we have
    if len(final_paths) < k:
        return final_paths
    
    # Now we need to check and optimize for diversity
    best_paths = optimize_for_diversity(graph, final_paths, k, min_node_diversity, min_edge_diversity)
    
    return best_paths

def dijkstra(graph, start, end, max_length=None):
    """
    Dijkstra's algorithm to find the shortest path from start to end.
    
    Args:
        graph: A dictionary representing the graph
        start: The start node
        end: The end node
        max_length: Maximum path length (number of edges)
        
    Returns:
        The shortest path as a list of nodes, or None if no path exists
    """
    if start not in graph or end not in graph:
        return None
        
    if start == end:
        return [start]
    
    # Priority queue: (cost, node, path, path_length)
    pq = [(0, start, [start], 0)]
    visited = set()
    
    while pq:
        (cost, current, path, path_length) = heapq.heappop(pq)
        
        if current == end:
            return path
        
        if current in visited:
            continue
            
        visited.add(current)
        
        # If we've reached the maximum path length, don't explore further
        if max_length is not None and path_length >= max_length:
            continue
        
        for neighbor, edge_cost in graph.get(current, {}).items():
            if neighbor not in visited and neighbor not in path:  # Avoid cycles
                new_cost = cost + edge_cost
                new_path = path + [neighbor]
                heapq.heappush(pq, (new_cost, neighbor, new_path, path_length + 1))
    
    return None  # No path found

def calculate_path_cost(graph, path):
    """Calculate the total cost of a path."""
    cost = 0
    for i in range(len(path) - 1):
        cost += graph[path[i]][path[i+1]]
    return cost

def optimize_for_diversity(graph, paths, k, min_node_diversity, min_edge_diversity):
    """
    Optimize the set of paths for both node and edge diversity.
    
    Args:
        graph: The network graph
        paths: All candidate paths sorted by cost
        k: Number of paths to select
        min_node_diversity: Minimum number of distinct nodes required
        min_edge_diversity: Minimum number of distinct edges required
        
    Returns:
        A list of up to k paths that maximize diversity while minimizing cost
    """
    if len(paths) <= k:
        return paths
    
    # Try all combinations of k paths from the available paths
    best_diversity_score = -1
    best_paths = paths[:k]  # Default to the k lowest-cost paths
    
    # Compute path costs once
    path_costs = [calculate_path_cost(graph, path) for path in paths]
    total_cost = sum(path_costs[:k])
    
    # Generate all possible combinations of k paths
    from itertools import combinations
    
    # Limit the number of combinations to check for performance
    # Use the first 2k paths to generate combinations
    max_paths_to_consider = min(len(paths), 2 * k)
    
    for combo_indices in combinations(range(max_paths_to_consider), k):
        combo_paths = [paths[i] for i in combo_indices]
        
        # Calculate node diversity (excluding destination)
        unique_nodes = set()
        for path in combo_paths:
            for node in path[:-1]:  # Exclude destination
                unique_nodes.add(node)
        node_diversity = len(unique_nodes)
        
        # Calculate edge diversity
        unique_edges = set()
        for path in combo_paths:
            for i in range(len(path) - 1):
                # Make edges undirected by sorting the nodes
                edge = tuple(sorted([path[i], path[i+1]]))
                unique_edges.add(edge)
        edge_diversity = len(unique_edges)
        
        # Calculate the total cost of this combination
        combo_cost = sum(path_costs[i] for i in combo_indices)
        
        # Calculate a diversity score that prioritizes node diversity then edge diversity
        diversity_score = node_diversity * 1000 + edge_diversity
        
        # If this combination has better diversity, or same diversity with lower cost
        if (diversity_score > best_diversity_score or 
            (diversity_score == best_diversity_score and combo_cost < total_cost)):
            best_diversity_score = diversity_score
            best_paths = combo_paths
            total_cost = combo_cost
    
    # Sort the best paths by cost before returning
    return sorted(best_paths, key=lambda p: calculate_path_cost(graph, p))