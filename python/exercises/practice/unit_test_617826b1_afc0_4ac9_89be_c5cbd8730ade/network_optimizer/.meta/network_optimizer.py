import heapq
from collections import defaultdict, deque

def design_network(N, M, K, communication_requests, cost):
    """
    Designs a network topology with minimal cost that satisfies all communication requests
    while ensuring each node has at most K direct connections.
    
    Args:
        N: Number of nodes (0 to N-1)
        M: Number of communication requests
        K: Maximum number of direct connections per node
        communication_requests: List of tuples (source, destination, data_size)
        cost: Function that calculates the cost between two nodes
        
    Returns:
        List of tuples representing direct links in the network topology
    """
    # Build a cost cache to avoid redundant calls to the cost function
    cost_cache = {}
    
    def get_cost(i, j):
        """Get cost from cache or calculate it if not cached"""
        if i > j:
            i, j = j, i  # Normalize to ensure i <= j
        if (i, j) not in cost_cache:
            cost_cache[(i, j)] = cost(i, j)
        return cost_cache[(i, j)]
    
    # Process communication requests to determine traffic demands between pairs of nodes
    traffic_demands = defaultdict(int)
    for source, dest, data_size in communication_requests:
        if source > dest:
            source, dest = dest, source  # Normalize to ensure source <= dest
        traffic_demands[(source, dest)] += data_size
    
    # Initial topology - empty
    topology = []
    # Track number of connections per node
    connections = [0] * N
    # Adjacency list for the current topology
    adjacency = [[] for _ in range(N)]
    
    # Helper function to check if a path exists between two nodes
    def path_exists(source, dest):
        if source == dest:
            return True
        visited = [False] * N
        queue = deque([source])
        visited[source] = True
        
        while queue:
            current = queue.popleft()
            for neighbor in adjacency[current]:
                if neighbor == dest:
                    return True
                if not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append(neighbor)
        return False
    
    # Sort the traffic demands by data size (descending) to prioritize heavier traffic
    sorted_demands = sorted(traffic_demands.items(), key=lambda x: x[1], reverse=True)
    
    # First pass: Direct connections for the highest traffic demands
    for (source, dest), data_size in sorted_demands:
        # Skip if path already exists or either node has reached max connections
        if path_exists(source, dest) or connections[source] >= K or connections[dest] >= K:
            continue
        
        # Add direct connection
        topology.append((source, dest))
        connections[source] += 1
        connections[dest] += 1
        adjacency[source].append(dest)
        adjacency[dest].append(source)
    
    # Second pass: Handle remaining traffic demands using MST-like approach for each component
    remaining_demands = []
    for (source, dest), data_size in sorted_demands:
        if not path_exists(source, dest):
            remaining_demands.append((source, dest, data_size))
    
    # For each component, connect the nodes efficiently
    while remaining_demands:
        # Find unconnected components
        components = []
        visited = [False] * N
        
        for i in range(N):
            if not visited[i]:
                component = []
                queue = deque([i])
                visited[i] = True
                
                while queue:
                    node = queue.popleft()
                    component.append(node)
                    for neighbor in adjacency[node]:
                        if not visited[neighbor]:
                            visited[neighbor] = True
                            queue.append(neighbor)
                
                components.append(component)
        
        # Process each remaining demand
        source, dest, _ = remaining_demands[0]
        
        # Find the components containing source and dest
        source_component = None
        dest_component = None
        
        for comp in components:
            if source in comp:
                source_component = comp
            if dest in comp:
                dest_component = comp
        
        if source_component == dest_component:
            # They're already in the same component, so the path exists
            remaining_demands.pop(0)
            continue
        
        # Find the best pair of nodes to connect these components
        best_cost = float('inf')
        best_pair = None
        
        for s in source_component:
            if connections[s] >= K:
                continue
            
            for d in dest_component:
                if connections[d] >= K:
                    continue
                
                c = get_cost(s, d)
                if c < best_cost:
                    best_cost = c
                    best_pair = (s, d)
        
        if best_pair:
            s, d = best_pair
            topology.append((s, d))
            connections[s] += 1
            connections[d] += 1
            adjacency[s].append(d)
            adjacency[d].append(s)
            # Reprocess remaining demands as some paths might now exist
            remaining_demands = [(s, d, size) for s, d, size in remaining_demands if not path_exists(s, d)]
        else:
            # No valid pair found to connect components
            # This should not happen given the problem guarantee that a solution exists
            # But just in case, we'll skip this demand
            remaining_demands.pop(0)
    
    # Third pass: Optimize the network by adding shortcut links if we have spare connections
    # This is a greedy approach to reduce path lengths where possible
    
    # Identify nodes with spare connections
    spare_connections = [(i, K - connections[i]) for i in range(N) if connections[i] < K]
    
    if spare_connections:
        # For each high traffic demand, try to add a direct link if it doesn't exist
        for (source, dest), data_size in sorted_demands:
            if (source, dest) in topology or (dest, source) in topology:
                continue  # Direct link already exists
            
            # Check if both nodes have spare connections
            source_spare = K - connections[source] if connections[source] < K else 0
            dest_spare = K - connections[dest] if connections[dest] < K else 0
            
            if source_spare > 0 and dest_spare > 0:
                # Add direct link
                topology.append((source, dest))
                connections[source] += 1
                connections[dest] += 1
                adjacency[source].append(dest)
                adjacency[dest].append(source)
    
    return topology