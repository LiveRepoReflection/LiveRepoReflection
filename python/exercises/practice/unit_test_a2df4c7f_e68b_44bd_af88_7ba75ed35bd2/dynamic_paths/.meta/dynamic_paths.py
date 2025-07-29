import heapq

def solve_dynamic_paths(N, roads, sources, updates):
    # Build graph as an adjacency list using dictionaries for quick updates.
    graph_dict = [{} for _ in range(N)]
    for u, v, w in roads:
        graph_dict[u][v] = w

    def multi_source_dijkstra(sources_list):
        if not sources_list:
            return [-1] * N
        
        dist = [float('inf')] * N
        heap = []
        for src in sources_list:
            if dist[src] > 0:
                dist[src] = 0
                heapq.heappush(heap, (0, src))
        
        while heap:
            d, u = heapq.heappop(heap)
            if d != dist[u]:
                continue
            for v, w in graph_dict[u].items():
                if dist[v] > d + w:
                    dist[v] = d + w
                    heapq.heappush(heap, (dist[v], v))
        
        # Convert unreachable nodes to -1.
        for i in range(N):
            if dist[i] == float('inf'):
                dist[i] = -1
        return dist

    current_sources = set(sources)
    results = []
    
    for update in updates:
        if update[0] == 0:
            # Road update: (0, u, v, w)
            _, u, v, w = update
            graph_dict[u][v] = w
        elif update[0] == 1:
            # Source update: (1, x, add)
            _, x, add = update
            if add:
                current_sources.add(x)
            else:
                if x in current_sources:
                    current_sources.remove(x)
        distances = multi_source_dijkstra(list(current_sources))
        results.append(sum(distances))
    
    return results

if __name__ == "__main__":
    # Sample test
    N = 4
    roads = [(0, 1, 2), (1, 2, 3)]
    sources = [0]
    updates = [
        (0, 2, 3, 1),
        (1, 1, True)
    ]
    print(solve_dynamic_paths(N, roads, sources, updates))