import math

def compute_network_cost(N, planet_coordinates, tech_matrix, critical_planets, K):
    # Compute cost between two planets: Euclidean distance * tech_matrix multiplier.
    def edge_cost(i, j):
        (x1, y1, z1) = planet_coordinates[i]
        (x2, y2, z2) = planet_coordinates[j]
        dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)
        return dist * tech_matrix[i][j]

    # Step 1: Build MST using Prim's algorithm.
    in_mst = [False] * N
    min_cost = [float('inf')] * N
    parent = [-1] * N
    min_cost[0] = 0.0
    mst_cost = 0.0

    # To record MST edges and build degree count.
    mst_edges = set()
    degree = [0] * N

    for _ in range(N):
        # Find the next vertex u not in MST with minimal min_cost[u]
        u = -1
        best = float('inf')
        for v in range(N):
            if not in_mst[v] and min_cost[v] < best:
                best = min_cost[v]
                u = v
        if u == -1:
            break
        in_mst[u] = True
        mst_cost += best
        # If u has a parent, record the edge
        if parent[u] != -1:
            a, b = min(u, parent[u]), max(u, parent[u])
            mst_edges.add((a, b))
            degree[u] += 1
            degree[parent[u]] += 1
        # Update min_cost for vertices not in MST
        for v in range(N):
            if not in_mst[v]:
                cost_uv = edge_cost(u, v)
                if cost_uv < min_cost[v]:
                    min_cost[v] = cost_uv
                    parent[v] = u

    # Step 2: Determine deficits for critical planets.
    deficits = {}
    for v in critical_planets:
        curr_deg = degree[v]
        if curr_deg < K:
            deficits[v] = K - curr_deg

    additional_cost = 0.0
    # If no deficits needed, return mst_cost.
    if not deficits:
        return round(mst_cost, 6)

    # Step 3: Build candidate list for additional edges that are not already in MST.
    candidates = []
    for i in range(N):
        for j in range(i+1, N):
            if (i, j) not in mst_edges:
                cost_ij = edge_cost(i, j)
                candidates.append((cost_ij, i, j))
    candidates.sort(key=lambda x: x[0])

    # Step 4: Greedy selection from candidate edges to cover deficits.
    for cost, i, j in candidates:
        updated = False
        # Check if adding edge (i,j) would help reduce deficit.
        if i in deficits and deficits[i] > 0:
            updated = True
        if j in deficits and deficits[j] > 0:
            updated = True
        if updated:
            # Add edge and update deficits if endpoints are critical.
            if i in deficits and deficits[i] > 0:
                deficits[i] -= 1
                if deficits[i] == 0:
                    del deficits[i]
            if j in deficits and deficits.get(j, 0) > 0:
                deficits[j] -= 1
                if deficits[j] == 0:
                    deficits.pop(j, None)
            additional_cost += cost
        if not deficits:
            break

    total_cost = mst_cost + additional_cost
    return round(total_cost, 6)