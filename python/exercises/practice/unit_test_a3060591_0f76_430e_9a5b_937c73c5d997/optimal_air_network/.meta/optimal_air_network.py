from math import radians, cos, sin, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def design_network(cities, airports, route_difficulty_factor):
    # If no airports available, network is disconnected.
    if not airports:
        return (0, float('inf'), [], [])
    
    # Select all available airport locations.
    selected_airport_indices = list(range(len(airports)))
    n_airports = len(airports)
    
    # Build a list of potential flight routes (edges) between every pair of airports.
    # Each edge: (cost_edge, airport1, airport2, distance)
    edges = []
    for i in range(n_airports):
        lat1, lon1, cost1, cap1 = airports[i]
        for j in range(i + 1, n_airports):
            lat2, lon2, cost2, cap2 = airports[j]
            d = haversine(lat1, lon1, lat2, lon2)
            cost_edge = d * route_difficulty_factor
            edges.append((cost_edge, i, j, d))
    edges.sort(key=lambda x: x[0])
    
    # Initialize Union-Find structure and degree counter for capacity tracking.
    parent = list(range(n_airports))
    rank = [0] * n_airports
    degree = [0] * n_airports

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return False
        if rank[rx] < rank[ry]:
            parent[rx] = ry
        elif rank[rx] > rank[ry]:
            parent[ry] = rx
        else:
            parent[ry] = rx
            rank[rx] += 1
        return True

    flight_routes = []
    mst_cost = 0

    # Build a spanning tree using a modified Kruskal algorithm ensuring capacity constraints.
    for cost_edge, i, j, distance in edges:
        if find(i) != find(j):
            if degree[i] < airports[i][3] and degree[j] < airports[j][3]:
                if union(i, j):
                    flight_routes.append((i, j))
                    mst_cost += cost_edge
                    degree[i] += 1
                    degree[j] += 1

    # Verify network connectivity among the selected airports.
    roots = set(find(i) for i in range(n_airports))
    if len(roots) > 1:
        max_travel_time = float('inf')
    else:
        # Construct a graph for the MST with travel times on edges.
        graph = {i: [] for i in range(n_airports)}
        for i, j in flight_routes:
            lat1, lon1, _, _ = airports[i]
            lat2, lon2, _, _ = airports[j]
            d = haversine(lat1, lon1, lat2, lon2)
            travel_time = d / 800.0
            graph[i].append((j, travel_time))
            graph[j].append((i, travel_time))
        
        # Compute the diameter (maximum travel time between any two nodes) of the MST.
        def dfs(node, parent_node, accumulated):
            farthest = (accumulated, node)
            for neighbor, t in graph[node]:
                if neighbor == parent_node:
                    continue
                candidate = dfs(neighbor, node, accumulated + t)
                if candidate[0] > farthest[0]:
                    farthest = candidate
            return farthest
        
        # Run two DFS to compute tree diameter.
        farthest_distance, far_node = dfs(0, -1, 0)
        diameter, _ = dfs(far_node, -1, 0)
        max_travel_time = diameter

    # Total cost includes the sum of the airport construction costs and the flight route costs.
    total_cost = sum(airport[2] for airport in airports) + mst_cost
    return (total_cost, max_travel_time, selected_airport_indices, flight_routes)

if __name__ == '__main__':
    # Example execution: Two cities example.
    cities = [(40.0, -70.0), (42.0, -71.0)]
    airports = [
        (40.0, -70.0, 150, 2),
        (42.0, -71.0, 200, 2)
    ]
    route_difficulty_factor = 1
    result = design_network(cities, airports, route_difficulty_factor)
    print(result)