import heapq
import copy

def find_paths(graph, source, destination, k, T):
    # Filter graph based on congestion threshold T.
    filtered_graph = {}
    for u, edges in graph.items():
        filtered_edges = {v: w for v, w in edges.items() if w <= T}
        filtered_graph[u] = filtered_edges

    # Special case: source == destination
    if source == destination:
        return [[source]]
        
    # Helper function: Dijkstra's algorithm modified to allow banning nodes/edges.
    def dijkstra(start, end, graph, banned_nodes, banned_edges):
        # Each entry is (cost, current_node, path)
        heap = [(0, start, [start])]
        visited = {}
        while heap:
            cost, node, path = heapq.heappop(heap)
            if node == end:
                return (path, cost)
            if node in visited and visited[node] <= cost:
                continue
            visited[node] = cost
            for neighbour, w in graph.get(node, {}).items():
                if neighbour in banned_nodes:
                    continue
                if (node, neighbour) in banned_edges:
                    continue
                if neighbour in path:
                    continue  # avoid cycles
                heapq.heappush(heap, (cost + w, neighbour, path + [neighbour]))
        return (None, None)

    # Helper: compute total cost of a given path using filtered_graph.
    def compute_cost(path, graph):
        total = 0
        for i in range(len(path) - 1):
            total += graph[path[i]][path[i+1]]
        return total

    # Yen's algorithm implementation
    A = []
    B = []

    # Get the first shortest path.
    first_path, first_cost = dijkstra(source, destination, filtered_graph, set(), set())
    if first_path is None:
        return []
    A.append((first_path, first_cost))

    # Set a limit for candidate generation: try to get up to max_candidates.
    max_candidates = k * 10

    candidates = []

    # Generate candidates until we have enough or no further candidate exists.
    for kth in range(1, max_candidates):
        for i in range(len(A[-1][0]) - 1):
            spur_node = A[-1][0][i]
            root_path = A[-1][0][:i+1]
            banned_edges = set()
            # Remove edges that were previously used in paths with the same root
            for path, cost in A:
                if len(path) > i and path[:i+1] == root_path:
                    banned_edges.add((path[i], path[i+1]))
            banned_nodes = set(root_path[:-1])
            spur_path, spur_cost = dijkstra(spur_node, destination, filtered_graph, banned_nodes, banned_edges)
            if spur_path is not None:
                candidate_path = root_path[:-1] + spur_path
                candidate_cost = compute_cost(candidate_path, filtered_graph)
                # Avoid duplicates in candidates and in A.
                if not any(candidate_path == p for p, c in A) and not any(candidate_path == p for c, p in candidates):
                    heapq.heappush(B, (candidate_cost, candidate_path))
        if not B:
            break
        # Get the candidate with smallest cost
        cost_candidate, path_candidate = heapq.heappop(B)
        A.append((path_candidate, cost_candidate))
        if len(A) >= k:
            break

    # Collect candidate paths from Yen's algorithm results.
    candidate_paths = A if len(A) <= k else A[:k]

    # If diversity selection is needed, we perform a greedy re-selection among the candidate paths.
    # We assume candidate_paths is a list of (path, cost). 
    # Define a function to compute edge set for a path.
    def path_edges(path):
        return set((path[i], path[i+1]) for i in range(len(path)-1))
    # Precompute edges for all candidate paths.
    candidate_info = []
    for path, cost in candidate_paths:
        candidate_info.append({
            'path': path,
            'cost': cost,
            'edges': path_edges(path)
        })
    # Sort candidates by cost ascending initially.
    candidate_info.sort(key=lambda x: x['cost'])
    
    selected = []
    # Greedy selection: first select the candidate with minimum cost.
    if candidate_info:
        selected.append(candidate_info[0])
    # For diversity, iteratively select candidate with minimal added similarity penalty.
    while len(selected) < min(k, len(candidate_info)):
        best_candidate = None
        best_score = None
        for candidate in candidate_info:
            if candidate in selected:
                continue
            similarity = 0
            for sel in selected:
                similarity += len(candidate['edges'] & sel['edges'])
            # Use tuple (similarity, cost) as score: lower similarity first, then lower cost.
            score = (similarity, candidate['cost'])
            if best_score is None or score < best_score:
                best_score = score
                best_candidate = candidate
        if best_candidate:
            selected.append(best_candidate)
        else:
            break

    # Final selected paths: sort by total cost finally.
    selected.sort(key=lambda x: x['cost'])
    result = [item['path'] for item in selected]
    return result