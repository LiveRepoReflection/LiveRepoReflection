from collections import defaultdict, deque

def optimal_toll_placement(N, edges, B, C, R, D):
    """
    Determine optimal toll booth placements on highway segments.
    
    Each edge is represented as (u, v, L, T):
      - u, v: endpoints (cities)
      - L: length of the highway segment
      - T: estimated daily traffic volume
    
    Building a toll booth on an edge costs (C * L) and generates revenue (R * L * T).
    The goal is to maximize total revenue subject to:
      1. Budget: total cost <= B.
      2. Connectivity: Removing selected toll booth edges must leave the graph connected.
      3. Distance constraint: For D > 0, no vertex can be incident to more than one toll booth.
         (This is a simplified enforcement of a minimum distance requirement.)
    
    This function attempts a greedy selection based on revenue potential.
    """
    # Helper function: Build graph as adjacency list, omitting edges in toll_edges.
    def build_graph(N, edges, toll_edges):
        graph = defaultdict(list)
        for (u, v, L, T) in edges:
            key = (min(u, v), max(u, v))
            if key in toll_edges:
                continue
            graph[u].append((v, L))
            graph[v].append((u, L))
        return graph

    # Helper function: Check if graph is connected using BFS.
    def is_connected(N, graph):
        if N == 0:
            return True
        visited = [False] * N
        q = deque([0])
        visited[0] = True
        count = 1
        while q:
            node = q.popleft()
            for neighbor, _ in graph[node]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    q.append(neighbor)
                    count += 1
        return count == N

    # Pre-calculate candidate data: revenue and cost for each edge.
    # Candidate format: (u, v, L, T, cost, revenue)
    candidates = []
    for (u, v, L, T) in edges:
        cost = C * L
        revenue = R * L * T
        candidates.append((u, v, L, T, cost, revenue))
    
    # Sort candidates in descending order of revenue.
    # In case of tie, prefer lower cost.
    candidates.sort(key=lambda x: (x[5], -x[4]), reverse=True)
    
    selected = []
    budget_remaining = B
    used_vertices = set()  # for enforcing distance constraint when D > 0
    toll_edges_set = set()  # store selected toll booth edges as (min(u,v), max(u,v))
    
    # Greedy selection
    for candidate in candidates:
        u, v, L, T, cost, revenue = candidate
        if cost > budget_remaining:
            continue
        # Enforce distance constraint: for D > 0, no vertex can have more than one toll booth incident.
        if D > 0:
            if u in used_vertices or v in used_vertices:
                continue
        
        # Tentatively add candidate edge.
        key = (min(u, v), max(u, v))
        new_toll_edges = toll_edges_set.copy()
        new_toll_edges.add(key)
        # Build graph with these edges removed
        graph = build_graph(N, edges, new_toll_edges)
        if not is_connected(N, graph):
            continue
        
        # Accept candidate edge
        selected.append((u, v))
        toll_edges_set.add(key)
        budget_remaining -= cost
        if D > 0:
            used_vertices.add(u)
            used_vertices.add(v)
    
    return selected