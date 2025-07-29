import heapq
from collections import defaultdict

def cdn_placement(cities, connections, demand, cdn_capacity, cdn_cost, latency_tolerance, candidate_sites):
    # Build the graph
    graph = defaultdict(list)
    for u, v, w in connections:
        graph[u].append((v, w))
        graph[v].append((u, w))
    
    # Precompute shortest distances from each candidate site using Dijkstra's algorithm
    # and store the set of cities that are within the latency_tolerance.
    candidate_coverage = {}
    for cand in candidate_sites:
        distances = [float('inf')] * cities
        distances[cand] = 0
        heap = [(0, cand)]
        while heap:
            cur_dist, u = heapq.heappop(heap)
            if cur_dist > distances[u]:
                continue
            for v, w in graph[u]:
                new_dist = cur_dist + w
                if new_dist < distances[v]:
                    distances[v] = new_dist
                    heapq.heappush(heap, (new_dist, v))
        # Build coverage set for candidate site: all cities within latency_tolerance 
        coverage = set(u for u in range(cities) if distances[u] <= latency_tolerance)
        candidate_coverage[cand] = coverage

    # Precompute total demand and the minimal number of servers required by capacity.
    total_demand = sum(demand)
    min_servers_by_capacity = (total_demand + cdn_capacity - 1) // cdn_capacity  # ceiling division

    cand_list = candidate_sites
    n = len(cand_list)
    
    if n == 0:
        return -1

    all_cities = set(range(cities))
    best_cost = float('inf')
    # Since candidate_sites might be small, try all subsets
    # Using bit mask iteration.
    # There are 2^n subsets. For each subset, check capacity and coverage viability.
    for mask in range(1, 1 << n):
        # Count servers in the subset
        count = 0
        union_coverage = set()
        for i in range(n):
            if mask & (1 << i):
                count += 1
                cand = cand_list[i]
                union_coverage |= candidate_coverage[cand]
                # Early break, if union_coverage already covers all cities and we have enough capacity,
                # we can break out if further selection would only add cost.
                # (Not necessary but a minor optimization)
        # Check if capacity is met.
        if count * cdn_capacity < total_demand:
            continue
        # Check if coverage is complete.
        if union_coverage != all_cities:
            continue
        current_cost = count * cdn_cost
        if current_cost < best_cost:
            best_cost = current_cost

    # If best_cost still infinity, no valid configuration is found.
    return best_cost if best_cost != float('inf') else -1