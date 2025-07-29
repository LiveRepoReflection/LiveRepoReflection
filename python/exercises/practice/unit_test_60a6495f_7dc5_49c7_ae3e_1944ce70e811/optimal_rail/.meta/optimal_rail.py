import math
import heapq
from collections import defaultdict, deque

def design_rail_network(cities, coordinates, budget, cost_per_distance):
    """
    Design an optimal rail network that connects all cities with redundancy
    within the given budget.
    
    Args:
        cities: List of city names
        coordinates: Dict mapping city names to (lat, lon) coordinates
        budget: Maximum allowed cost for the network
        cost_per_distance: Cost per unit of distance
    
    Returns:
        List of (city1, city2) tuples representing rail connections, or empty list if impossible
    """
    # Calculate all possible edges and their costs
    edges = []
    for i in range(len(cities)):
        for j in range(i + 1, len(cities)):
            city1, city2 = cities[i], cities[j]
            lat1, lon1 = coordinates[city1]
            lat2, lon2 = coordinates[city2]
            distance = math.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2)
            cost = distance * cost_per_distance
            edges.append((cost, city1, city2))
    
    # Sort edges by cost
    edges.sort()
    
    # First, try to find a 2-edge-connected graph within budget using a modified Kruskal's algorithm
    result = find_2edge_connected_subgraph(cities, edges, budget)
    if result:
        return result
    
    # If no solution found, return empty list
    return []

def find_2edge_connected_subgraph(cities, edges, budget):
    """
    Try to find a 2-edge-connected subgraph within budget using a greedy approach.
    We first build a minimum spanning tree, then add additional edges to ensure
    2-edge-connectivity within budget constraints.
    """
    # First, build a minimum spanning tree using Kruskal's algorithm
    parent = {city: city for city in cities}
    rank = {city: 0 for city in cities}
    
    def find(city):
        if parent[city] != city:
            parent[city] = find(parent[city])
        return parent[city]
    
    def union(city1, city2):
        root1 = find(city1)
        root2 = find(city2)
        if root1 != root2:
            if rank[root1] < rank[root2]:
                parent[root1] = root2
            else:
                parent[root2] = root1
                if rank[root1] == rank[root2]:
                    rank[root1] += 1
    
    mst_edges = []
    remaining_edges = []
    total_cost = 0
    
    for cost, city1, city2 in edges:
        if find(city1) != find(city2):
            union(city1, city2)
            mst_edges.append((city1, city2))
            total_cost += cost
        else:
            remaining_edges.append((cost, city1, city2))
    
    # Check if we have a connected graph
    root_set = set(find(city) for city in cities)
    if len(root_set) > 1:
        # Cannot even form a basic connected graph
        return []
    
    # Build adjacency list from MST
    graph = defaultdict(list)
    for city1, city2 in mst_edges:
        graph[city1].append(city2)
        graph[city2].append(city1)
    
    # Find bridges in the MST
    bridges = find_bridges(graph, cities)
    
    # Sort remaining edges by cost for greedy selection
    remaining_edges.sort()
    
    # Try to add edges to eliminate bridges, respecting the budget
    result_graph = set(mst_edges)
    
    # Add edges to eliminate bridges while staying within budget
    for cost, city1, city2 in remaining_edges:
        if not bridges:  # No more bridges to fix
            break
        
        if total_cost + cost > budget:
            continue
        
        # Check if adding this edge would eliminate a bridge
        new_edge = (city1, city2) if city1 < city2 else (city2, city1)
        
        if removes_bridges(graph, bridges, city1, city2):
            graph[city1].append(city2)
            graph[city2].append(city1)
            result_graph.add(new_edge)
            total_cost += cost
            
            # Recalculate bridges after adding the new edge
            bridges = find_bridges(graph, cities)
    
    # Check if there are any bridges left
    if bridges:
        # Try a different approach: start from scratch and use a more sophisticated algorithm
        # to find a 2-edge-connected subgraph within budget
        return try_alternative_approach(cities, edges, budget)
    
    # Return the list of edges
    return list(result_graph)

def find_bridges(graph, cities):
    """
    Find all bridges in the graph using Tarjan's algorithm.
    A bridge is an edge whose removal disconnects the graph.
    """
    visited = set()
    discovery = {}
    low = {}
    parent = {city: None for city in cities}
    bridges = set()
    time = [0]  # Use a list to simulate a mutable integer reference
    
    def dfs(u):
        visited.add(u)
        discovery[u] = low[u] = time[0]
        time[0] += 1
        
        for v in graph[u]:
            if v not in visited:
                parent[v] = u
                dfs(v)
                
                # Check if the subtree rooted with v has a connection to
                # one of the ancestors of u
                low[u] = min(low[u], low[v])
                
                # If the lowest vertex reachable from the subtree under v
                # is below u in the DFS tree, then u-v is a bridge
                if low[v] > discovery[u]:
                    bridge = (u, v) if u < v else (v, u)
                    bridges.add(bridge)
            
            elif v != parent[u]:  # Update low value of u for parent function calls
                low[u] = min(low[u], discovery[v])
    
    for city in cities:
        if city not in visited:
            dfs(city)
    
    return bridges

def removes_bridges(graph, bridges, city1, city2):
    """
    Check if adding an edge between city1 and city2 would eliminate a bridge.
    """
    if (city1, city2) in bridges or (city2, city1) in bridges:
        return True
    
    # Check if adding this edge creates a cycle that contains a bridge
    visited = set()
    path = []
    
    def dfs(current, target, parent):
        visited.add(current)
        path.append(current)
        
        if current == target:
            return True
        
        for neighbor in graph[current]:
            if neighbor != parent and neighbor not in visited:
                if dfs(neighbor, target, current):
                    return True
        
        path.pop()
        return False
    
    # If there's already a path from city1 to city2, adding this edge creates a cycle
    found_path = dfs(city1, city2, None)
    
    if found_path:
        # Check if the cycle contains a bridge
        for i in range(len(path) - 1):
            edge = (path[i], path[i+1]) if path[i] < path[i+1] else (path[i+1], path[i])
            if edge in bridges:
                return True
    
    return False

def try_alternative_approach(cities, edges, budget):
    """
    Try an alternative approach to find a 2-edge-connected subgraph within budget.
    This uses a more direct approach focusing on ensuring each vertex has at least 2 connections.
    """
    n = len(cities)
    city_to_idx = {city: i for i, city in enumerate(cities)}
    
    # We need at least 2 edges per city for redundancy, which means at least n edges
    # And to have a cycle for each potential bridge, we need at least n+1 edges
    min_edges_needed = max(n, n+1)
    
    # Use a greedy approach to select edges
    selected_edges = []
    total_cost = 0
    city_degree = {city: 0 for city in cities}
    
    # First, ensure each city has at least one connection (build a spanning tree)
    uf_parent = {city: city for city in cities}
    uf_rank = {city: 0 for city in cities}
    
    def find(city):
        if uf_parent[city] != city:
            uf_parent[city] = find(uf_parent[city])
        return uf_parent[city]
    
    def union(city1, city2):
        root1 = find(city1)
        root2 = find(city2)
        if root1 != root2:
            if uf_rank[root1] < uf_rank[root2]:
                uf_parent[root1] = root2
            else:
                uf_parent[root2] = root1
                if uf_rank[root1] == uf_rank[root2]:
                    uf_rank[root1] += 1
    
    for cost, city1, city2 in edges:
        if find(city1) != find(city2) and total_cost + cost <= budget:
            union(city1, city2)
            selected_edges.append((city1, city2))
            total_cost += cost
            city_degree[city1] += 1
            city_degree[city2] += 1
    
    # Check if we have a connected graph
    if len(set(find(city) for city in cities)) > 1:
        return []  # Cannot even form a basic connected graph within budget
    
    # Next, prioritize adding edges to cities with degree 1 to ensure redundancy
    for cost, city1, city2 in sorted(edges, key=lambda x: (-(city_degree[x[1]] == 1 or city_degree[x[2]] == 1), x[0])):
        if (city1, city2) not in selected_edges and (city2, city1) not in selected_edges:
            if total_cost + cost <= budget:
                selected_edges.append((city1, city2))
                total_cost += cost
                city_degree[city1] += 1
                city_degree[city2] += 1
                
                # Check if all cities have at least degree 2
                if all(degree >= 2 for degree in city_degree.values()):
                    # Verify that the graph is 2-edge-connected
                    graph = defaultdict(list)
                    for c1, c2 in selected_edges:
                        graph[c1].append(c2)
                        graph[c2].append(c1)
                    
                    bridges = find_bridges(graph, cities)
                    if not bridges:
                        return selected_edges
    
    # If we can't ensure 2-edge-connectivity within budget, use a different approach
    return biconnectivity_algorithm(cities, edges, budget)

def biconnectivity_algorithm(cities, edges, budget):
    """
    Use a more sophisticated algorithm to find a 2-edge-connected graph within budget.
    This uses an iterative approach starting with the minimal spanning tree and
    incrementally adding edges to establish biconnectivity.
    """
    # Initialize graph with no edges
    graph = defaultdict(list)
    edge_costs = {}
    
    # First, build a minimum spanning tree using Kruskal's algorithm
    parent = {city: city for city in cities}
    rank = {city: 0 for city in cities}
    
    def find(city):
        if parent[city] != city:
            parent[city] = find(parent[city])
        return parent[city]
    
    def union(city1, city2):
        root1 = find(city1)
        root2 = find(city2)
        if root1 != root2:
            if rank[root1] < rank[root2]:
                parent[root1] = root2
            else:
                parent[root2] = root1
                if rank[root1] == rank[root2]:
                    rank[root1] += 1
    
    selected_edges = []
    total_cost = 0
    
    # Sort edges by cost and build the minimum spanning tree
    sorted_edges = sorted(edges, key=lambda x: x[0])
    
    for cost, city1, city2 in sorted_edges:
        if find(city1) != find(city2):
            union(city1, city2)
            selected_edges.append((city1, city2))
            graph[city1].append(city2)
            graph[city2].append(city1)
            edge_costs[(city1, city2)] = cost
            edge_costs[(city2, city1)] = cost
            total_cost += cost
    
    # Check if we have enough budget remaining to ensure 2-edge-connectivity
    remaining_budget = budget - total_cost
    
    # Find all articulation points (cut vertices) and bridges
    bridges = find_bridges(graph, cities)
    
    # If there are no bridges, we already have a 2-edge-connected graph
    if not bridges:
        return selected_edges
    
    # Sort remaining edges by cost for greedy selection
    remaining_edges = []
    for cost, city1, city2 in sorted_edges:
        edge = (city1, city2)
        rev_edge = (city2, city1)
        if edge not in edge_costs and rev_edge not in edge_costs:
            remaining_edges.append((cost, city1, city2))
    
    # Try to eliminate bridges by adding additional edges
    for cost, city1, city2 in remaining_edges:
        if total_cost + cost > budget:
            continue
            
        # Check if adding this edge would create a cycle that includes a bridge
        new_path = bfs_path(graph, city1, city2)
        if new_path:
            # Adding this edge creates a cycle
            cycle_edges = []
            for i in range(len(new_path) - 1):
                c1, c2 = new_path[i], new_path[i+1]
                cycle_edges.append((c1, c2) if c1 < c2 else (c2, c1))
            
            # Check if the cycle contains any bridge
            has_bridge = any(edge in bridges for edge in cycle_edges)
            if has_bridge:
                # Add the edge to eliminate the bridge
                graph[city1].append(city2)
                graph[city2].append(city1)
                edge_costs[(city1, city2)] = cost
                edge_costs[(city2, city1)] = cost
                selected_edges.append((city1, city2))
                total_cost += cost
                
                # Recalculate bridges
                bridges = find_bridges(graph, cities)
                
                if not bridges:
                    return selected_edges
    
    # If we've added all possible edges and still have bridges, we can't satisfy the requirements
    return []

def bfs_path(graph, start, end):
    """Find a path from start to end using BFS"""
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        vertex, path = queue.popleft()
        if vertex == end:
            return path
            
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return None  # No path exists