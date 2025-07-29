import heapq
from collections import defaultdict, deque
import itertools

def optimize_router_placement(n, edges, k, server_weights):
    """
    Find the optimal placement of k edge routers to minimize weighted average latency.
    
    Args:
        n (int): Number of servers.
        edges (list): List of tuples (u, v) representing undirected edges between servers.
        k (int): Number of edge routers to place.
        server_weights (list): Importance weight of each server.
        
    Returns:
        list: Indices of servers where routers should be placed.
    """
    # Validate inputs
    if not 1 <= k <= n:
        raise ValueError(f"Number of routers k must be between 1 and {n}")
    
    if len(server_weights) != n:
        raise ValueError(f"Server weights must have exactly {n} elements")
    
    for w in server_weights:
        if w <= 0:
            raise ValueError("Server weights must be positive")
    
    # Build adjacency list representation of the graph
    graph = defaultdict(list)
    for u, v in edges:
        if not (0 <= u < n and 0 <= v < n):
            raise ValueError(f"Edge ({u}, {v}) contains an invalid server index")
        graph[u].append(v)
        graph[v].append(u)
    
    # Check if graph is connected
    visited = set()
    queue = deque([0])
    while queue:
        node = queue.popleft()
        if node not in visited:
            visited.add(node)
            queue.extend(neighbor for neighbor in graph[node] if neighbor not in visited)
    
    if len(visited) != n:
        raise ValueError("Graph is not connected")
    
    # Special case: if k equals n, place routers at all nodes
    if k == n:
        return list(range(n))
    
    # For small k values, we can try all combinations of k nodes and find the best
    if k <= 10 and n <= 20:
        return optimal_placement_brute_force(n, graph, k, server_weights)
    
    # For larger graphs, use a greedy approach based on node centrality
    return greedy_centrality_based_placement(n, graph, k, server_weights)


def optimal_placement_brute_force(n, graph, k, server_weights):
    """
    Find the optimal router placement by trying all combinations of k nodes.
    
    Args:
        n (int): Number of servers.
        graph (dict): Adjacency list representation of the graph.
        k (int): Number of edge routers to place.
        server_weights (list): Importance weight of each server.
        
    Returns:
        list: Indices of servers where routers should be placed.
    """
    best_placement = None
    best_latency = float('inf')
    
    for router_nodes in itertools.combinations(range(n), k):
        latency = calculate_weighted_average_latency(n, graph, list(router_nodes), server_weights)
        if latency < best_latency:
            best_latency = latency
            best_placement = list(router_nodes)
    
    return best_placement


def greedy_centrality_based_placement(n, graph, k, server_weights):
    """
    Find router placement using a greedy approach based on node centrality.
    
    Args:
        n (int): Number of servers.
        graph (dict): Adjacency list representation of the graph.
        k (int): Number of edge routers to place.
        server_weights (list): Importance weight of each server.
        
    Returns:
        list: Indices of servers where routers should be placed.
    """
    # Calculate weighted degree centrality for each node
    centrality = []
    for node in range(n):
        # Weighted degree centrality: degree * node_weight
        w_degree = len(graph[node]) * server_weights[node]
        centrality.append((node, w_degree))
    
    # Sort nodes by centrality (descending)
    centrality.sort(key=lambda x: x[1], reverse=True)
    
    # Initial selection based on centrality
    router_nodes = [centrality[i][0] for i in range(k)]
    
    # Iteratively improve the solution using local search
    improved = True
    iterations = 0
    max_iterations = 100  # Limit the number of iterations
    
    while improved and iterations < max_iterations:
        improved = False
        iterations += 1
        
        current_latency = calculate_weighted_average_latency(n, graph, router_nodes, server_weights)
        
        # Try to swap each selected node with a non-selected node
        for i, current_node in enumerate(router_nodes):
            for new_node in range(n):
                if new_node in router_nodes:
                    continue
                
                # Create a new placement by swapping nodes
                new_placement = router_nodes.copy()
                new_placement[i] = new_node
                
                # Calculate the latency with the new placement
                new_latency = calculate_weighted_average_latency(n, graph, new_placement, server_weights)
                
                # If the new placement is better, accept it
                if new_latency < current_latency:
                    router_nodes = new_placement
                    current_latency = new_latency
                    improved = True
                    break
            
            if improved:
                break
    
    return router_nodes


def calculate_weighted_average_latency(n, graph, router_nodes, server_weights):
    """
    Calculate the weighted average latency for a given router placement.
    
    Args:
        n (int): Number of servers.
        graph (dict): Adjacency list representation of the graph.
        router_nodes (list): Indices of servers where routers are placed.
        server_weights (list): Importance weight of each server.
        
    Returns:
        float: The weighted average latency.
    """
    total_weighted_latency = 0
    total_weight = sum(server_weights)
    
    # For each server, find the shortest path to the nearest router
    for server in range(n):
        if server in router_nodes:
            latency = 0  # Server has a router directly
        else:
            # Use BFS to find the shortest path to a router
            latency = shortest_path_to_router(graph, server, router_nodes)
        
        total_weighted_latency += latency * server_weights[server]
    
    return total_weighted_latency / total_weight


def shortest_path_to_router(graph, start_node, router_nodes):
    """
    Find the shortest path from a node to any router using BFS.
    
    Args:
        graph (dict): Adjacency list representation of the graph.
        start_node (int): Starting node.
        router_nodes (list): List of nodes where routers are placed.
        
    Returns:
        int: Length of the shortest path to a router.
    """
    if start_node in router_nodes:
        return 0
    
    visited = set([start_node])
    queue = deque([(start_node, 0)])  # (node, distance)
    
    while queue:
        node, distance = queue.popleft()
        
        for neighbor in graph[node]:
            if neighbor in router_nodes:
                return distance + 1  # Found a router
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, distance + 1))
    
    return float('inf')  # No path to a router (should not happen in a connected graph)