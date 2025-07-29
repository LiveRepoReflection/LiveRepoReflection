from collections import deque

def build_graph(N, edges):
    graph = {i: [] for i in range(N)}
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    return graph

def multi_source_bfs(mirrors, graph, N):
    distances = [N] * N
    q = deque()
    for m in mirrors:
        distances[m] = 0
        q.append(m)
    while q:
        current = q.popleft()
        for neighbor in graph[current]:
            if distances[neighbor] > distances[current] + 1:
                distances[neighbor] = distances[current] + 1
                q.append(neighbor)
    return distances

def compute_total_cost(distances, importance_scores):
    return sum(importance_scores[i] * distances[i] for i in range(len(importance_scores)))

def find_optimal_mirrors(N, edges, importance_scores, K):
    graph = build_graph(N, edges)
    
    # Greedy initialization: Start with an empty set and add one mirror at a time.
    candidates = []
    for _ in range(K):
        best_candidate = None
        best_cost = float('inf')
        for node in range(N):
            if node in candidates:
                continue
            temp_candidates = candidates + [node]
            distances = multi_source_bfs(temp_candidates, graph, N)
            cost = compute_total_cost(distances, importance_scores)
            if cost < best_cost:
                best_cost = cost
                best_candidate = node
        candidates.append(best_candidate)
    
    # Iterative improvement: Try swapping one mirror with a non-mirror to reduce cost.
    current_distances = multi_source_bfs(candidates, graph, N)
    current_cost = compute_total_cost(current_distances, importance_scores)
    improved = True
    while improved:
        improved = False
        # Try every mirror in the current set and every candidate not in the set
        for i in range(len(candidates)):
            mirror_to_replace = candidates[i]
            for node in range(N):
                if node in candidates:
                    continue
                new_candidates = candidates.copy()
                new_candidates[i] = node
                new_distances = multi_source_bfs(new_candidates, graph, N)
                new_cost = compute_total_cost(new_distances, importance_scores)
                if new_cost < current_cost:
                    candidates = new_candidates
                    current_cost = new_cost
                    improved = True
                    break
            if improved:
                break

    return candidates