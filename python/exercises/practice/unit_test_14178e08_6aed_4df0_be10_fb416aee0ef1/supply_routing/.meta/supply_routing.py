import heapq
from collections import defaultdict

def min_cost_flow(N, M, capacities, demands, costs):
    """
    Solves the min-cost flow problem for supply routing.
    
    Args:
        N (int): The number of warehouses.
        M (int): The number of retail stores.
        capacities (List[int]): Capacities of each warehouse.
        demands (List[int]): Demands of each retail store.
        costs (List[List[int]]): Cost matrix for transportation.
    
    Returns:
        List[List[int]] or None: The optimal flow matrix or None if no solution exists.
    """
    # Check if a solution is feasible
    total_capacity = sum(capacities)
    total_demand = sum(demands)
    
    if total_capacity < total_demand:
        return None
    
    # Create a network flow graph representation
    # Nodes: 0 to N-1 are warehouses, N to N+M-1 are retail stores, 
    # N+M is source, N+M+1 is sink
    source = N + M
    sink = N + M + 1
    
    # Initialize graph as an adjacency list with costs and capacities
    graph = defaultdict(dict)
    
    # Connect source to warehouses with warehouse capacities
    for i in range(N):
        graph[source][i] = {'capacity': capacities[i], 'cost': 0, 'flow': 0}
        graph[i][source] = {'capacity': 0, 'cost': 0, 'flow': 0}  # Reverse edge for residual graph
    
    # Connect warehouses to retail stores with infinite capacity and specified costs
    for i in range(N):
        for j in range(M):
            store_node = N + j
            graph[i][store_node] = {'capacity': float('inf'), 'cost': costs[i][j], 'flow': 0}
            graph[store_node][i] = {'capacity': 0, 'cost': -costs[i][j], 'flow': 0}  # Reverse edge
    
    # Connect retail stores to sink with store demands
    for j in range(M):
        store_node = N + j
        graph[store_node][sink] = {'capacity': demands[j], 'cost': 0, 'flow': 0}
        graph[sink][store_node] = {'capacity': 0, 'cost': 0, 'flow': 0}  # Reverse edge
    
    # Run successive shortest path algorithm
    total_flow = 0
    while total_flow < total_demand:
        # Find shortest path using Dijkstra's algorithm
        dist, prev = find_shortest_path(graph, source, sink)
        
        if prev[sink] is None:
            return None  # No augmenting path exists, no solution
        
        # Find bottleneck capacity
        path_capacity = float('inf')
        node = sink
        while node != source:
            parent = prev[node]
            path_capacity = min(path_capacity, graph[parent][node]['capacity'] - graph[parent][node]['flow'])
            node = parent
        
        # Update flow along the path
        node = sink
        while node != source:
            parent = prev[node]
            graph[parent][node]['flow'] += path_capacity
            graph[node][parent]['flow'] -= path_capacity  # Update reverse edge
            node = parent
        
        total_flow += path_capacity
    
    # Extract the flow matrix from the graph
    flow_matrix = [[0 for _ in range(M)] for _ in range(N)]
    for i in range(N):
        for j in range(M):
            store_node = N + j
            if store_node in graph[i]:
                flow_matrix[i][j] = graph[i][store_node]['flow']
    
    return flow_matrix

def find_shortest_path(graph, source, sink):
    """
    Finds the shortest path from source to sink in a residual graph using Dijkstra's algorithm.
    
    Args:
        graph: Adjacency list representation of the graph.
        source: Source node.
        sink: Sink node.
    
    Returns:
        Tuple of (distances, predecessors)
    """
    dist = defaultdict(lambda: float('inf'))
    dist[source] = 0
    prev = defaultdict(lambda: None)
    
    pq = [(0, source)]  # Priority queue with (distance, node)
    visited = set()
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        
        if current in visited:
            continue
        
        visited.add(current)
        
        if current == sink:
            break
        
        for neighbor in graph[current]:
            edge = graph[current][neighbor]
            # Only consider edges with remaining capacity
            if edge['capacity'] > edge['flow']:
                new_dist = current_dist + edge['cost']
                if new_dist < dist[neighbor]:
                    dist[neighbor] = new_dist
                    prev[neighbor] = current
                    heapq.heappush(pq, (new_dist, neighbor))
    
    return dist, prev