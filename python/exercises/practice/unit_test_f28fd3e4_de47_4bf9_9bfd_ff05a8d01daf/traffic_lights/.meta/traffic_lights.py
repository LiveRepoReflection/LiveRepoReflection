import math
from itertools import combinations

def compute_average_travel_time(n, roads, lights, delay_function):
    # Initialize matrix for shortest travel times
    dist = [[math.inf for _ in range(n)] for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0.0

    for (u, v, length, speed_limit) in roads:
        base_time = length / speed_limit
        extra_delay = delay_function(length, speed_limit) if v in lights else 0.0
        travel_time = base_time + extra_delay
        if travel_time < dist[u][v]:
            dist[u][v] = travel_time

    # Floyd-Warshall algorithm to compute all-pairs shortest paths
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    total = 0.0
    count = 0
    for i in range(n):
        for j in range(n):
            if i != j and dist[i][j] < math.inf:
                total += dist[i][j]
                count += 1

    return total / count if count > 0 else math.inf

def brute_force_optimal(n, roads, budget, delay_function):
    best_avg = math.inf
    best_subset = []
    # Only consider up to n intersections if budget is larger than n
    max_lights = min(budget, n)
    for r in range(0, max_lights + 1):
        for subset in combinations(range(n), r):
            avg_time = compute_average_travel_time(n, roads, set(subset), delay_function)
            if avg_time < best_avg:
                best_avg = avg_time
                best_subset = list(subset)
    return best_subset

def greedy_optimal(n, roads, budget, delay_function):
    lights = set()
    current_avg = compute_average_travel_time(n, roads, lights, delay_function)
    available = set(range(n))
    improved = True

    while improved and len(lights) < budget:
        improved = False
        best_candidate = None
        best_candidate_avg = current_avg
        for candidate in available - lights:
            new_lights = lights.union({candidate})
            avg_time = compute_average_travel_time(n, roads, new_lights, delay_function)
            if avg_time < best_candidate_avg:
                best_candidate_avg = avg_time
                best_candidate = candidate
        if best_candidate is not None:
            lights.add(best_candidate)
            current_avg = best_candidate_avg
            improved = True

    return list(lights)

def traffic_lights(n, roads, budget, light_cost, delay_function):
    """
    Determine the optimal set of intersections at which to install traffic lights.
    The objective is to minimize the average travel time between all reachable intersection pairs.
    If multiple sets yield the same average travel time, any one is acceptable.
    """
    # For small graphs, we use brute force to guarantee optimality.
    if n <= 10:
        return brute_force_optimal(n, roads, budget, delay_function)
    else:
        # For larger graphs, due to combinatorial explosion, we use a greedy heuristic.
        return greedy_optimal(n, roads, budget, delay_function)