def min_total_cost(n, edges, data_centers, k, cable_cost, latency_penalty):
    # Compute initial distance matrix using Floyd Warshall
    INF = float('inf')
    dist = [[INF] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        if w < dist[u][v]:
            dist[u][v] = w
            dist[v][u] = w
    # Standard Floyd Warshall to compute all-pairs shortest paths for the original graph
    for mid in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][mid] + dist[mid][j] < dist[i][j]:
                    dist[i][j] = dist[i][mid] + dist[mid][j]

    # Helper to compute total cost from a given distance matrix and number of cables deployed
    def compute_total_cost(distance_matrix, cables_deployed):
        # Compute sum for all pairs of data centers.
        # data_centers is a list where data_centers[i] is the list of centers in city i.
        dc_cost = 0
        # For each pair of cities (i, j), if there are x centers in i and y centers in j,
        # then that contributes distance_matrix[i][j] * (x*y)
        for i in range(n):
            for j in range(i + 1, n):
                cnt_i = len(data_centers[i])
                cnt_j = len(data_centers[j])
                dc_cost += distance_matrix[i][j] * cnt_i * cnt_j
        # Compute total network latency: sum of distances for every pair (i, j) of cities
        network_latency = 0
        for i in range(n):
            for j in range(i + 1, n):
                network_latency += distance_matrix[i][j]
        total = dc_cost + (cables_deployed * cable_cost) + (latency_penalty * network_latency)
        return total

    # Function to simulate adding a cable between city u and v and update distances accordingly.
    # Returns a new distance matrix after relaxing distances using the new cable.
    def relax_with_cable(curr_matrix, u, v):
        # Create a copy of the current distances
        new_mat = [row[:] for row in curr_matrix]
        # The cable gives direct edge weight 1 between u and v (bidirectional)
        if 1 < new_mat[u][v]:
            new_mat[u][v] = 1
            new_mat[v][u] = 1
        # Use the new cable edge to relax all pairs distances
        for i in range(n):
            for j in range(n):
                # Two possible new routes: i->u then cable u->v then v->j; or i->v then cable v->u then u->j.
                via_uv = curr_matrix[i][u] + 1 + curr_matrix[v][j]
                via_vu = curr_matrix[i][v] + 1 + curr_matrix[u][j]
                if via_uv < new_mat[i][j]:
                    new_mat[i][j] = via_uv
                if via_vu < new_mat[i][j]:
                    new_mat[i][j] = via_vu
        # It suffices to do one relaxation pass because curr_matrix was already optimal
        return new_mat

    # Begin greedy cable deployment: try adding cables one by one if they reduce total cost.
    current_matrix = [row[:] for row in dist]
    current_cost = compute_total_cost(current_matrix, 0)
    cables_used = 0
    # Keep track of deployed cables to avoid duplication.
    deployed = set()

    # List candidate city pairs (u, v) with u < v that could potentially be improved (current shortest path > 1)
    candidates = []
    for u in range(n):
        for v in range(u + 1, n):
            if current_matrix[u][v] > 1:
                candidates.append((u, v))

    # Greedy selection: up to k cables can be deployed.
    while cables_used < k:
        best_improvement = 0
        best_candidate = None
        best_new_matrix = None

        for (u, v) in candidates:
            if (u, v) in deployed:
                continue
            # Simulate adding cable between u and v
            new_matrix = relax_with_cable(current_matrix, u, v)
            new_cost = compute_total_cost(new_matrix, cables_used + 1)
            improvement = current_cost - new_cost
            if improvement > best_improvement:
                best_improvement = improvement
                best_candidate = (u, v)
                best_new_matrix = new_matrix

        if best_candidate is not None and best_improvement > 0:
            # Deploy the best cable.
            deployed.add(best_candidate)
            cables_used += 1
            current_matrix = best_new_matrix
            current_cost = compute_total_cost(current_matrix, cables_used)
        else:
            break

    return int(current_cost)