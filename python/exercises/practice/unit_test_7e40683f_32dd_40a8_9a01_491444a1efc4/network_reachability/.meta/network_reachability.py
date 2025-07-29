from collections import defaultdict, deque


def is_reachable(node_data, start_node, end_node, max_hops):
    """
    Determines if end_node is reachable from start_node within max_hops in a decentralized network.
    
    Args:
        node_data: List of tuples (node_id, neighbor_list, distant_node_list)
        start_node: The starting node ID
        end_node: The destination node ID
        max_hops: Maximum number of hops allowed
        
    Returns:
        True if end_node is reachable from start_node within max_hops, False otherwise
    """
    # Handle edge cases
    if not node_data:
        return False
    
    if start_node == end_node:
        return max_hops >= 0
    
    # Build an adjacency list from the network data
    # We only use direct connections (neighbor_list) for path finding
    graph = defaultdict(list)
    
    # Dictionary to keep track of nodes that exist in the network
    node_exists = set()
    
    for node_id, neighbors, _ in node_data:
        graph[node_id].extend(neighbors)
        node_exists.add(node_id)
        for neighbor in neighbors:
            node_exists.add(neighbor)
    
    # Check if both start_node and end_node exist in the network
    if start_node not in node_exists or end_node not in node_exists:
        return False
    
    # BFS to find the shortest path within max_hops
    queue = deque([(start_node, 0)])  # (node, hops)
    visited = set([start_node])
    
    while queue:
        current_node, hops = queue.popleft()
        
        if current_node == end_node:
            return True
        
        # If we've reached max_hops, don't explore further from this node
        if hops >= max_hops:
            continue
        
        # Explore neighbors
        for neighbor in graph[current_node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, hops + 1))
    
    return False