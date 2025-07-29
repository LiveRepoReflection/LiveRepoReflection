import itertools

def optimal_patrol_placement(n, k, edges):
    # Calculate total accident cost for all edges
    total_accidents = sum(l * r for _, _, l, r in edges)
    
    # If no patrol units, return total accident cost
    if k == 0:
        return total_accidents
    # If patrol units cover all cities, no accidents remain unpatrolled
    if k >= n:
        return 0

    # Precompute edge weights and incident cities mapping
    # Each edge represented as (u, v, weight)
    weighted_edges = [(u, v, l * r) for u, v, l, r in edges]

    # For small n, use brute-force to search for optimal placement
    if n <= 20:
        best_covered = 0
        cities = range(n)
        for combo in itertools.combinations(cities, k):
            selected = set(combo)
            covered = 0
            # Sum edge weight if at least one endpoint is selected
            for u, v, weight in weighted_edges:
                if u in selected or v in selected:
                    covered += weight
            if covered > best_covered:
                best_covered = covered
                # Early exit if fully covered all edges
                if best_covered == total_accidents:
                    break
        return total_accidents - best_covered

    # For larger graphs, use a greedy heuristic (approximation).
    # Initialize selected set as empty.
    selected = set()
    current_covered = 0
    # Pre-calculate for each city, the total weight it can cover if chosen.
    incident_weights = [0] * n
    for u, v, weight in weighted_edges:
        incident_weights[u] += weight
        incident_weights[v] += weight

    # Greedy selection of vertices based on marginal gains.
    remaining = set(range(n))
    # To avoid double counting, track for each edge whether it is covered.
    edge_covered = [False] * len(weighted_edges)

    # Precompute for each city the list of edge indices it is incident to.
    city_to_edges = {i: [] for i in range(n)}
    for idx, (u, v, weight) in enumerate(weighted_edges):
        city_to_edges[u].append(idx)
        city_to_edges[v].append(idx)

    for _ in range(k):
        best_gain = -1
        best_city = None
        for city in remaining:
            marginal_gain = 0
            for edge_idx in city_to_edges[city]:
                if not edge_covered[edge_idx]:
                    marginal_gain += weighted_edges[edge_idx][2]
            if marginal_gain > best_gain:
                best_gain = marginal_gain
                best_city = city
        if best_city is None:
            break
        selected.add(best_city)
        remaining.remove(best_city)
        for edge_idx in city_to_edges[best_city]:
            edge_covered[edge_idx] = True
        current_covered = sum(weight for covered, (_, _, weight) in zip(edge_covered, weighted_edges) if covered)
        # If full coverage achieved, can break early.
        if current_covered == total_accidents:
            break

    return total_accidents - current_covered