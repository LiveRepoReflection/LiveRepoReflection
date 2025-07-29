from collections import defaultdict, deque
import heapq
from typing import List, Tuple, Set, Dict

def optimize_server_placement(
    nodes: List[int],
    edges: List[Tuple[int, int, int]],
    client_requests: List[Tuple[int, int, int]],
    initial_server_locations: List[int],
    max_server_count: int
) -> List[int]:
    # Input validation
    if not nodes and not edges and not client_requests and not initial_server_locations:
        return []
    
    if max_server_count < len(initial_server_locations):
        raise ValueError("Maximum server count cannot be less than initial server count")
    
    # Validate nodes exist in the network
    node_set = set(nodes)
    for n1, n2, _ in edges:
        if n1 not in node_set or n2 not in node_set:
            raise ValueError("Edge contains invalid node ID")
    
    for server in initial_server_locations:
        if server not in node_set:
            raise ValueError("Initial server location invalid")

    # Build adjacency list representation of the network
    graph = defaultdict(list)
    for n1, n2, capacity in edges:
        if capacity == 0:
            raise ValueError("Edge capacity cannot be zero")
        graph[n1].append((n2, capacity))
        graph[n2].append((n1, capacity))

    def calculate_congestion(server_locations: Set[int]) -> float:
        """Calculate maximum congestion for given server placement"""
        edge_load = defaultdict(float)
        
        for client, target_server, data_size in client_requests:
            if data_size == 0:
                continue
                
            # Find nearest server
            nearest_server = None
            min_distance = float('inf')
            path_to_server = None
            
            # BFS to find shortest path to nearest server
            for server in server_locations:
                distance, path = find_shortest_path(graph, client, server)
                if distance < min_distance:
                    min_distance = distance
                    nearest_server = server
                    path_to_server = path
            
            if not path_to_server:
                raise ValueError("No path exists between client and any server")
            
            # Update edge loads along the path
            for i in range(len(path_to_server)-1):
                n1, n2 = path_to_server[i], path_to_server[i+1]
                # Find capacity of this edge
                capacity = next(c for _, c in graph[n1] if _ == n2)
                edge_load[(min(n1,n2), max(n1,n2))] += data_size / capacity

        return max(edge_load.values()) if edge_load else 0.0

    def find_shortest_path(graph: Dict[int, List[Tuple[int, int]]], 
                         start: int, 
                         end: int) -> Tuple[int, List[int]]:
        """Find shortest path between two nodes using BFS"""
        if start == end:
            return 0, [start]
            
        visited = {start}
        queue = deque([(start, [start])])
        
        while queue:
            vertex, path = queue.popleft()
            for next_node, _ in graph[vertex]:
                if next_node == end:
                    return len(path), path + [next_node]
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, path + [next_node]))
                    
        return float('inf'), []

    def get_candidate_locations(current_servers: Set[int]) -> List[Set[int]]:
        """Generate candidate server placements"""
        candidates = []
        
        # If we can add more servers
        if len(current_servers) < max_server_count:
            # Try adding a new server at each possible location
            for node in nodes:
                if node not in current_servers:
                    new_placement = current_servers | {node}
                    candidates.append(new_placement)
        
        # Try moving existing servers (except initial servers)
        moveable_servers = current_servers - set(initial_server_locations)
        for server in moveable_servers:
            for node in nodes:
                if node not in current_servers:
                    new_placement = (current_servers - {server}) | {node}
                    candidates.append(new_placement)
                    
        return candidates

    # Initialize with initial server locations
    current_servers = set(initial_server_locations)
    current_congestion = calculate_congestion(current_servers)
    
    while True:
        best_placement = current_servers
        best_congestion = current_congestion
        improved = False
        
        # Generate and evaluate candidate placements
        for candidate in get_candidate_locations(current_servers):
            try:
                congestion = calculate_congestion(candidate)
                if congestion < best_congestion:
                    best_congestion = congestion
                    best_placement = candidate
                    improved = True
            except ValueError:
                continue
        
        if not improved:
            break
            
        current_servers = best_placement
        current_congestion = best_congestion
    
    return sorted(list(current_servers))