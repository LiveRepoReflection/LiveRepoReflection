import heapq
from collections import defaultdict

def optimal_multi_source_spt(num_nodes, edges, source_nodes):
    """
    Construct an Optimal Multi-Source Shortest Path Tree.
    
    Args:
        num_nodes: Number of nodes in the graph (nodes are 0 to num_nodes-1)
        edges: List of tuples (u, v, w) representing a directed edge from u to v with weight w
        source_nodes: List of source nodes
    
    Returns:
        List of tuples (u, v, w) representing the edges of the OMS-SPT
    """
    # Build adjacency list representation of the input graph
    graph = defaultdict(list)
    for u, v, w in edges:
        graph[u].append((v, w))
    
    # Store shortest distances from any source node and the nearest source node
    # Distance is initialized to infinity for all nodes except source nodes
    # Nearest source is initialized to None
    distances = {node: float('inf') for node in range(num_nodes)}
    nearest_source = {node: None for node in range(num_nodes)}
    
    # Initialize priority queue for Dijkstra's algorithm
    # Format: (distance, node, source)
    priority_queue = []
    
    # Initialize the distances and priority queue with source nodes
    for source in source_nodes:
        distances[source] = 0
        nearest_source[source] = source
        heapq.heappush(priority_queue, (0, source, source))
    
    # Dictionary to store the edge that led to each node in the shortest path
    # Format: predecessor[node] = (from_node, weight)
    predecessor = {}
    
    # Run multi-source Dijkstra's algorithm
    while priority_queue:
        curr_dist, curr_node, source = heapq.heappop(priority_queue)
        
        # Skip if we've already found a better path
        if curr_dist > distances[curr_node]:
            continue
        
        # If we have a tie in distances, choose the source with the smallest ID
        if curr_dist == distances[curr_node] and source > nearest_source[curr_node]:
            continue
            
        # Process neighbors
        for neighbor, weight in graph[curr_node]:
            distance = curr_dist + weight
            
            # If we found a shorter path or a path from a source with smaller ID
            # when distance is equal to current distance
            if (distance < distances[neighbor] or 
                (distance == distances[neighbor] and source < nearest_source[neighbor])):
                
                distances[neighbor] = distance
                nearest_source[neighbor] = source
                predecessor[neighbor] = (curr_node, weight)
                heapq.heappush(priority_queue, (distance, neighbor, source))
    
    # Construct the optimal multi-source shortest path tree from the predecessor dictionary
    tree_edges = []
    
    # For each node, add the edge that led to it from its predecessor
    for node in range(num_nodes):
        # Skip source nodes and unreachable nodes
        if node in source_nodes or nearest_source[node] is None:
            continue
        
        if node in predecessor:
            pred_node, weight = predecessor[node]
            tree_edges.append((pred_node, node, weight))
    
    return tree_edges