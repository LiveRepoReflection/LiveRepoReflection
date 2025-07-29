from heapq import heappush, heappop
from collections import defaultdict
import time

def find_k_shortest_paths(graph, start, end, k, priority_nodes, coordination_window, 
                         capacity_penalty, prev_routes, updates):
    if k <= 0:
        raise ValueError("k must be positive")
    if coordination_window <= 0:
        raise ValueError("coordination_window must be positive")
    if start not in graph or end not in graph:
        raise ValueError("Start or end node not in graph")

    # Apply real-time updates to the graph
    updated_graph = update_graph(graph, updates)
    
    # Calculate current time for coordination window
    current_time = time.time()
    
    # Track edge usage within coordination window
    edge_usage = calculate_edge_usage(prev_routes, current_time, coordination_window)
    
    # Priority queue for Dijkstra's algorithm
    # Format: (cost, path, visited_priority_nodes)
    pq = [(0, [start], set())]
    # Track visited states to avoid cycles
    visited = set()
    # Store found paths
    paths = []
    
    while pq and len(paths) < k:
        cost, path, visited_priorities = heappop(pq)
        current = path[-1]
        
        # Found a path to destination
        if current == end:
            paths.append(path)
            continue
            
        # Skip if we've been in this state before
        state = (current, tuple(sorted(visited_priorities)))
        if state in visited:
            continue
        visited.add(state)
        
        # Explore neighbors
        for next_node, base_cost, capacity in updated_graph[current]:
            if next_node in path:  # Avoid cycles
                continue
                
            # Calculate actual cost considering various factors
            actual_cost = calculate_edge_cost(
                current, next_node, base_cost, capacity,
                edge_usage, capacity_penalty, next_node in priority_nodes
            )
            
            # Update visited priority nodes
            new_priorities = visited_priorities.copy()
            if next_node in priority_nodes:
                new_priorities.add(next_node)
            
            # Add new path to priority queue
            new_path = path + [next_node]
            new_cost = cost + actual_cost
            heappush(pq, (new_cost, new_path, new_priorities))
    
    return paths

def update_graph(graph, updates):
    """Apply real-time updates to the graph."""
    updated_graph = defaultdict(list)
    
    # Copy original graph
    for node, edges in graph.items():
        updated_graph[node].extend(edges)
    
    # Apply updates
    for start_node, end_node, new_cost, new_capacity in updates:
        # Remove old edge if it exists
        updated_graph[start_node] = [
            (n, c, cap) for n, c, cap in updated_graph[start_node]
            if n != end_node
        ]
        # Add new edge
        updated_graph[start_node].append((end_node, new_cost, new_capacity))
    
    return updated_graph

def calculate_edge_usage(prev_routes, current_time, coordination_window):
    """Calculate current edge usage based on previous routes."""
    edge_usage = defaultdict(int)
    
    for route, dispatch_time in prev_routes:
        # Skip routes outside coordination window
        if current_time - dispatch_time > coordination_window:
            continue
            
        # Count usage of each edge in the route
        for i in range(len(route) - 1):
            edge = (route[i], route[i + 1])
            edge_usage[edge] += 1
    
    return edge_usage

def calculate_edge_cost(start, end, base_cost, capacity, edge_usage, 
                       capacity_penalty, is_priority_node):
    """Calculate actual edge cost considering all factors."""
    edge = (start, end)
    current_usage = edge_usage[edge]
    
    # Apply capacity penalty if exceeded
    if current_usage >= capacity:
        cost = base_cost * capacity_penalty
    else:
        cost = base_cost
    
    # Small bonus for priority nodes
    if is_priority_node:
        cost *= 0.95  # 5% reduction for priority nodes
    
    return cost