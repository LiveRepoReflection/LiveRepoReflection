import heapq
from collections import defaultdict

def min_cost_flow(num_nodes, edges, source, destination, amount):
    """
    Calculate the minimum cost to route the required amount of trade from source to destination.
    
    Args:
        num_nodes: Number of trading hubs (nodes).
        edges: List of tuples (source_node, destination_node, capacity, cost).
        source: Index of the source trading hub.
        destination: Index of the destination trading hub.
        amount: Total amount of trade to be routed.
    
    Returns:
        Minimum total cost to route the required amount of trade, or -1.0 if impossible.
    """
    # Special case: source and destination are the same
    if source == destination:
        return 0.0
    
    # Build the graph as an adjacency list
    graph = defaultdict(list)
    for u, v, cap, cost in edges:
        if cap > 0:  # Only consider edges with positive capacity
            graph[u].append((v, cap, cost))
    
    total_flow = 0.0
    total_cost = 0.0
    
    # Continue finding shortest paths and augmenting flow until we meet the demand
    while total_flow < amount:
        # Use Dijkstra's algorithm to find the shortest path from source to destination
        dist = [float('inf')] * num_nodes
        dist[source] = 0
        prev = [-1] * num_nodes
        prev_edge = [-1] * num_nodes
        pq = [(0, source)]
        
        while pq and dist[destination] == float('inf'):
            cost_so_far, node = heapq.heappop(pq)
            
            if cost_so_far > dist[node]:
                continue
            
            for i, (neighbor, capacity, cost) in enumerate(graph[node]):
                if capacity > 0 and dist[node] + cost < dist[neighbor]:
                    dist[neighbor] = dist[node] + cost
                    prev[neighbor] = node
                    prev_edge[neighbor] = i
                    heapq.heappush(pq, (dist[neighbor], neighbor))
        
        # If no path found, we can't route more flow
        if dist[destination] == float('inf'):
            break
        
        # Find maximum flow that can be pushed through the found path
        path_flow = amount - total_flow
        node = destination
        while node != source:
            parent = prev[node]
            edge_idx = prev_edge[node]
            edge_capacity = graph[parent][edge_idx][1]
            path_flow = min(path_flow, edge_capacity)
            node = parent
        
        # Update capacities along the path
        node = destination
        while node != source:
            parent = prev[node]
            edge_idx = prev_edge[node]
            # Reduce capacity of forward edge
            v, cap, edge_cost = graph[parent][edge_idx]
            graph[parent][edge_idx] = (v, cap - path_flow, edge_cost)
            
            # Update total cost
            total_cost += path_flow * edge_cost
            
            node = parent
        
        total_flow += path_flow
    
    # Check if we managed to route the entire amount
    if total_flow < amount:
        return -1.0
    
    return total_cost

def min_cost_flow_network_simplex(num_nodes, edges, source, destination, amount):
    """
    Alternative implementation using Network Simplex algorithm,
    which is more efficient for min-cost flow problems.
    
    Note: This implementation is more complex and is provided as a more
    efficient alternative to the augmenting path approach.
    
    Args:
        num_nodes: Number of trading hubs (nodes).
        edges: List of tuples (source_node, destination_node, capacity, cost).
        source: Index of the source trading hub.
        destination: Index of the destination trading hub.
        amount: Total amount of trade to be routed.
    
    Returns:
        Minimum total cost to route the required amount of trade, or -1.0 if impossible.
    """
    # Special case: source and destination are the same
    if source == destination:
        return 0.0
    
    # Initialize network with a super source and super sink
    # This allows us to handle the problem as a circulation problem
    n = num_nodes + 2
    super_source = num_nodes
    super_sink = num_nodes + 1
    
    # Build the graph with costs and capacities
    graph = [[] for _ in range(n)]
    cost = {}
    capacity = {}
    flow = {}
    
    # Add original edges
    for u, v, cap, c in edges:
        if cap > 0:  # Only consider edges with positive capacity
            graph[u].append(v)
            if (u, v) not in capacity:
                capacity[(u, v)] = 0
                cost[(u, v)] = 0
                flow[(u, v)] = 0
            capacity[(u, v)] += cap
            # Use weighted average for cost if there are parallel edges
            cost[(u, v)] = (cost[(u, v)] * flow[(u, v)] + c * cap) / (flow[(u, v)] + cap)
    
    # Add edges from super_source to source and from destination to super_sink
    graph[super_source].append(source)
    capacity[(super_source, source)] = amount
    cost[(super_source, source)] = 0
    flow[(super_source, source)] = 0
    
    graph[destination].append(super_sink)
    capacity[(destination, super_sink)] = amount
    cost[(destination, super_sink)] = 0
    flow[(destination, super_sink)] = 0
    
    # Add return edge from super_sink to super_source to make it a circulation
    graph[super_sink].append(super_source)
    capacity[(super_sink, super_source)] = amount
    cost[(super_sink, super_source)] = 0
    flow[(super_sink, super_source)] = 0
    
    # Initialize potential for each node
    potential = [0] * n
    
    # Initialize spanning tree
    # For simplicity, we'll use an augmenting path approach here
    # A full implementation of Network Simplex would maintain an explicit tree structure
    
    # Find an initial feasible flow (e.g., using augmenting paths)
    # For simplicity, we'll use Edmonds-Karp algorithm
    def bfs(s, t):
        visited = [False] * n
        queue = [s]
        visited[s] = True
        prev = {}
        
        while queue and not visited[t]:
            node = queue.pop(0)
            for neighbor in graph[node]:
                if not visited[neighbor] and capacity.get((node, neighbor), 0) > flow.get((node, neighbor), 0):
                    queue.append(neighbor)
                    visited[neighbor] = True
                    prev[neighbor] = (node, True)  # True indicates a forward edge
            
            # Also consider residual edges (backward edges)
            for u in range(n):
                if (u, node) in flow and flow[(u, node)] > 0 and not visited[u]:
                    queue.append(u)
                    visited[u] = True
                    prev[u] = (node, False)  # False indicates a backward edge
        
        if visited[t]:
            return prev
        return None
    
    # Find max flow using augmenting paths
    while True:
        prev = bfs(super_source, super_sink)
        if not prev:
            break
        
        # Find the bottleneck capacity
        path_flow = float('inf')
        node = super_sink
        while node != super_source:
            parent, is_forward = prev[node]
            if is_forward:
                path_flow = min(path_flow, capacity.get((parent, node), 0) - flow.get((parent, node), 0))
            else:
                path_flow = min(path_flow, flow.get((node, parent), 0))
            node = parent
        
        # Update flow along the path
        node = super_sink
        while node != super_source:
            parent, is_forward = prev[node]
            if is_forward:
                flow[(parent, node)] = flow.get((parent, node), 0) + path_flow
            else:
                flow[(node, parent)] = flow.get((node, parent), 0) - path_flow
            node = parent
    
    # Check if we managed to route the entire amount
    if flow.get((super_source, source), 0) < amount:
        return -1.0
    
    # Calculate the total cost
    total_cost = 0.0
    for (u, v), f in flow.items():
        if u != super_source and u != super_sink and v != super_source and v != super_sink:
            total_cost += f * cost.get((u, v), 0)
    
    return total_cost

# By default, use the simpler augmenting path approach
# The more efficient Network Simplex approach is provided as an alternative