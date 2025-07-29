import heapq
import random

# Global dictionary to maintain occupancy for each edge.
occupancy_dict = {}

def update_occupancy(edge, delta):
    current = occupancy_dict.get(edge, 0)
    new_val = current + delta
    if new_val < 0:
        new_val = 0
    occupancy_dict[edge] = new_val

def find_least_risky_path(graph, origin, destination, congestion_factor, exploration_factor):
    # Modified Dijkstra's algorithm with exploration randomization.
    # Priority queue elements: (accumulated_cost, current_node, path_so_far)
    pq = []
    heapq.heappush(pq, (0, origin, [origin]))
    visited = {}

    while pq:
        cost, node, path = heapq.heappop(pq)
        if node == destination:
            return path
        if node in visited and visited[node] <= cost:
            continue
        visited[node] = cost
        if node not in graph:
            continue
        for neighbor, attributes in graph[node].items():
            base_risk = attributes.get('base_risk', 0)
            occ = occupancy_dict.get((node, neighbor), 0)
            edge_risk = base_risk + occ * congestion_factor
            # Incorporate random exploration factor: add a multiplicative noise factor.
            noise_multiplier = 1 + random.uniform(0, exploration_factor)
            effective_risk = edge_risk * noise_multiplier
            new_cost = cost + effective_risk
            new_path = path + [neighbor]
            heapq.heappush(pq, (new_cost, neighbor, new_path))
    return []