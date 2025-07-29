from heapq import heappush, heappop
from collections import defaultdict
import sys

def find_optimal_path(N, M, graph, S, D, T_start, T_end, L, get_edge_cost, get_edge_capacity):
    """
    Find the optimal path considering dynamic costs, capacity constraints, and time windows.
    Uses a modified Dijkstra's algorithm with time-dependent costs and capacity constraints.
    """
    # Input validation
    if not (1 <= N <= 1000 and 1 <= M <= 5000 and 
            0 <= S < N and 0 <= D < N and 
            0 <= T_start < T_end <= 1000 and 
            1 <= L <= 100):
        raise ValueError("Invalid input parameters")

    # Build adjacency list
    adj_list = defaultdict(list)
    for u, v, _ in graph:
        adj_list[u].append(v)
        adj_list[v].append(u)  # bidirectional

    # Priority queue elements: (total_cost, current_time, node, path)
    pq = [(0, T_start, S, [S])]
    # Track visited states: (node, time)
    visited = set()
    
    # Best cost and path for each node at each time
    best_costs = defaultdict(lambda: float('inf'))
    best_costs[(S, T_start)] = 0

    while pq:
        total_cost, current_time, node, path = heappop(pq)

        # Skip if we've found a better path to this state
        if (node, current_time) in visited:
            continue

        visited.add((node, current_time))

        # Found destination within time window
        if node == D and T_start <= current_time <= T_end:
            return path

        # Look ahead within window L
        for next_node in adj_list[node]:
            for t in range(current_time, min(current_time + L + 1, T_end + 1)):
                # Check capacity constraint
                if get_edge_capacity(node, next_node, t) <= 0:
                    continue

                # Calculate new cost
                edge_cost = get_edge_cost(node, next_node, t)
                new_total_cost = total_cost + edge_cost

                # Check if this is a better path
                if new_total_cost < best_costs[(next_node, t)]:
                    best_costs[(next_node, t)] = new_total_cost
                    new_path = path + [next_node]
                    
                    # Add to priority queue with cost as priority
                    heappush(pq, (new_total_cost, t, next_node, new_path))

    # No valid path found
    return []

def validate_path(path, N, M, graph, S, D, T_start, T_end, get_edge_cost, get_edge_capacity):
    """
    Validate if the path meets all constraints
    """
    if not path:
        return False
    
    if path[0] != S or path[-1] != D:
        return False

    current_time = T_start
    total_cost = 0

    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        
        # Check if edge exists
        edge_exists = False
        for src, dst, _ in graph:
            if (src == u and dst == v) or (src == v and dst == u):
                edge_exists = True
                break
        if not edge_exists:
            return False

        # Check capacity
        if get_edge_capacity(u, v, current_time) <= 0:
            return False

        # Add cost
        total_cost += get_edge_cost(u, v, current_time)

    return T_start <= current_time <= T_end