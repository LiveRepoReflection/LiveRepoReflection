import itertools
import heapq

def min_links_removal(N, D, edges):
    # If there are no edges, every node is isolated and diameter 0.
    if not edges:
        return 0

    m = len(edges)
    edge_indices = list(range(m))
    
    # Try removals in increasing count.
    for k in range(0, m + 1):
        # Generate all combinations of k edges to remove.
        for removal in itertools.combinations(edge_indices, k):
            removed = set(removal)
            graph = build_graph(N, edges, removed)
            if all_components_within_diameter(graph, D, N):
                return k
    return -1

def build_graph(N, edges, removed):
    graph = {i: [] for i in range(N)}
    for idx, (u, v, latency) in enumerate(edges):
        if idx not in removed:
            graph[u].append((v, latency))
            graph[v].append((u, latency))
    return graph

def all_components_within_diameter(graph, D, N):
    visited = [False] * N
    for i in range(N):
        if not visited[i]:
            component = []
            stack = [i]
            while stack:
                node = stack.pop()
                if visited[node]:
                    continue
                visited[node] = True
                component.append(node)
                for neigh, _ in graph[node]:
                    if not visited[neigh]:
                        stack.append(neigh)
            if len(component) > 1:
                comp_diam = compute_component_diameter(component, graph)
                if comp_diam > D:
                    return False
    return True

def compute_component_diameter(component, graph):
    # For a given connected component (list of nodes), compute the diameter.
    # We use Dijkstra's algorithm from each node in the component.
    diam = 0
    for node in component:
        farthest = dijkstra_max_distance(node, component, graph)
        diam = max(diam, farthest)
        # Early stopping if already exceeds D.
        if diam > 1000000000:  # a safe upper bound
            return diam
    return diam

def dijkstra_max_distance(start, component, graph):
    distances = {node: float('inf') for node in component}
    distances[start] = 0
    heap = [(0, start)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > distances[node]:
            continue
        for neigh, weight in graph[node]:
            if neigh in distances:
                new_dist = d + weight
                if new_dist < distances[neigh]:
                    distances[neigh] = new_dist
                    heapq.heappush(heap, (new_dist, neigh))
    return max(distances[node] for node in component)