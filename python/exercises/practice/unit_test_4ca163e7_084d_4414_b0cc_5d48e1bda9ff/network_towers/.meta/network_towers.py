def min_network_cost(N, M, edges, population, demand, tower_cost, capacity):
    # Build graph adjacency list
    adj = {i: set() for i in range(N)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    
    # Precompute coverage mask and total load for each node if tower is deployed
    # Coverage mask: includes itself and all its adjacent nodes
    # Load: sum of demands for itself and all its adjacent nodes
    coverage = [0] * N
    load = [0] * N
    for i in range(N):
        cover = 1 << i
        total_demand = demand[i]
        for neigh in adj[i]:
            cover |= 1 << neigh
            total_demand += demand[neigh]
        coverage[i] = cover
        load[i] = total_demand

    # A tower can only be deployed if its load does not exceed capacity.
    # Build candidate list of nodes where a tower can be deployed.
    candidates = []
    for i in range(N):
        if load[i] <= capacity:
            candidates.append(i)

    # The overall goal is to cover all nodes. Represent full coverage as bitmask.
    full_coverage = (1 << N) - 1
    best_cost = float('inf')

    # Enumerate all subsets of candidate towers. Since N <= 20 the worst-case number of subsets is 2^20.
    cand_count = len(candidates)
    for mask in range(1 << cand_count):
        current_coverage = 0
        total_cost = 0
        for j in range(cand_count):
            if mask & (1 << j):
                node = candidates[j]
                current_coverage |= coverage[node]
                total_cost += tower_cost[node]
        # Check if the set of towers covers all nodes.
        if current_coverage == full_coverage:
            if total_cost < best_cost:
                best_cost = total_cost

    if best_cost == float('inf'):
        return -1
    return best_cost

if __name__ == "__main__":
    # Example usage:
    N = 4
    M = 4
    edges = [(0, 1), (0, 2), (1, 2), (2, 3)]
    population = [100, 150, 200, 120]
    demand = [20, 30, 40, 25]
    tower_cost = [100, 150, 200, 120]
    capacity = 70
    result = min_network_cost(N, M, edges, population, demand, tower_cost, capacity)
    print(result)