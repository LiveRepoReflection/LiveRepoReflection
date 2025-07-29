import heapq
import math

def minimum_corruption(edges, compromised, source, destination):
    # Build graph: u -> list of (v, latency)
    graph = {}
    for u, v, w in edges:
        if u not in graph:
            graph[u] = []
        graph[u].append((v, w))
    # Use a set for faster compromised lookup
    compromised_set = set(compromised)
    
    # Dijkstra-style search.
    # For every node, store the best cost to reach it with its corruption (if any) already applied.
    dist = {}
    dist[source] = 0
    heap = [(0, source)]
    
    while heap:
        cost, u = heapq.heappop(heap)
        # Skip if we already have a better cost for u
        if cost > dist.get(u, math.inf):
            continue
        if u == destination:
            return cost
        # If u has no outgoing edges, continue.
        if u not in graph:
            continue
        for v, w in graph[u]:
            # Determine candidate cost for reaching v.
            # For non-compromised node, simply add the latency.
            if v not in compromised_set:
                candidate = cost + w
            else:
                # For compromised nodes:
                # - If v has not yet been reached at all, we must pay the corruption cost on the arriving edge,
                #   so cost = current cost + (w for latency + w for corruption) = cost + 2*w.
                # - If v has already been reached (triggered) then we can use the same node again without paying extra,
                #   so cost = cost + w.
                if v in dist:
                    candidate = cost + w
                else:
                    candidate = cost + 2 * w
            
            if candidate < dist.get(v, math.inf):
                dist[v] = candidate
                heapq.heappush(heap, (candidate, v))
    return -1

if __name__ == '__main__':
    # Sample run (feel free to change parameters).
    edges = [
        (1, 2, 5),
        (1, 3, 4),
        (3, 4, 1),
        (2, 4, 3)
    ]
    compromised = [2]
    source = 1
    destination = 4
    print(minimum_corruption(edges, compromised, source, destination))