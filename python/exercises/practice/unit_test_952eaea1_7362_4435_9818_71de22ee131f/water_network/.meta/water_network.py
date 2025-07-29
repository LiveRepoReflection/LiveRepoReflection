from collections import defaultdict
import heapq

def min_cost_water_network(n: int, pipes: list) -> int:
    """
    Calculate the minimum cost to connect all buildings to the water network.
    
    Args:
        n: Number of buildings (excluding reservoir)
        pipes: List of tuples (building1, building2, cost)
    
    Returns:
        Minimum cost to connect all buildings, or -1 if impossible
    """
    if n == 0:
        return 0
    
    # Create adjacency list representation of the graph
    graph = defaultdict(list)
    for u, v, cost in pipes:
        graph[u].append((v, cost))
        graph[v].append((u, cost))
    
    # If any building has no connections, return -1
    if any(i not in graph for i in range(n + 1)):
        return -1
    
    # Use Prim's algorithm to find minimum spanning tree
    total_cost = 0
    visited = set()
    min_heap = [(0, 0)]  # (cost, vertex)
    
    while min_heap and len(visited) < n + 1:
        cost, vertex = heapq.heappop(min_heap)
        
        if vertex in visited:
            continue
            
        visited.add(vertex)
        total_cost += cost
        
        # Add all adjacent vertices to the min heap
        for next_vertex, edge_cost in graph[vertex]:
            if next_vertex not in visited:
                heapq.heappush(min_heap, (edge_cost, next_vertex))
    
    # Check if all buildings are connected
    if len(visited) < n + 1:
        return -1
        
    return total_cost

def optimize_pipes(pipes: list) -> list:
    """
    Helper function to remove duplicate pipes keeping only the minimum cost.
    
    Args:
        pipes: List of tuples (building1, building2, cost)
    
    Returns:
        Optimized list of pipes with duplicates removed
    """
    pipe_dict = {}
    for u, v, cost in pipes:
        key = tuple(sorted([u, v]))
        if key not in pipe_dict or cost < pipe_dict[key]:
            pipe_dict[key] = cost
    
    return [(u, v, cost) for (u, v), cost in pipe_dict.items()]