import heapq

def shortest_path(graph, sources, destinations, updates):
    # Apply updates: for each update, search for the edge in the adjacency list and update it.
    for u, v, new_weight in updates:
        if u in graph:
            # update only if the edge exists; if multiple, update first occurrence
            updated = False
            for i, (neighbor, weight) in enumerate(graph[u]):
                if neighbor == v:
                    graph[u][i] = (v, new_weight)
                    updated = True
                    break
            # Optionally, if edge not exists, add it.
            if not updated:
                graph[u].append((v, new_weight))
        else:
            # if the node u is not in graph, add it with this edge
            graph[u] = [(v, new_weight)]
    
    # Set of destination nodes for quick lookup
    dest_set = set(destinations)
    
    # Multi-source dijkstra initialization
    heap = []
    dist = {}
    # Initialize all source distances to zero
    for src in sources:
        heapq.heappush(heap, (0, src))
        if src not in dist or 0 < dist[src]:
            dist[src] = 0

    # Dijkstra's algorithm
    while heap:
        current_dist, node = heapq.heappop(heap)
        if current_dist > dist.get(node, float('inf')):
            continue
        
        # If the current node is a destination return the distance immediately.
        if node in dest_set:
            return current_dist
        
        # Traverse all neighbors
        for neighbor, weight in graph.get(node, []):
            new_dist = current_dist + weight
            if new_dist < dist.get(neighbor, float('inf')):
                dist[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))
                
    # If none of the destinations were reached, return -1
    return -1

if __name__ == '__main__':
    # Example usage:
    graph_example = {
        1: [(2, 2), (3, 5)],
        2: [(4, 1)],
        3: [(4, 3)],
        4: []
    }
    sources_example = [1, 3]
    destinations_example = [4]
    updates_example = []
    print(shortest_path(graph_example, sources_example, destinations_example, updates_example))