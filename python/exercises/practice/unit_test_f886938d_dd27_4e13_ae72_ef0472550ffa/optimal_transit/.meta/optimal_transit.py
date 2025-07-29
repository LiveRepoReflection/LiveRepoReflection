import heapq

def find_optimal_route(edges, start_node, end_node, num_passengers):
    # Build graph: for each node, list of (neighbor, cost, capacity)
    graph = {}
    for u, v, cost, capacity in edges:
        if u not in graph:
            graph[u] = []
        graph[u].append((v, cost, capacity))
    
    # The state for each node: (max_utilization, total_cost)
    # For start_node, max utilization is 0 and cost is 0.
    # Use dictionary to store best state for a node.
    best = {}
    best[start_node] = (0, 0)
    # To reconstruct the path, store predecessor.
    predecessor = {}
    predecessor[start_node] = None

    # Priority queue: (max_util, total_cost, node)
    heap = [(0, 0, start_node)]
    
    while heap:
        current_max, current_cost, node = heapq.heappop(heap)
        
        # If this state is not up-to-date, skip it.
        if best.get(node, (float('inf'), float('inf'))) != (current_max, current_cost):
            continue
        
        if node == end_node:
            # Reconstruct path from start_node to end_node.
            return _reconstruct_path(predecessor, end_node)
        
        # Explore neighbors if node has outgoing edges.
        if node not in graph:
            continue
        for neighbor, edge_cost, capacity in graph[node]:
            if capacity < num_passengers:
                # This edge cannot accommodate num_passengers.
                continue
            # Calculate utilization for this edge.
            edge_util = num_passengers / capacity
            new_max = max(current_max, edge_util)
            new_cost = current_cost + edge_cost
            # Compare lexicographically: (new_max, new_cost)
            if neighbor not in best or (new_max, new_cost) < best[neighbor]:
                best[neighbor] = (new_max, new_cost)
                predecessor[neighbor] = node
                heapq.heappush(heap, (new_max, new_cost, neighbor))
                
    # If we exit the loop without finding a valid path.
    return []

def _reconstruct_path(predecessor, end_node):
    path = []
    current = end_node
    while current is not None:
        path.append(current)
        current = predecessor.get(current)
    path.reverse()
    return path