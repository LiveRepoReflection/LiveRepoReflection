def min_connections_needed(servers, connections):
    """
    Calculate the minimum number of additional connections needed to make the network strongly connected.
    
    Args:
        servers: A list of strings representing server identifiers.
        connections: A list of tuples (source, destination) representing directional connections.
    
    Returns:
        An integer representing the minimum number of additional connections needed.
        
    Raises:
        ValueError: If any connection refers to a server not in the servers list.
    """
    # Handle empty cases
    if not servers:
        return 0
    
    # Handle single server case
    if len(servers) == 1:
        return 0
    
    # Handle no connections case
    if not connections:
        # Need n-1 connections to connect n servers
        return len(servers) - 1
    
    # Create a map for faster lookup of servers
    server_set = set(servers)
    
    # Validate all connections
    for source, dest in connections:
        if source not in server_set or dest not in server_set:
            invalid_server = source if source not in server_set else dest
            raise ValueError(f"Invalid server '{invalid_server}' found in connections")
    
    # Remove duplicate connections and self-loops
    unique_connections = set((source, dest) for source, dest in connections if source != dest)
    
    # Build adjacency list for graph
    graph = {server: [] for server in servers}
    for source, dest in unique_connections:
        graph[source].append(dest)
    
    # Find strongly connected components using Kosaraju's algorithm
    sccs = find_strongly_connected_components(graph, servers)
    
    if len(sccs) == 1:
        # If there is only one strongly connected component, the network is already strongly connected
        return 0
    
    # Create a condensed graph where each node represents a strongly connected component
    condensed_graph = {i: set() for i in range(len(sccs))}
    
    # Map from server to SCC index
    server_to_scc = {}
    for i, scc in enumerate(sccs):
        for server in scc:
            server_to_scc[server] = i
    
    # Build edges in the condensed graph
    for source_server, dest_list in graph.items():
        source_scc = server_to_scc[source_server]
        for dest_server in dest_list:
            dest_scc = server_to_scc[dest_server]
            if source_scc != dest_scc:
                condensed_graph[source_scc].add(dest_scc)
    
    # Count in-degree and out-degree of each SCC
    in_degree = {i: 0 for i in range(len(sccs))}
    out_degree = {i: 0 for i in range(len(sccs))}
    
    for scc_idx, outgoing_sccs in condensed_graph.items():
        out_degree[scc_idx] = len(outgoing_sccs)
        for outgoing_scc in outgoing_sccs:
            in_degree[outgoing_scc] += 1
    
    # Count SCCs with zero in-degree and zero out-degree
    zero_in = sum(1 for scc_idx in range(len(sccs)) if in_degree[scc_idx] == 0)
    zero_out = sum(1 for scc_idx in range(len(sccs)) if out_degree[scc_idx] == 0)
    
    # The minimum number of additional connections needed is max(zero_in, zero_out)
    # If there's only one SCC, the result is 0
    return max(zero_in, zero_out) if len(sccs) > 1 else 0

def find_strongly_connected_components(graph, servers):
    """
    Find strongly connected components in a directed graph using Kosaraju's algorithm.
    
    Args:
        graph: A dictionary representing the adjacency list of the graph.
        servers: A list of server identifiers.
    
    Returns:
        A list of lists, where each inner list contains the servers in one strongly connected component.
    """
    # First DFS to determine finishing order
    visited = set()
    finish_order = []
    
    def dfs_first(node):
        if node in visited:
            return
        visited.add(node)
        for neighbor in graph[node]:
            dfs_first(neighbor)
        finish_order.append(node)
    
    for server in servers:
        if server not in visited:
            dfs_first(server)
    
    # Transpose the graph
    transposed = {server: [] for server in servers}
    for source, dest_list in graph.items():
        for dest in dest_list:
            transposed[dest].append(source)
    
    # Second DFS to find SCCs
    visited.clear()
    sccs = []
    
    def dfs_second(node, component):
        if node in visited:
            return
        visited.add(node)
        component.append(node)
        for neighbor in transposed[node]:
            dfs_second(neighbor, component)
    
    # Process nodes in reverse order of finishing time
    for server in reversed(finish_order):
        if server not in visited:
            current_scc = []
            dfs_second(server, current_scc)
            sccs.append(current_scc)
    
    return sccs