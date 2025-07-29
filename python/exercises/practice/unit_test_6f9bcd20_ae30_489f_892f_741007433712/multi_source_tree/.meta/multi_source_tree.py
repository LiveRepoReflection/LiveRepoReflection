import heapq
from collections import defaultdict

def multi_source_tree(nodes, edges, sources):
    """
    Construct a minimum-weight shortest-path tree rooted at multiple source nodes.
    
    Args:
        nodes: List of node IDs (integers)
        edges: List of tuples (u, v, w) representing directed edges from u to v with weight w
        sources: List of node IDs representing the source nodes
        
    Returns:
        List of tuples (u, v, w) representing the edges in the minimum-weight shortest-path tree
    """
    if not nodes or not edges or not sources:
        return []

    # If all nodes are sources, no edges are needed
    if set(sources) == set(nodes):
        return []

    # Build adjacency list
    graph = defaultdict(list)
    for u, v, w in edges:
        graph[u].append((v, w))
    
    # Initialize distance dictionary and predecessor dictionary
    distances = {node: float('inf') for node in nodes}
    predecessors = {node: None for node in nodes}  # Store the predecessor for each node
    
    # Set distance to 0 for all source nodes
    for source in sources:
        distances[source] = 0
    
    # Priority queue for Dijkstra's algorithm
    # Format: (distance, node, predecessor)
    pq = [(0, source, None) for source in sources]
    heapq.heapify(pq)
    
    # Set to keep track of processed nodes
    processed = set()
    
    # Run modified Dijkstra's algorithm
    while pq:
        current_distance, current_node, predecessor = heapq.heappop(pq)
        
        # Skip if we've already processed this node
        if current_node in processed:
            continue
            
        # Mark as processed
        processed.add(current_node)
        
        # Update the predecessor if this is a non-source node
        if current_node not in sources:
            predecessors[current_node] = predecessor
            
        # Explore neighbors
        for neighbor, weight in graph[current_node]:
            # Only process if not already processed
            if neighbor not in processed:
                # Calculate new distance
                new_distance = current_distance + weight
                
                # If new distance is better, update and add to queue
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    heapq.heappush(pq, (new_distance, neighbor, current_node))
    
    # Construct the shortest-path tree
    tree_edges = []
    for node in nodes:
        if node not in sources and predecessors[node] is not None:
            # Find the edge weight from predecessor to node
            for neighbor, weight in graph[predecessors[node]]:
                if neighbor == node:
                    tree_edges.append((predecessors[node], node, weight))
                    break
    
    # Verify the tree property (no cycles)
    if not _is_tree(tree_edges, nodes, sources):
        # If our tree has cycles, we need a different approach
        # This should not happen with a correct implementation of Dijkstra's algorithm
        # But just in case, we can use a minimum spanning tree algorithm starting from the sources
        tree_edges = _fallback_minimum_spanning_tree(nodes, edges, sources, distances)

    return tree_edges

def _is_tree(edges, nodes, sources):
    """
    Check if the graph formed by edges is a forest (no cycles).
    Each connected component should have exactly one source or be unreachable.
    """
    # Create undirected adjacency list for cycle detection
    undirected_adj = defaultdict(list)
    for u, v, _ in edges:
        undirected_adj[u].append(v)
        undirected_adj[v].append(u)  # Add reverse edge for undirected check
    
    # Helper function for DFS cycle detection
    def has_cycle(node, parent, visited):
        visited.add(node)
        for neighbor in undirected_adj[node]:
            if neighbor not in visited:
                if has_cycle(neighbor, node, visited):
                    return True
            elif neighbor != parent:  # Back edge found (cycle)
                return True
        return False
    
    # Check each component
    visited = set(sources)  # Mark sources as visited
    for node in nodes:
        if node not in visited and node in undirected_adj:
            if has_cycle(node, None, visited):
                return False
    
    return True

def _fallback_minimum_spanning_tree(nodes, edges, sources, distances):
    """
    Construct a minimum spanning tree ensuring shortest paths from sources.
    This is a fallback method in case our main algorithm produces cycles.
    """
    # Create a set of all reachable nodes
    reachable = {node for node in nodes if distances[node] < float('inf')}
    
    # Filter out unreachable nodes and create new edges
    tree_edges = []
    visited = set(sources)
    
    # Sort edges by weight for greedy MST construction
    sorted_edges = []
    for u, v, w in edges:
        if u in reachable and v in reachable:
            # Adjust weight to prioritize edges along shortest paths
            adjusted_weight = w
            if distances[u] + w == distances[v]:  # This edge is on a shortest path
                adjusted_weight = 0  # Prioritize these edges
            sorted_edges.append((u, v, w, adjusted_weight))
    
    sorted_edges.sort(key=lambda x: (x[3], x[2]))  # Sort by adjusted weight, then by original weight
    
    # Kruskal's algorithm for MST
    parent = {node: node for node in reachable}
    
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        parent[find(x)] = find(y)
    
    for u, v, w, _ in sorted_edges:
        if find(u) != find(v):
            union(u, v)
            tree_edges.append((u, v, w))
    
    return tree_edges