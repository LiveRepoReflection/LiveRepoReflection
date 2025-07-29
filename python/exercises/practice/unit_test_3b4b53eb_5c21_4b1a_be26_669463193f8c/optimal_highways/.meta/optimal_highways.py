from collections import deque
import math

def find_optimal_highway_network(N, B, D, city_costs, strategic_hubs):
    m = len(city_costs)
    best = math.inf

    # Pre-calculate all subsets of edges (using bitmasks)
    # For each subset, check if it forms a valid network.
    for mask in range(1, 1 << m):
        total_cost = 0
        # Build graph and count degrees
        graph = {i: [] for i in range(1, N+1)}
        degree = {i: 0 for i in range(1, N+1)}
        valid_subset = True
        
        for j in range(m):
            if mask & (1 << j):
                u, v, cost = city_costs[j]
                total_cost += cost
                # Early break if cost exceeds budget
                if total_cost > B:
                    valid_subset = False
                    break
                graph[u].append(v)
                graph[v].append(u)
                degree[u] += 1
                degree[v] += 1

        if not valid_subset:
            continue

        # Check connectivity using BFS (start from vertex 1)
        visited = set()
        queue = deque([1])
        visited.add(1)
        while queue:
            node = queue.popleft()
            for nei in graph[node]:
                if nei not in visited:
                    visited.add(nei)
                    queue.append(nei)
        if len(visited) != N:
            continue

        # Compute current maximum degree in this subgraph.
        current_max_degree = max(degree.values()) if degree else 0
        
        # Check if the current network satisfies strategic hubs distance constraint.
        if not check_strategic_hubs(graph, strategic_hubs, D):
            continue
        
        # If valid, update best answer.
        best = min(best, current_max_degree)

    return best if best != math.inf else -1

def check_strategic_hubs(graph, strategic_hubs, D):
    # For each strategic hub, perform BFS and ensure that every other hub is within D hops.
    for hub in strategic_hubs:
        if not bfs_within_distance(graph, hub, strategic_hubs, D):
            return False
    return True

def bfs_within_distance(graph, start, strategic_hubs, max_distance):
    # BFS starting from 'start', check distances to strategic hubs.
    distances = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for nei in graph[node]:
            if nei not in distances:
                distances[nei] = distances[node] + 1
                queue.append(nei)
    # All strategic hubs including start must be within max_distance.
    for hub in strategic_hubs:
        # If a hub is not reachable (shouldn't happen because graph is connected) or distance > max_distance.
        if hub not in distances or distances[hub] > max_distance:
            return False
    return True