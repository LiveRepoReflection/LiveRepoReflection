import heapq
from collections import defaultdict, deque
from typing import List, Tuple, Dict, Set, Optional


def optimize_routing(N: int, edges: List[Tuple[int, int, int, int]], S: int, D: int, packets: List[int]) -> List[List[int]]:
    """
    Optimize packet routing to minimize the maximum latency while respecting capacity constraints.
    
    Args:
        N: Number of nodes in the network
        edges: List of (u, v, latency, capacity) tuples representing network links
        S: Source node
        D: Destination node
        packets: List of packet sizes
    
    Returns:
        List of paths for each packet, or empty list if routing is impossible
    """
    # Special case: if source equals destination
    if S == D:
        return [[S] for _ in packets]

    # Build adjacency list and store latency and capacity information
    graph = [[] for _ in range(N)]
    latencies = {}
    capacities = {}
    
    for u, v, latency, capacity in edges:
        graph[u].append(v)
        latencies[(u, v)] = latency
        capacities[(u, v)] = capacity
    
    # Check if destination is reachable from source
    if not is_reachable(graph, S, D):
        return []
    
    # Sort packets in descending order to route larger packets first
    sorted_packets = sorted(enumerate(packets), key=lambda x: x[1], reverse=True)
    
    # Calculate all possible paths from S to D with their total latencies
    all_paths = find_all_paths(graph, latencies, S, D)
    
    if not all_paths:
        return []
    
    # Sort paths by total latency
    all_paths.sort(key=lambda x: x[1])
    
    # Try to assign packets to paths
    remaining_capacities = {edge: capacities[edge] for edge in capacities}
    packet_paths = [None] * len(packets)
    
    # First attempt: greedy assignment based on latency
    for packet_idx, packet_size in sorted_packets:
        assigned = False
        
        for path_nodes, path_latency in all_paths:
            # Check if this path has enough capacity for the packet
            can_use_path = True
            
            for i in range(len(path_nodes) - 1):
                edge = (path_nodes[i], path_nodes[i+1])
                if remaining_capacities[edge] < packet_size:
                    can_use_path = False
                    break
            
            if can_use_path:
                # Assign packet to this path
                packet_paths[packet_idx] = path_nodes
                
                # Update remaining capacities
                for i in range(len(path_nodes) - 1):
                    edge = (path_nodes[i], path_nodes[i+1])
                    remaining_capacities[edge] -= packet_size
                
                assigned = True
                break
        
        if not assigned:
            # Could not assign this packet, so routing is impossible
            return []
    
    # If we've successfully assigned all packets, return the paths
    return packet_paths


def is_reachable(graph: List[List[int]], start: int, end: int) -> bool:
    """
    Determine if end node is reachable from start node using BFS.
    """
    visited = [False] * len(graph)
    queue = deque([start])
    visited[start] = True
    
    while queue:
        node = queue.popleft()
        
        if node == end:
            return True
        
        for neighbor in graph[node]:
            if not visited[neighbor]:
                visited[neighbor] = True
                queue.append(neighbor)
    
    return False


def find_all_paths(graph: List[List[int]], latencies: Dict[Tuple[int, int], int], 
                  start: int, end: int, max_paths: int = 100) -> List[Tuple[List[int], int]]:
    """
    Find all paths from start to end using modified Dijkstra's algorithm.
    Returns list of (path, total_latency) tuples, limited to max_paths.
    """
    # Priority queue for Dijkstra's algorithm: (latency, node, path)
    pq = [(0, start, [start])]
    paths = []
    
    # To prevent cycles, keep track of visited nodes in each path
    visited_in_path = defaultdict(set)
    visited_in_path[start].add(tuple([start]))
    
    while pq and len(paths) < max_paths:
        latency, node, path = heapq.heappop(pq)
        
        if node == end:
            paths.append((path, latency))
            continue
        
        for neighbor in graph[node]:
            # Skip if this would create a cycle
            if neighbor in path:
                continue
            
            new_path = path + [neighbor]
            new_latency = latency + latencies[(node, neighbor)]
            
            # Check if this path to neighbor is unique
            path_tuple = tuple(new_path)
            if path_tuple not in visited_in_path[neighbor]:
                visited_in_path[neighbor].add(path_tuple)
                heapq.heappush(pq, (new_latency, neighbor, new_path))
    
    return paths


def min_latency_max_flow(graph: List[List[int]], capacities: Dict[Tuple[int, int], int], 
                        latencies: Dict[Tuple[int, int], int], S: int, D: int, 
                        total_flow_needed: int) -> Optional[Dict[Tuple[int, int], int]]:
    """
    Try to find a flow assignment that satisfies the total flow needed while minimizing latency.
    Returns a dictionary mapping edges to flow amounts, or None if impossible.
    """
    # Implementation not needed for the current solution approach, but could be used
    # for a more sophisticated flow-based solution in the future.
    return None