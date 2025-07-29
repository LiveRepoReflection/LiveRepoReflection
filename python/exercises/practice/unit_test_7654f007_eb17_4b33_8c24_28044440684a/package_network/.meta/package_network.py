import heapq
from collections import defaultdict

def calculate_min_delivery_cost(N, edges, destination_cities):
    # Build adjacency list with calculated costs
    graph = defaultdict(list)
    for u, v, distance, base_cost, traffic_factor, fuel_price_factor in edges:
        cost = distance * base_cost * traffic_factor * fuel_price_factor
        graph[u].append((v, cost))
    
    # Precompute shortest paths from depot (0) to all nodes
    def dijkstra(start):
        distances = {node: float('inf') for node in range(N)}
        distances[start] = 0
        heap = [(0, start)]
        
        while heap:
            current_dist, u = heapq.heappop(heap)
            if current_dist > distances[u]:
                continue
            for v, cost in graph[u]:
                if distances[v] > distances[u] + cost:
                    distances[v] = distances[u] + cost
                    heapq.heappush(heap, (distances[v], v))
        return distances
    
    # Get shortest paths from depot to all nodes
    from_depot = dijkstra(0)
    
    # Get shortest paths from all nodes back to depot
    # Need to reverse the graph for return paths
    reversed_graph = defaultdict(list)
    for u in graph:
        for v, cost in graph[u]:
            reversed_graph[v].append((u, cost))
    
    def reversed_dijkstra(start):
        distances = {node: float('inf') for node in range(N)}
        distances[start] = 0
        heap = [(0, start)]
        
        while heap:
            current_dist, u = heapq.heappop(heap)
            if current_dist > distances[u]:
                continue
            for v, cost in reversed_graph[u]:
                if distances[v] > distances[u] + cost:
                    distances[v] = distances[u] + cost
                    heapq.heappush(heap, (distances[v], v))
        return distances
    
    to_depot = reversed_dijkstra(0)
    
    # Handle case where there are no destinations
    if not destination_cities:
        return 0.0
    
    # Now solve the TSP-like problem for the destinations
    # Since N can be up to 1000, we need an efficient approach
    # We'll use dynamic programming with bitmask for small k (<=15)
    # For larger k, we'll use approximation (minimum spanning tree approach)
    
    k = len(destination_cities)
    destinations = destination_cities
    
    if k <= 15:
        # DP approach for small number of destinations
        # dp[mask][u] = min cost to visit all cities in mask ending at u
        dp = [[float('inf')] * k for _ in range(1 << k)]
        
        # Initialize: starting from depot (0) to each destination
        for i in range(k):
            u = destinations[i]
            dp[1 << i][i] = from_depot[u]
        
        # Fill DP table
        for mask in range(1 << k):
            for last in range(k):
                if not (mask & (1 << last)):
                    continue
                current_cost = dp[mask][last]
                if current_cost == float('inf'):
                    continue
                for next_node in range(k):
                    if mask & (1 << next_node):
                        continue
                    u = destinations[last]
                    v = destinations[next_node]
                    # Find shortest path from u to v
                    # Since we don't have all-pairs shortest path, we'll use Dijkstra
                    # This makes the solution O(k * (E + V log V)) which is acceptable for k <= 15
                    temp_dist = dijkstra(u)
                    new_cost = current_cost + temp_dist[v]
                    new_mask = mask | (1 << next_node)
                    if new_cost < dp[new_mask][next_node]:
                        dp[new_mask][next_node] = new_cost
        
        # Find the minimal cost to visit all destinations and return to depot
        final_mask = (1 << k) - 1
        min_cost = float('inf')
        for last in range(k):
            u = destinations[last]
            total_cost = dp[final_mask][last] + to_depot[u]
            if total_cost < min_cost:
                min_cost = total_cost
    else:
        # Approximation for large k: Minimum spanning tree approach
        # This is a 2-approximation of the optimal solution
        # First compute all-pairs shortest paths between destinations
        all_pairs = {}
        for u in destinations:
            dists = dijkstra(u)
            for v in destinations:
                if u != v:
                    all_pairs[(u, v)] = dists[v]
        
        # Build complete graph between destinations with shortest paths
        edges_mst = []
        for i in range(len(destinations)):
            for j in range(i+1, len(destinations)):
                u = destinations[i]
                v = destinations[j]
                edges_mst.append((i, j, all_pairs[(u, v)]))
        
        # Krusky's algorithm for MST
        parent = [i for i in range(len(destinations))]
        
        def find(u):
            while parent[u] != u:
                parent[u] = parent[parent[u]]
                u = parent[u]
            return u
        
        edges_mst.sort(key=lambda x: x[2])
        mst_cost = 0
        mst_edges = 0
        for u, v, cost in edges_mst:
            root_u = find(u)
            root_v = find(v)
            if root_u != root_v:
                parent[root_u] = root_v
                mst_cost += cost
                mst_edges += 1
                if mst_edges == len(destinations) - 1:
                    break
        
        # The approximation is twice the MST cost plus depot connections
        # Find the closest destination to depot and back
        min_to_dest = min(from_depot[u] for u in destinations)
        min_from_dest = min(to_depot[u] for u in destinations)
        min_cost = 2 * mst_cost + min_to_dest + min_from_dest
    
    return round(min_cost, 2)