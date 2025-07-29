import heapq
import math

def optimal_highway(graph, highways, budget, targets):
    source, target = targets
    # If source or target not in graph, no valid path exists.
    if source not in graph or target not in graph:
        return float('inf')
    
    # Build highway adjacency list (undirected)
    highway_adj = {}
    # Initialize highway_adj for nodes already in graph to ensure consistency.
    for node in graph:
        highway_adj[node] = []
    # Add highways; if a highway involves a node not in graph, add it.
    for u, v, cost, t in highways:
        if u not in highway_adj:
            highway_adj[u] = []
        if v not in highway_adj:
            highway_adj[v] = []
        highway_adj[u].append((v, cost, t))
        highway_adj[v].append((u, cost, t))
    
    # State: (total_time, current_node, total_highway_cost)
    # Use multi-criteria Dijkstra, with state dimension = current highway cost spent.
    # Maintain best_time[state] keyed by (node, cost_spent) to prune inferior routes.
    pq = []
    heapq.heappush(pq, (0, source, 0))
    best = {}
    best[(source, 0)] = 0

    while pq:
        cur_time, node, cost_spent = heapq.heappop(pq)
        # If we reached target, this is the optimal solution (Dijkstra property)
        if node == target:
            return cur_time
        
        # If this state has been processed with a better time, skip
        if best.get((node, cost_spent), math.inf) < cur_time:
            continue
        
        # Explore road edges from current node (existing roads - no cost penalty)
        for neighbor, travel_time in graph[node].items():
            new_time = cur_time + travel_time
            new_cost = cost_spent
            state = (neighbor, new_cost)
            if best.get(state, math.inf) > new_time:
                best[state] = new_time
                heapq.heappush(pq, (new_time, neighbor, new_cost))
        
        # Explore highway edges from current node (optional edges - cost penalty applies)
        if node in highway_adj:
            for neighbor, h_cost, h_time in highway_adj[node]:
                new_cost = cost_spent + h_cost
                if new_cost <= budget:
                    new_time = cur_time + h_time
                    state = (neighbor, new_cost)
                    if best.get(state, math.inf) > new_time:
                        best[state] = new_time
                        heapq.heappush(pq, (new_time, neighbor, new_cost))
    
    return float('inf')