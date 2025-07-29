import collections

def hcc_collapse(num_nodes, edges, density_threshold):
    if num_nodes == 0:
        return [], []
    
    # Build adjacency list
    adj = collections.defaultdict(set)
    for u, v in edges:
        adj[u].add(v)
    
    # Kosaraju's algorithm to find SCCs
    visited = set()
    order = []
    
    def dfs(u):
        stack = [(u, False)]
        while stack:
            node, processed = stack.pop()
            if processed:
                order.append(node)
                continue
            if node in visited:
                continue
            visited.add(node)
            stack.append((node, True))
            for neighbor in adj[node]:
                if neighbor not in visited:
                    stack.append((neighbor, False))
    
    for u in range(num_nodes):
        if u not in visited:
            dfs(u)
    
    # Build reversed graph
    reversed_adj = collections.defaultdict(set)
    for u, v in edges:
        reversed_adj[v].add(u)
    
    visited = set()
    sccs = []
    
    def reversed_dfs(u, component):
        stack = [u]
        visited.add(u)
        while stack:
            node = stack.pop()
            component.add(node)
            for neighbor in reversed_adj[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)
        return component
    
    for u in reversed(order):
        if u not in visited:
            scc = reversed_dfs(u, set())
            sccs.append(scc)
    
    # Filter SCCs by density threshold
    hccs = []
    for scc in sccs:
        if len(scc) == 1:
            continue
        
        # Calculate density
        edge_count = 0
        for u in scc:
            for v in adj[u]:
                if v in scc and u != v:
                    edge_count += 1
        
        possible_edges = len(scc) * (len(scc) - 1)
        density = edge_count / possible_edges if possible_edges > 0 else 0
        
        if density >= density_threshold:
            hccs.append(scc)
    
    # Find maximal non-overlapping HCCs
    hccs.sort(key=len, reverse=True)
    selected_hccs = []
    covered = set()
    
    for hcc in hccs:
        if not covered.intersection(hcc):
            selected_hccs.append(hcc)
            covered.update(hcc)
    
    # Create node mapping
    node_map = {}
    supernodes = set()
    for hcc in selected_hccs:
        supernode = min(hcc)
        supernodes.add(supernode)
        for node in hcc:
            node_map[node] = supernode
    
    # Build collapsed graph
    collapsed_nodes = set()
    collapsed_edges = set()
    
    # Add regular nodes
    for u in range(num_nodes):
        if u not in node_map:
            collapsed_nodes.add(u)
    
    # Add supernodes
    for supernode in supernodes:
        collapsed_nodes.add(supernode)
    
    # Process edges
    for u, v in edges:
        src = node_map.get(u, u)
        dst = node_map.get(v, v)
        if src != dst:  # Skip self-loops in supernodes
            collapsed_edges.add((src, dst))
    
    # Convert to sorted lists
    sorted_nodes = sorted(collapsed_nodes)
    sorted_edges = sorted(collapsed_edges)
    
    return sorted_nodes, sorted_edges