from collections import deque

def optimize_router_placement(N, edges, R, C, K, critical_buildings):
    # Build graph as an adjacency list
    graph = {i: set() for i in range(N)}
    for u, v in edges:
        graph[u].add(v)
        graph[v].add(u)

    # Function to compute coverage of routers set T using multi-source BFS
    def compute_coverage(T):
        covered = set()
        queue = deque()
        # Initialize queue with all routers in T at distance 0
        for src in T:
            covered.add(src)
            queue.append((src, 0))
        while queue:
            node, dist = queue.popleft()
            if dist < R:
                for nei in graph[node]:
                    if nei not in covered:
                        covered.add(nei)
                        queue.append((nei, dist + 1))
        return covered

    # Start with critical buildings as mandatory router placements.
    placements = set(critical_buildings)
    covered_nodes = compute_coverage(placements)
    
    # Greedy addition: while some nodes are not covered, choose a new router position that maximizes additional coverage.
    while len(covered_nodes) < N:
        best_candidate = None
        best_gain = -1
        for candidate in range(N):
            if candidate in placements:
                continue
            # Compute additional nodes covered if we add candidate
            new_coverage = compute_coverage(placements.union({candidate}))
            gain = len(new_coverage) - len(covered_nodes)
            if gain > best_gain or (gain == best_gain and (best_candidate is None or candidate < best_candidate)):
                best_gain = gain
                best_candidate = candidate
        # Add best candidate
        if best_candidate is None:
            break
        placements.add(best_candidate)
        covered_nodes = compute_coverage(placements)
    
    # Convert placements to sorted list for consistency in output.
    placements = sorted(list(placements))
    min_routers = len(placements)
    
    # Calculate served users by selecting up to C routers among placements as high-capacity routers.
    # Each high-capacity router serves min(K, degree+1) users, where (degree+1) is the router itself and its neighbors.
    served_list = []
    for node in placements:
        served = min(K, len(graph[node]) + 1)
        served_list.append(served)
    # Sort in descending order to choose routers with greater serving capacity.
    served_list.sort(reverse=True)
    max_served_users = sum(served_list[:C])
    
    return (min_routers, placements, max_served_users)