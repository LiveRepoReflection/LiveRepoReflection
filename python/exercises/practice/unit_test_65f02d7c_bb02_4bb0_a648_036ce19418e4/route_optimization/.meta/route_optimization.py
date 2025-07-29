import heapq
from itertools import combinations
from collections import defaultdict

def optimize_route(graph, start, destinations, time_window, package_values):
    if not destinations:
        return [start]
    
    # Precompute all pairs shortest paths using Dijkstra's algorithm
    all_nodes = set(graph.keys()).union(set().union(*[set(graph[k]) for k in graph]))
    shortest_paths = {}
    
    for node in all_nodes:
        shortest_paths[node] = dijkstra(graph, node)
    
    # Check if all destinations are reachable from start
    for dest in destinations:
        if dest not in shortest_paths[start] or shortest_paths[start][dest] == float('inf'):
            return []
    
    # Generate all possible orders to visit destinations
    max_value = -1
    best_route = []
    
    for r in range(1, len(destinations)+1):
        for subset in combinations(destinations, r):
            for permutation in permutations(subset):
                current_route = [start] + list(permutation) + [start]
                total_time = 0
                total_value = 0
                
                # Calculate total time and value
                valid = True
                for i in range(len(current_route)-1):
                    u = current_route[i]
                    v = current_route[i+1]
                    if v not in shortest_paths[u]:
                        valid = False
                        break
                    total_time += shortest_paths[u][v]
                
                if not valid or total_time > time_window:
                    continue
                
                total_value = sum(package_values[d] for d in permutation)
                
                if total_value > max_value or (total_value == max_value and total_time < best_route[1]):
                    max_value = total_value
                    best_route = (current_route, total_time)
    
    return best_route[0] if max_value != -1 else []

def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    heap = [(0, start)]
    
    while heap:
        current_dist, current_node = heapq.heappop(heap)
        
        if current_dist > distances[current_node]:
            continue
            
        for neighbor, weight in graph.get(current_node, []):
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(heap, (distance, neighbor))
    
    return distances

def permutations(iterable):
    # Non-recursive permutation generator
    pool = tuple(iterable)
    n = len(pool)
    indices = list(range(n))
    cycles = list(range(n, 0, -1))
    yield tuple(pool[i] for i in indices[:n])
    
    while n:
        for i in reversed(range(n)):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i+1:] + indices[i:i+1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                yield tuple(pool[i] for i in indices[:n])
                break
        else:
            return