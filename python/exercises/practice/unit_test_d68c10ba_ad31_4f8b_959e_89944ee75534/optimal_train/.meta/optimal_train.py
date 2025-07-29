import math

def haversine_distance(lat1, lon1, lat2, lon2):
    # Radius of Earth in kilometers
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        xr = self.find(x)
        yr = self.find(y)
        if xr == yr:
            return False
        if self.rank[xr] < self.rank[yr]:
            self.parent[xr] = yr
        else:
            self.parent[yr] = xr
            if self.rank[xr] == self.rank[yr]:
                self.rank[xr] += 1
        return True

def tree_diameter(adj, n):
    # Performs two DFS traversals to find the diameter of the tree.
    # First DFS: from an arbitrary starting node (0) find the farthest node.
    def dfs(node, parent, dist):
        farthest_node = node
        max_dist = dist
        for nei, w in adj[node]:
            if nei == parent:
                continue
            candidate_node, candidate_dist = dfs(nei, node, dist + w)
            if candidate_dist > max_dist:
                max_dist = candidate_dist
                farthest_node = candidate_node
        return farthest_node, max_dist

    # If tree is empty, return 0
    if n == 0:
        return 0.0
    # Start DFS from node 0
    far_node, _ = dfs(0, -1, 0.0)
    # Second DFS from far_node to determine diameter
    _, diameter = dfs(far_node, -1, 0.0)
    return diameter

def find_optimal_train_network(cities, budget, cost_per_km, train_speed):
    """
    Computes an optimal train network connecting all cities within the given budget,
    minimizing the maximum travel time between any two cities.
    
    Returns a tuple:
       (railway_lines, max_travel_time, total_cost)
    where:
       railway_lines: list of tuples (city1, city2)
       max_travel_time: maximum travel time between any two cities (in minutes)
       total_cost: total cost of the constructed network
       
    If it's impossible to build a connected network within budget, returns
       ([], float('inf'), float('inf'))
    """
    n = len(cities)
    if n == 0:
        return ([], 0.0, 0.0)
    if n == 1:
        return ([], 0.0, 0.0)
    
    # Map city index to city name and coordinates
    city_names = [city[0] for city in cities]
    city_coords = [(city[1], city[2]) for city in cities]
    
    # Build all possible edges with computed distances using the Haversine formula.
    edges = []
    for i in range(n):
        lat1, lon1 = city_coords[i]
        for j in range(i+1, n):
            lat2, lon2 = city_coords[j]
            dist = haversine_distance(lat1, lon1, lat2, lon2)
            edges.append((dist, i, j))
    
    # Sort edges by distance
    edges.sort(key=lambda x: x[0])
    
    uf = UnionFind(n)
    mst_edges = []
    total_distance = 0.0  # Sum of distances for the MST
    for dist, i, j in edges:
        if uf.union(i, j):
            mst_edges.append((i, j, dist))
            total_distance += dist
            if len(mst_edges) == n - 1:
                break
    
    # If we didn't connect all cities, return failure approach.
    if len(mst_edges) != n - 1:
        return ([], float('inf'), float('inf'))
    
    total_cost = total_distance * cost_per_km
    if total_cost > budget:
        return ([], float('inf'), float('inf'))
    
    # Build adjacency list for the MST (tree)
    adj = {i: [] for i in range(n)}
    railway_lines = []
    for i, j, dist in mst_edges:
        adj[i].append((j, dist))
        adj[j].append((i, dist))
        railway_lines.append((city_names[i], city_names[j]))
    
    # Find the diameter (maximum travel distance) in kilometers
    diameter_distance = tree_diameter(adj, n)
    # Convert distance to travel time using train_speed (km/minute)
    max_travel_time = diameter_distance / train_speed
    
    return (railway_lines, max_travel_time, total_cost)