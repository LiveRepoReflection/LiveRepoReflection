import heapq
import math

def optimal_evacuation(graph, population, evacuation_centers):
    # Initialize distances to infinity for all nodes in the graph.
    distances = {node: math.inf for node in graph}
    min_heap = []
    
    # Multi-source initialization: set distance for evacuation centers to 0.
    for center in evacuation_centers:
        if center in graph:
            distances[center] = 0
            heapq.heappush(min_heap, (0, center))
    
    # Execute Dijkstra's algorithm from all evacuation centers simultaneously.
    while min_heap:
        curr_distance, node = heapq.heappop(min_heap)
        if curr_distance > distances[node]:
            continue
        for neighbor, weight in graph[node]:
            new_distance = curr_distance + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                heapq.heappush(min_heap, (new_distance, neighbor))
    
    # Determine the maximum evacuation time among all populated nodes.
    max_time = 0
    for node, pop in population.items():
        if pop > 0:
            if node not in distances or distances[node] == math.inf:
                return -1
            max_time = max(max_time, distances[node])
    return max_time