import math

def optimal_network(n, m, links, P):
    best_cost = float('inf')
    num_links = len(links)
    
    # Iterate over all possible subsets of links using bitmask
    for mask in range(1, 1 << num_links):
        # A minimum of n edges is necessary for a 2-connected graph (cycle on n nodes)
        if bin(mask).count("1") < n:
            continue

        subset_edges = []
        total_cost = 0
        prob_list = []
        
        for i in range(num_links):
            if mask & (1 << i):
                u, v, cost, prob = links[i]
                subset_edges.append((u, v))
                total_cost += cost
                prob_list.append(prob)
                
        # Check the failure probability constraint using product of probabilities.
        prod = math.prod(prob_list)
        if prod > P:
            continue
        
        # Build the graph for the chosen subset of edges.
        graph = {i: set() for i in range(n)}
        for (u, v) in subset_edges:
            graph[u].add(v)
            graph[v].add(u)
        
        # Check that the full graph is connected.
        if not is_connected(graph, n, removed=-1):
            continue
        
        # Check resilience: the graph must remain connected after removal of any single node.
        resilient = True
        for r in range(n):
            if not is_connected(graph, n, removed=r):
                resilient = False
                break
        if not resilient:
            continue
        
        # Valid network found, update minimal cost.
        if total_cost < best_cost:
            best_cost = total_cost
            
    return best_cost if best_cost != float('inf') else -1

def is_connected(graph, n, removed):
    """
    Checks connectivity of the graph.
    If removed is not -1, the node with that index is considered removed.
    """
    nodes = [i for i in range(n) if i != removed]
    if not nodes:
        return True
    start = nodes[0]
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor == removed:
                continue
            if neighbor not in visited:
                stack.append(neighbor)
    return set(nodes) == visited