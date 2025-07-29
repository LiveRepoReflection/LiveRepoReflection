import heapq
from collections import defaultdict, deque

def minimize_congestion(N, M, edges, K, flows, L, P):
    """
    Minimize network congestion by strategically prioritizing edges.
    
    Parameters:
    N (int): Number of nodes in the network
    M (int): Number of edges in the network
    edges (list): List of tuples (u, v, capacity) representing edges
    K (int): Number of data flows
    flows (list): List of tuples (source, destination, bandwidth) representing flows
    L (int): Maximum number of edges to prioritize
    P (int): Percentage by which the bandwidth requirement is reduced for prioritized edges
    
    Returns:
    list: List of edge indices to prioritize
    """
    # If no prioritization is allowed, return an empty list
    if L == 0:
        return []
    
    # Build the adjacency list for the graph
    graph = build_graph(N, edges)
    
    # Try different combinations of edges to prioritize
    return optimize_prioritization(N, M, edges, K, flows, L, P, graph)

def build_graph(N, edges):
    """
    Build an adjacency list representation of the graph.
    
    Parameters:
    N (int): Number of nodes
    edges (list): List of edges (u, v, capacity)
    
    Returns:
    dict: Adjacency list where graph[u] is a list of (v, capacity, edge_idx) tuples
    """
    graph = defaultdict(list)
    for idx, (u, v, capacity) in enumerate(edges):
        graph[u].append((v, capacity, idx))
        graph[v].append((u, capacity, idx))  # Bidirectional edge
    return graph

def optimize_prioritization(N, M, edges, K, flows, L, P, graph):
    """
    Find the optimal set of edges to prioritize.
    
    This implementation uses a greedy approach with edge scoring:
    1. Calculate initial congestion without prioritization
    2. Score each edge based on potential congestion reduction
    3. Prioritize the L edges with highest scores
    
    Parameters:
    N, M, edges, K, flows, L, P: As in the main function
    graph: Adjacency list representation of the network
    
    Returns:
    list: Edge indices to prioritize
    """
    # Calculate initial routes and congestion
    edge_flows = defaultdict(float)
    initial_routes = []
    
    for src, dst, bandwidth in flows:
        # Find shortest path for each flow (by number of hops)
        path = shortest_path(graph, src, dst)
        if not path:
            # Source and destination are disconnected
            continue
            
        initial_routes.append((path, bandwidth))
        
        # Update edge flow usage
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            edge_idx = get_edge_idx(graph, u, v)
            edge_flows[edge_idx] += bandwidth
    
    # Calculate initial congestion for each edge
    congestion = {}
    for idx, (u, v, capacity) in enumerate(edges):
        if edge_flows[idx] > 0:
            congestion[idx] = edge_flows[idx] / capacity
    
    if not congestion:
        # No valid flows or all flows have zero bandwidth
        return []
        
    # Calculate potential benefit of prioritizing each edge
    edge_scores = []
    for edge_idx, current_congestion in congestion.items():
        u, v, capacity = edges[edge_idx]
        flow_on_edge = edge_flows[edge_idx]
        
        # Calculate congestion if this edge is prioritized
        reduced_flow = flow_on_edge * (1 - P/100)
        new_congestion = reduced_flow / capacity
        
        # Score is the reduction in congestion
        score = current_congestion - new_congestion
        edge_scores.append((score, edge_idx))
    
    # Sort edges by score (highest first)
    edge_scores.sort(reverse=True)
    
    # Prioritize top L edges with positive score
    prioritized_edges = [edge_idx for score, edge_idx in edge_scores[:L] if score > 0]
    
    # If we couldn't fill L slots with positive-scoring edges, try a more advanced approach
    if len(prioritized_edges) < L and L > 0:
        return advanced_optimization(N, M, edges, K, flows, L, P, graph)
    
    return prioritized_edges

def advanced_optimization(N, M, edges, K, flows, L, P, graph):
    """
    More advanced optimization approach that considers rerouting of flows.
    
    This uses a simulated annealing-like approach to explore different combinations.
    
    Parameters:
    N, M, edges, K, flows, L, P, graph: As in previous functions
    
    Returns:
    list: Edge indices to prioritize
    """
    # Start with empty prioritization
    best_prioritization = []
    best_congestion = float('inf')
    
    # Create a candidate list of edges to consider for prioritization
    candidate_edges = [idx for idx in range(M)]
    
    # Try different combinations of prioritized edges
    for iteration in range(min(100, 2**min(M, 15))):  # Limit iterations for large graphs
        # Create a new prioritization based on iteration strategy
        if iteration == 0:
            # First try - empty prioritization as baseline
            current_prioritization = []
        elif iteration == 1 and L > 0:
            # Second try - prioritize most used edges
            edge_usage = get_edge_usage(graph, edges, flows)
            current_prioritization = [idx for usage, idx in 
                                     sorted(edge_usage.items(), key=lambda x: x[0], reverse=True)[:L]]
        else:
            # Subsequent tries - random selection or other strategies
            import random
            current_prioritization = random.sample(candidate_edges, min(L, len(candidate_edges)))
        
        # Calculate congestion with this prioritization
        current_congestion = calculate_max_congestion(N, edges, flows, current_prioritization, P, graph)
        
        # Update best solution if needed
        if current_congestion < best_congestion:
            best_congestion = current_congestion
            best_prioritization = current_prioritization.copy()
    
    return best_prioritization

def get_edge_usage(graph, edges, flows):
    """
    Calculate how many flows use each edge.
    
    Parameters:
    graph: Adjacency list
    edges: List of edges
    flows: List of flows
    
    Returns:
    dict: Map from edge index to number of flows using it
    """
    edge_usage = defaultdict(int)
    
    for src, dst, bandwidth in flows:
        path = shortest_path(graph, src, dst)
        if not path:
            continue
            
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            edge_idx = get_edge_idx(graph, u, v)
            edge_usage[edge_idx] += bandwidth
    
    return edge_usage

def calculate_max_congestion(N, edges, flows, prioritized_edges, P, graph):
    """
    Calculate the maximum congestion with a given set of prioritized edges.
    
    Parameters:
    N: Number of nodes
    edges: List of edges
    flows: List of flows
    prioritized_edges: List of edge indices to prioritize
    P: Prioritization percentage
    graph: Adjacency list
    
    Returns:
    float: Maximum congestion across all edges
    """
    # Create a modified graph with prioritized edges
    modified_graph = create_prioritized_graph(N, edges, prioritized_edges, P, graph)
    
    # Calculate routes and edge loads
    edge_loads = defaultdict(float)
    for src, dst, bandwidth in flows:
        path = dijkstra(modified_graph, src, dst)
        if not path:
            continue
            
        # For each edge in the path, update load
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            edge_idx = get_edge_idx(graph, u, v)
            
            # Apply reduction if edge is prioritized
            effective_bandwidth = bandwidth
            if edge_idx in prioritized_edges:
                effective_bandwidth *= (1 - P/100)
                
            edge_loads[edge_idx] += effective_bandwidth
    
    # Calculate congestion for each edge
    max_congestion = 0
    for idx, (u, v, capacity) in enumerate(edges):
        if edge_loads[idx] > 0:
            congestion = edge_loads[idx] / capacity
            max_congestion = max(max_congestion, congestion)
    
    return max_congestion

def create_prioritized_graph(N, edges, prioritized_edges, P, original_graph):
    """
    Create a graph with modified weights for prioritized edges for Dijkstra's algorithm.
    
    Parameters:
    N: Number of nodes
    edges: List of edges
    prioritized_edges: List of prioritized edge indices
    P: Prioritization percentage
    original_graph: Original adjacency list
    
    Returns:
    dict: Modified graph for routing
    """
    prioritized_graph = defaultdict(list)
    
    for node in range(N):
        for neighbor, capacity, edge_idx in original_graph[node]:
            weight = 1  # Basic weight for hop count
            
            # If this edge is prioritized, make it more attractive for routing
            if edge_idx in prioritized_edges:
                weight = 0.5  # Lower weight to prefer this edge
                
            prioritized_graph[node].append((neighbor, weight, edge_idx))
    
    return prioritized_graph

def shortest_path(graph, start, end):
    """
    Find shortest path (fewest hops) from start to end.
    
    Parameters:
    graph: Adjacency list
    start: Start node
    end: End node
    
    Returns:
    list: Path from start to end, or [] if no path exists
    """
    if start == end:
        return [start]
        
    visited = set()
    queue = deque([(start, [start])])
    
    while queue:
        node, path = queue.popleft()
        
        if node == end:
            return path
            
        if node in visited:
            continue
            
        visited.add(node)
        
        for neighbor, _, _ in graph[node]:
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))
    
    return []  # No path found

def dijkstra(graph, start, end):
    """
    Find shortest path using Dijkstra's algorithm with modified weights.
    
    Parameters:
    graph: Adjacency list with weights
    start: Start node
    end: End node
    
    Returns:
    list: Shortest path from start to end
    """
    if start == end:
        return [start]
        
    # Priority queue for Dijkstra
    pq = [(0, start, [start])]
    visited = set()
    
    while pq:
        cost, node, path = heapq.heappop(pq)
        
        if node == end:
            return path
            
        if node in visited:
            continue
            
        visited.add(node)
        
        for neighbor, weight, _ in graph[node]:
            if neighbor not in visited:
                heapq.heappush(pq, (cost + weight, neighbor, path + [neighbor]))
    
    return []  # No path found

def get_edge_idx(graph, u, v):
    """
    Helper function to get the edge index between two nodes.
    
    Parameters:
    graph: Adjacency list
    u, v: The two nodes
    
    Returns:
    int: Edge index
    """
    for neighbor, _, edge_idx in graph[u]:
        if neighbor == v:
            return edge_idx
    return -1  # Should not happen if the graph is properly built