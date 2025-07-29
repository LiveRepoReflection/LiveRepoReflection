import heapq
from collections import defaultdict

def optimize_routes(n, edges, packets):
    # Build graph as an adjacency list.
    # Each entry: graph[u] = list of (v, base_cost, endpoints)
    # Using endpoints = (min(u,v), max(u,v)) for counting congestion.
    graph = defaultdict(list)
    for u, v, base_cost in edges:
        endpoints = (min(u, v), max(u, v))
        graph[u].append((v, base_cost, endpoints))
        graph[v].append((u, base_cost, endpoints))

    # Function to run dijkstra from source to destination using effective costs computed on the fly.
    def dijkstra(source, destination, counts):
        dist = [float('inf')] * n
        prev = [None] * n
        dist[source] = 0
        heap = [(0, source)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue
            if u == destination:
                break
            for v, base_cost, endpoints in graph[u]:
                # effective cost = base_cost * (1 + congestion/1000)
                congestion = counts[endpoints]
                effective_cost = base_cost * (1 + congestion / 1000)
                new_dist = dist[u] + effective_cost
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    prev[v] = u
                    heapq.heappush(heap, (new_dist, v))
        if dist[destination] == float('inf'):
            return None
        
        # Reconstruct path from source to destination.
        path = []
        current = destination
        while current is not None:
            path.append(current)
            current = prev[current]
        path.reverse()
        return path

    # Function to compute new routes for all packets given the current congestion counts.
    def compute_all_routes(counts):
        routes = []
        for source, destination, _ in packets:
            route = dijkstra(source, destination, counts)
            routes.append(route)
        return routes

    # Initial iteration: no congestion.
    counts = defaultdict(int)
    routes = compute_all_routes(counts)

    # Iterative improvement:
    max_iterations = 15
    for iteration in range(max_iterations):
        # Compute congestion counts based on current routes.
        new_counts = defaultdict(int)
        for route in routes:
            if route is None:
                continue
            for i in range(len(route) - 1):
                u, v = route[i], route[i+1]
                endpoints = (min(u, v), max(u, v))
                new_counts[endpoints] += 1

        # Compute new routes with updated congestion.
        new_routes = compute_all_routes(new_counts)
        # Check for convergence: if new_routes equals routes, break.
        if new_routes == routes:
            counts = new_counts
            routes = new_routes
            break
        counts = new_counts
        routes = new_routes

    return routes