def min_edge_weight_for_k_components(points, k):
    """
    Calculates the minimum total edge weight required to create exactly K connected components.
    
    Args:
        points: List of (x, y) tuples representing points on a 2D plane
        k: Number of desired connected components
        
    Returns:
        Float representing the minimum total edge weight
    """
    n = len(points)
    
    # Validate inputs
    if k < 1:
        raise ValueError("k must be at least 1")
    if k > n:
        raise ValueError("k cannot be greater than the number of points")
    
    # If k equals n, no edges needed
    if k == n:
        return 0.0
    
    # Calculate all edges and their weights
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            x1, y1 = points[i]
            x2, y2 = points[j]
            weight = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
            edges.append((i, j, weight))
    
    # Sort edges by weight (ascending)
    edges.sort(key=lambda e: e[2])
    
    # Apply Kruskal's algorithm to find the minimum spanning tree (MST)
    # with a specific number of components
    
    # Union-Find data structure for tracking connected components
    parent = list(range(n))
    rank = [0] * n
    
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        root_x = find(x)
        root_y = find(y)
        if root_x == root_y:
            return False
        
        if rank[root_x] < rank[root_y]:
            parent[root_x] = root_y
        else:
            parent[root_y] = root_x
            if rank[root_x] == rank[root_y]:
                rank[root_x] += 1
        return True
    
    # Initially, we have n components (each point is its own component)
    components = n
    
    # The MST will have exactly (n-1) edges for a fully connected graph
    # We need (n-k) edges to get exactly k components
    edges_needed = n - k
    total_weight = 0.0
    
    # Add edges until we have desired number of components
    for u, v, weight in edges:
        if components <= k:
            break
        
        if find(u) != find(v):  # If adding this edge doesn't create a cycle
            union(u, v)
            total_weight += weight
            components -= 1
    
    return total_weight