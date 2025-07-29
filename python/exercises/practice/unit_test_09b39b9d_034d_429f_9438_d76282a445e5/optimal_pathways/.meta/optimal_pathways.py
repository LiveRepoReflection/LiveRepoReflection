import heapq
from collections import defaultdict


def find_k_shortest_paths(n, m, edges, district_assignments, risk_factors, destination, k, max_risk):
    """
    Find the k shortest paths from node 0 to the destination node, subject to a maximum risk constraint.
    
    Args:
        n: Number of nodes in the graph (0 to n-1)
        m: Number of edges in the graph
        edges: List of tuples (u, v, w) representing directed edges from u to v with weight w
        district_assignments: List where district_assignments[i] is the district to which node i belongs
        risk_factors: List where risk_factors[i] is the risk factor of district i
        destination: The destination node
        k: Number of shortest paths to find
        max_risk: Maximum allowable risk for any path
        
    Returns:
        List of up to k shortest paths from node 0 to destination, where each path is a list of nodes
    """
    # Handle the case where start and destination are the same
    if 0 == destination:
        return [[0]]
    
    # Build adjacency list representation of the graph
    graph = defaultdict(list)
    for u, v, w in edges:
        graph[u].append((v, w))
    
    # Modified Yen's algorithm for k shortest paths with risk constraint
    
    # Track shortest paths found
    result_paths = []
    
    # Set to track considered path signatures to avoid duplicates
    candidates = []
    visited_signatures = set()
    
    # Find the initial shortest path using Dijkstra's algorithm
    first_path = find_shortest_path(graph, 0, destination, district_assignments, risk_factors, max_risk)
    
    if not first_path:
        return []  # No valid path exists
    
    # Add the first path to the result
    result_paths.append(first_path)
    
    if k == 1:
        return result_paths
    
    # Generate k-1 more alternative paths
    for _ in range(k - 1):
        # Current shortest path from the previous iteration
        prev_path = result_paths[-1]
        
        # For each node in the previous path (except the last)
        for i in range(len(prev_path) - 1):
            # Create a rootPath which is the prefix of the previous path from 0 to i
            root_path = prev_path[:i+1]
            root_node = root_path[-1]
            
            # Calculate the risk of the root path
            root_risk = calculate_path_risk(root_path, district_assignments, risk_factors)
            
            # Create a temporary graph by removing edges to avoid cycles and force deviation
            # Remove edges that would create a path we've already seen
            temp_graph = create_temp_graph(graph, root_path, prev_path, result_paths, i)
            
            # Find the shortest path from the root_node to the destination in the temp graph
            deviation_path = find_shortest_path(
                temp_graph, root_node, destination, 
                district_assignments, risk_factors, 
                max_risk - root_risk, # remaining allowed risk
                visited_path=set(root_path[:-1]) # avoid cycles
            )
            
            if deviation_path:
                # Combine the root path with the deviation path (without duplicating the root node)
                candidate_path = root_path + deviation_path[1:]
                
                # Check if this path is valid and hasn't been seen before
                path_signature = tuple(candidate_path)
                if path_signature not in visited_signatures:
                    visited_signatures.add(path_signature)
                    # Calculate the total travel time for this path
                    travel_time = calculate_path_travel_time(candidate_path, graph)
                    # Add to candidates
                    heapq.heappush(candidates, (travel_time, candidate_path))
        
        # No more candidates
        if not candidates:
            break
            
        # Get the next best path
        _, next_path = heapq.heappop(candidates)
        result_paths.append(next_path)
    
    return result_paths


def find_shortest_path(graph, start, end, district_assignments, risk_factors, max_risk, visited_path=None):
    """
    Find the shortest path from start to end using Dijkstra's algorithm, 
    considering the risk constraint.
    """
    # Initialize
    if visited_path is None:
        visited_path = set()
    
    # Priority queue for Dijkstra's algorithm: (travel_time, risk, current_node, path)
    pq = [(0, risk_factors[district_assignments[start]], start, [start])]
    visited = set()
    
    while pq:
        time, risk, node, path = heapq.heappop(pq)
        
        # If we reached the destination, return the path
        if node == end:
            return path
        
        # Skip if we've already visited this node with a better time/risk
        if node in visited:
            continue
        
        visited.add(node)
        
        # Explore neighbors
        for neighbor, weight in graph[node]:
            # Skip if this would create a cycle with the root path
            if neighbor in visited_path:
                continue
                
            # Calculate new risk by adding the risk of the neighbor's district
            neighbor_district = district_assignments[neighbor]
            new_risk = risk + risk_factors[neighbor_district]
            
            # Skip if the risk exceeds the maximum allowed
            if new_risk > max_risk:
                continue
            
            # Calculate new travel time
            new_time = time + weight
            
            # Add to priority queue
            heapq.heappush(pq, (new_time, new_risk, neighbor, path + [neighbor]))
    
    return []  # No path found


def create_temp_graph(graph, root_path, prev_path, result_paths, spur_index):
    """
    Create a temporary graph by removing certain edges to force deviation.
    """
    temp_graph = defaultdict(list)
    
    # Copy the original graph
    for node in graph:
        temp_graph[node] = graph[node].copy()
    
    root_node = root_path[-1]
    next_node = prev_path[spur_index + 1]
    
    # Remove the edge that was used in the previous path at the spur node
    temp_graph[root_node] = [(v, w) for v, w in temp_graph[root_node] if v != next_node]
    
    # For each previously found path that shares the same root path
    for path in result_paths:
        if len(path) > spur_index + 1 and path[:spur_index+1] == root_path:
            # Remove the edge that was used in this path at the spur node
            u = path[spur_index]
            v = path[spur_index + 1]
            temp_graph[u] = [(n, w) for n, w in temp_graph[u] if n != v]
    
    return temp_graph


def calculate_path_risk(path, district_assignments, risk_factors):
    """
    Calculate the total risk of a path.
    """
    risk = 0
    unique_districts = set()
    
    for node in path:
        district = district_assignments[node]
        unique_districts.add(district)
    
    for district in unique_districts:
        risk += risk_factors[district]
    
    return risk


def calculate_path_travel_time(path, graph):
    """
    Calculate the total travel time of a path.
    """
    time = 0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        for neighbor, weight in graph[u]:
            if neighbor == v:
                time += weight
                break
    return time