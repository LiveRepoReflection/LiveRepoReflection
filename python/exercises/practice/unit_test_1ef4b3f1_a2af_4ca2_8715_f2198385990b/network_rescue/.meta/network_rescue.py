from collections import defaultdict

def deploy_routers(num_locations, edges, router_range, router_power, budget):
    """
    Selects a subset of locations to place wireless routers such that every location is connected 
    (each connected component of the graph has at least one router), the total direct link cost from routers 
    to non-router nodes is within the given budget, and the total power consumption of routers is minimized.
    
    Parameters:
    - num_locations: int, number of nodes (locations)
    - edges: list of tuples (u, v, weight) representing undirected edges between locations
    - router_range: list of floats representing the transmission range (not used in current calculation)
    - router_power: list of floats representing the power consumption rate for placing a router at each node
    - budget: float, maximum allowed total direct link cost from routers to covered nodes
    
    Returns:
    - A list of integers representing the indices of locations where routers are placed.
      Returns an empty list if no solution satisfies the constraints.
    """
    # Precompute the connectivity components from the full graph.
    graph = build_graph(num_locations, edges)
    components = get_connected_components(num_locations, graph)
    
    # Precompute an adjacency dictionary that maps each node to its neighbors with the minimum edge cost.
    adj = build_adj(num_locations, edges)

    best_power = float('inf')
    best_subset = None
    # Iterate over all subsets of nodes (except the empty set).
    # Since num_locations <= 20, 2^num_locations is tractable.
    for mask in range(1, 1 << num_locations):
        candidate = set()
        candidate_power = 0
        for i in range(num_locations):
            if mask & (1 << i):
                candidate.add(i)
                candidate_power += router_power[i]
        # Connectivity: each connected component must have at least one router.
        valid = True
        for comp in components:
            if candidate.isdisjoint(comp):
                valid = False
                break
        if not valid:
            continue

        direct_cost = compute_direct_link_cost(num_locations, adj, candidate)
        if direct_cost <= budget:
            if candidate_power < best_power:
                best_power = candidate_power
                best_subset = candidate

    if best_subset is None:
        return []
    return sorted(list(best_subset))


def build_graph(num_locations, edges):
    """
    Builds an undirected graph represented as a dictionary from node to list of neighbors.
    """
    graph = defaultdict(list)
    for u, v, w in edges:
        graph[u].append(v)
        graph[v].append(u)
    # Ensure all nodes appear in the graph even if isolated.
    for i in range(num_locations):
        if i not in graph:
            graph[i] = []
    return graph


def get_connected_components(num_locations, graph):
    """
    Returns the connected components of the graph as a list of sets.
    """
    visited = [False] * num_locations
    components = []
    for i in range(num_locations):
        if not visited[i]:
            component = set()
            stack = [i]
            visited[i] = True
            while stack:
                node = stack.pop()
                component.add(node)
                for neighbor in graph[node]:
                    if not visited[neighbor]:
                        visited[neighbor] = True
                        stack.append(neighbor)
            components.append(component)
    return components


def build_adj(num_locations, edges):
    """
    Builds an adjacency dictionary for direct link cost computation.
    For each node, maps neighboring node to the minimum edge weight.
    """
    adj = defaultdict(dict)
    for u, v, w in edges:
        if v not in adj[u] or w < adj[u][v]:
            adj[u][v] = w
        if u not in adj[v] or w < adj[v][u]:
            adj[v][u] = w
    # Ensure every node has an entry in adj.
    for i in range(num_locations):
        if i not in adj:
            adj[i] = {}
    return adj


def compute_direct_link_cost(num_locations, adj, router_set):
    """
    For each non-router node, finds the minimum cost of a direct edge from a router in router_set.
    If the node is not directly adjacent to any router, it is assumed to be covered indirectly and
    does not incur a cost.
    
    Returns the sum of the minimum direct link costs for all non-router nodes.
    """
    total_cost = 0
    for node in range(num_locations):
        if node in router_set:
            continue
        min_cost = None
        for neighbor, cost in adj[node].items():
            if neighbor in router_set:
                if min_cost is None or cost < min_cost:
                    min_cost = cost
        if min_cost is not None:
            total_cost += min_cost
    return total_cost