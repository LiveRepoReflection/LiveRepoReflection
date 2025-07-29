def find_optimal_components(n, m, dependencies, k):
    """
    Find optimal component decomposition that minimizes inter-component dependencies.
    
    Args:
        n: Number of modules
        m: Number of dependencies
        dependencies: List of (u, v) tuples representing dependencies from u to v
        k: Maximum size of a component
        
    Returns:
        List of lists, where each inner list represents a component
    """
    # Create adjacency lists for the directed graph
    graph = [[] for _ in range(n)]
    in_degree = [[] for _ in range(n)]
    
    for u, v in dependencies:
        graph[u].append(v)
        in_degree[v].append(u)
    
    # Topologically sort the nodes
    topo_order = topological_sort(n, graph)
    
    # Build a directed graph of modules with dependency weights
    weighted_graph = build_weighted_graph(n, graph, in_degree)
    
    # Group modules into components using dynamic programming
    return optimize_components(n, k, topo_order, weighted_graph, graph, in_degree)


def topological_sort(n, graph):
    """Perform topological sort of the graph."""
    visited = [False] * n
    temp = [False] * n
    order = []
    
    def dfs(node):
        if temp[node]:
            return  # Cycle detected (though problem guarantees no cycles)
        if visited[node]:
            return
        
        temp[node] = True
        for neighbor in graph[node]:
            dfs(neighbor)
        
        temp[node] = False
        visited[node] = True
        order.append(node)
    
    for i in range(n):
        if not visited[i]:
            dfs(i)
    
    return order[::-1]  # Reverse for correct topological order


def build_weighted_graph(n, graph, in_degree):
    """
    Build a weighted graph where edge (u,v) has weight representing the 
    importance of keeping u and v in the same component.
    """
    weighted_graph = [[0 for _ in range(n)] for _ in range(n)]
    
    # Direct dependencies have weight 1
    for u in range(n):
        for v in graph[u]:
            weighted_graph[u][v] = 1
            weighted_graph[v][u] = 1  # Make it undirected for component formation
    
    # Modules with common dependencies or dependents have additional weight
    for u in range(n):
        for v in range(u+1, n):
            # Common outgoing dependencies
            common_out = len(set(graph[u]) & set(graph[v]))
            # Common incoming dependencies
            common_in = len(set(in_degree[u]) & set(in_degree[v]))
            
            # Add weights based on common connections
            weighted_graph[u][v] += 0.5 * (common_out + common_in)
            weighted_graph[v][u] += 0.5 * (common_out + common_in)
    
    return weighted_graph


def optimize_components(n, k, topo_order, weighted_graph, graph, in_degree):
    """
    Use a combination of greedy and dynamic programming to group modules into components
    that minimize inter-component dependencies.
    """
    if k == n:  # Edge case: can put all modules in one component
        return [list(range(n))]
    
    if k == 1:  # Edge case: each module must be in its own component
        return [[i] for i in range(n)]
    
    # First, try a greedy approach using the topological order
    components = []
    current_component = []
    component_map = {}  # Maps node to component index
    
    for node in topo_order:
        # Check if adding this node to current component maintains DAG property
        valid = True
        if len(current_component) >= k:
            valid = False
        
        # If valid, add to current component
        if valid:
            current_component.append(node)
        else:
            # Start a new component
            components.append(current_component)
            for n in current_component:
                component_map[n] = len(components) - 1
            current_component = [node]
    
    # Don't forget the last component
    if current_component:
        components.append(current_component)
        for n in current_component:
            component_map[n] = len(components) - 1
    
    # Try to improve the initial solution using local search
    max_iterations = 100
    for _ in range(max_iterations):
        improved = False
        
        # For each node, try moving it to a different component
        for node in range(n):
            current_comp = component_map[node]
            best_comp = current_comp
            best_gain = 0
            
            for target_comp in range(len(components)):
                if target_comp == current_comp:
                    continue
                
                # Skip if target component is already at max size
                if len(components[target_comp]) >= k:
                    continue
                
                # Calculate gain/loss of moving node to target_comp
                gain = calculate_move_gain(node, current_comp, target_comp, component_map, graph, in_degree)
                
                # Check if moving would create cycles between components
                if gain > best_gain and not would_create_cycle(node, components, component_map, target_comp, graph, in_degree):
                    best_gain = gain
                    best_comp = target_comp
            
            # If beneficial move found, make the move
            if best_comp != current_comp:
                components[current_comp].remove(node)
                components[best_comp].append(node)
                component_map[node] = best_comp
                improved = True
        
        # If no improvements found in this iteration, stop
        if not improved:
            break
    
    # Try merging small components if it reduces inter-component dependencies
    return try_merging_components(components, component_map, n, k, graph)


def calculate_move_gain(node, from_comp, to_comp, component_map, graph, in_degree):
    """Calculate the gain (reduction in inter-component dependencies) by moving a node."""
    gain = 0
    
    # Check outgoing edges
    for neighbor in graph[node]:
        neighbor_comp = component_map[neighbor]
        if neighbor_comp == from_comp:
            # Was intra-component, will become inter-component
            gain -= 1
        elif neighbor_comp == to_comp:
            # Was inter-component, will become intra-component
            gain += 1
    
    # Check incoming edges
    for parent in in_degree[node]:
        parent_comp = component_map[parent]
        if parent_comp == from_comp:
            # Was intra-component, will become inter-component
            gain -= 1
        elif parent_comp == to_comp:
            # Was inter-component, will become intra-component
            gain += 1
    
    return gain


def would_create_cycle(node, components, component_map, target_comp, graph, in_degree):
    """Check if moving node to target_comp would create cycles in the component dependency graph."""
    # Create a temporary mapping with the node moved
    temp_map = component_map.copy()
    temp_map[node] = target_comp
    
    # Build component dependency graph
    comp_deps = set()
    for u in range(len(temp_map)):
        for v in graph[u]:
            if temp_map[u] != temp_map[v]:
                comp_deps.add((temp_map[u], temp_map[v]))
    
    # Check for cycles in the component dependency graph
    visited = set()
    temp_visited = set()
    
    def has_cycle(comp):
        if comp in temp_visited:
            return True
        if comp in visited:
            return False
        
        temp_visited.add(comp)
        
        for next_comp in [v for u, v in comp_deps if u == comp]:
            if has_cycle(next_comp):
                return True
        
        temp_visited.remove(comp)
        visited.add(comp)
        return False
    
    # Check for cycles starting from each component
    for comp in range(len(components)):
        if comp not in visited:
            if has_cycle(comp):
                return True
    
    return False


def try_merging_components(components, component_map, n, k, graph):
    """Try to merge small components if it reduces inter-component dependencies."""
    merged = True
    while merged:
        merged = False
        best_merge = None
        best_gain = 0
        
        for i in range(len(components)):
            for j in range(i + 1, len(components)):
                # Skip if merged component would exceed size limit
                if len(components[i]) + len(components[j]) > k:
                    continue
                
                # Calculate gain from merging these components
                gain = 0
                for node_i in components[i]:
                    for node_j in components[j]:
                        # Check if there are dependencies between these nodes
                        if node_j in graph[node_i]:
                            gain += 1
                        if node_i in graph[node_j]:
                            gain += 1
                
                if gain > best_gain:
                    best_gain = gain
                    best_merge = (i, j)
        
        # If beneficial merge found, merge components
        if best_merge and best_gain > 0:
            i, j = best_merge
            # Add all nodes from j to i
            components[i].extend(components[j])
            # Update component map
            for node in components[j]:
                component_map[node] = i
            # Remove component j
            components.pop(j)
            merged = True
    
    return components