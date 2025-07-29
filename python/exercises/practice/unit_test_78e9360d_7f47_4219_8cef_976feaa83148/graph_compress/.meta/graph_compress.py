import heapq

def compress_graph(edges, important_nodes):
    # Build an adjacency list from the edge list.
    graph = {}
    for u, v, w in edges:
        if u not in graph:
            graph[u] = []
        graph[u].append((v, w))
    # Initialize a set to store edges of the compressed graph.
    compressed_edges_set = set()
    # For each important node as source, run Dijkstra to get shortest paths to all nodes.
    for source in important_nodes:
        distances = {}
        prev = {}
        heap = [(0, source, None)]  # (distance, current_node, (parent, weight))
        while heap:
            cur_dist, u, pre_info = heapq.heappop(heap)
            if u in distances:
                continue
            distances[u] = cur_dist
            if pre_info is not None:
                prev[u] = pre_info
            for v, weight in graph.get(u, []):
                if v not in distances:
                    heapq.heappush(heap, (cur_dist + weight, v, (u, weight)))
        # For every other important node reachable from this source, reconstruct the path.
        for target in important_nodes:
            if source == target:
                continue
            if target not in distances:
                continue  # No path from source to target.
            # Reconstruct path from source to target.
            path_edges = []
            cur = target
            while cur != source:
                parent, weight = prev[cur]
                path_edges.append((parent, cur, weight))
                cur = parent
            # Add path edges to the compressed graph.
            for edge in path_edges:
                compressed_edges_set.add(edge)
    # Convert the set into a list and return.
    compressed_edges = list(compressed_edges_set)
    return compressed_edges