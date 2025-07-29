import heapq
from collections import defaultdict

def optimal_path_cost(n, links, risk_factors, s, d, risk_weight):
    if s == d:
        return risk_factors[s] * risk_weight
    
    # Build adjacency list
    graph = defaultdict(list)
    for u, v, latency in links:
        graph[u].append((v, latency))
        graph[v].append((u, latency))  # bidirectional links
    
    # Priority queue: (current_cost, current_node, visited_risk)
    heap = []
    heapq.heappush(heap, (risk_factors[s] * risk_weight, s, {s}))
    
    # Dictionary to store minimal costs for nodes with their visited risks
    min_costs = defaultdict(lambda: float('inf'))
    min_costs[(s, frozenset({s}))] = risk_factors[s] * risk_weight
    
    while heap:
        current_cost, current_node, visited = heapq.heappop(heap)
        visited_frozen = frozenset(visited)
        
        if current_node == d:
            return current_cost
        
        if current_cost > min_costs.get((current_node, visited_frozen), float('inf')):
            continue
            
        for neighbor, latency in graph[current_node]:
            if neighbor in visited:
                continue
                
            new_visited = set(visited)
            new_visited.add(neighbor)
            new_visited_frozen = frozenset(new_visited)
            
            additional_risk = risk_factors[neighbor] * risk_weight
            new_cost = current_cost + latency + additional_risk
            
            if new_cost < min_costs.get((neighbor, new_visited_frozen), float('inf')):
                min_costs[(neighbor, new_visited_frozen)] = new_cost
                heapq.heappush(heap, (new_cost, neighbor, new_visited))
    
    return -1