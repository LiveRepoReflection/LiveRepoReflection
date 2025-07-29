import heapq

def dijkstra(n, graph, s, t, weight_func):
    # distances and predecessors initialization
    dist = [float('inf')] * n
    prev = [None] * n
    dist[s] = 0
    # priority queue: (distance, node)
    heap = [(0, s)]
    
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        if u == t:
            break
        for edge in graph.get(u, []):
            v, a, b = edge
            w = weight_func(u, v, a, b)
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                heapq.heappush(heap, (dist[v], v))
                
    # reconstruct path as list of edges (u,v)
    if dist[t] == float('inf'):
        return float('inf'), []
    path = []
    cur = t
    while cur != s:
        p = prev[cur]
        path.append((p, cur))
        cur = p
    path.reverse()
    return dist[t], path

def find_equilibrium(n, edges, s, t, num_users):
    # Build graph: for each node, list of outgoing edge tuples (v, a, b)
    graph = {}
    cost_params = {}
    for u, v, a, b in edges:
        if u not in graph:
            graph[u] = []
        graph[u].append((v, a, b))
        cost_params[(u, v)] = (a, b)
    
    # Initialize flows: all edges have flow 0
    flows = { (u, v): 0 for u, v, a, b in edges }
    
    # Dijkstra using fixed cost b for initialization
    def weight_init(u, v, a, b):
        return b
    # find initial path (same for all users)
    _, init_path = dijkstra(n, graph, s, t, weight_init)
    if not init_path:
        return flows  # no path, though input guarantees a path exists
    
    # Initialize each user's assignment and update flows accordingly.
    user_paths = [init_path[:] for _ in range(num_users)]
    for edge in init_path:
        flows[edge] += num_users

    improved = True
    while improved:
        improved = False
        for i in range(num_users):            
            current_path = user_paths[i]
            # Pre-calculate current cost for user i on their current path.
            current_cost = 0
            for edge in current_path:
                a, b = cost_params[edge]
                # The user is already using this edge so they don't add extra unit.
                current_cost += a * flows[edge] + b

            # Prepare a set for quick membership testing of current path edges.
            current_set = set(current_path)
            
            # Define modified weight function for candidate path:
            def weight_modified(u, v, a, b):
                # if edge is part of current path, cost remains a * flows[edge] + b.
                # if not in current, using it adds one unit.
                if (u, v) in current_set:
                    return a * flows[(u, v)] + b
                else:
                    return a * (flows[(u, v)] + 1) + b

            candidate_cost, candidate_path = dijkstra(n, graph, s, t, weight_modified)
            # If candidate path is empty, skip update.
            if not candidate_path:
                continue

            if candidate_cost < current_cost:
                # Update flows: remove user from old path.
                for edge in current_path:
                    flows[edge] -= 1
                # Update flows: add user to candidate path.
                for edge in candidate_path:
                    flows[edge] += 1
                # Update user's assignment.
                user_paths[i] = candidate_path
                improved = True

    return flows