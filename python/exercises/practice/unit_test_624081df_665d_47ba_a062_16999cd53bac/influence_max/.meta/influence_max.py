import heapq
from collections import defaultdict, deque

def select_seeds(n, edges, k, iterations, activation_threshold):
    if k == 0:
        return []
    if k >= n:
        return list(range(n))
    
    # Build graph
    graph = defaultdict(list)
    for u, v, p in edges:
        graph[u].append((v, p))
    
    # Precompute reverse graph for influence calculation
    reverse_graph = defaultdict(list)
    for u, v, p in edges:
        reverse_graph[v].append((u, p))
    
    # Calculate degree centrality as initial heuristic
    degree_centrality = [0] * n
    for u, v, p in edges:
        degree_centrality[u] += 1
    
    # Use a max heap based on degree centrality
    heap = [(-degree_centrality[i], i) for i in range(n)]
    heapq.heapify(heap)
    
    seeds = []
    for _ in range(k):
        if not heap:
            break
        _, node = heapq.heappop(heap)
        seeds.append(node)
    
    # Greedy algorithm with influence spread estimation
    best_seeds = seeds.copy()
    max_influence = estimate_influence(graph, seeds, iterations, activation_threshold, n)
    
    # Try improving the selection
    for _ in range(min(100, n)):  # Limit iterations for large networks
        candidate = seeds.copy()
        # Randomly swap one seed
        if len(candidate) > 1:
            idx = len(candidate) - 1
            candidate[idx] = (candidate[idx] + 1) % n
            while candidate[idx] in candidate[:idx]:
                candidate[idx] = (candidate[idx] + 1) % n
        
        current_influence = estimate_influence(graph, candidate, iterations, activation_threshold, n)
        if current_influence > max_influence:
            max_influence = current_influence
            best_seeds = candidate.copy()
    
    return best_seeds[:k]

def estimate_influence(graph, seeds, iterations, threshold, n):
    if not seeds:
        return 0
    
    active = set(seeds)
    new_active = set(active)
    
    for _ in range(iterations):
        next_active = set()
        for node in range(n):
            if node in active:
                continue
                
            total_influence = 0.0
            for neighbor, p in graph.get(node, []):
                if neighbor in active:
                    total_influence += p
            
            if total_influence >= threshold:
                next_active.add(node)
        
        if not next_active:
            break
        active.update(next_active)
    
    return len(active)